import streamlit as st
from sqlalchemy import create_engine, text

# ── Conexão ────────────────────────────────────────────────────────────────────
DATABASE_URL = "postgresql://neondb_owner:npg_0UWcJ7XLIotb@ep-holy-grass-amcai7dk-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(DATABASE_URL)

def query(sql, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        conn.commit()
        return result.fetchall()

def query_df(sql, params=None):
    import pandas as pd
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})

# ── Config ─────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="European Soccer DB", page_icon="⚽", layout="wide")
st.title("⚽ European Soccer Database")

pagina = st.sidebar.radio("Navegar", [
    "🏠 Home", "👤 Players", "🏟️ Teams",
    "🏆 Leagues", "⚽ Matches", "📊 Análises",
])

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "🏠 Home":
    st.subheader("Resumo do banco de dados")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Players",  query("SELECT COUNT(*) FROM player")[0][0])
    c2.metric("Teams",    query("SELECT COUNT(*) FROM team")[0][0])
    c3.metric("Matches",  query("SELECT COUNT(*) FROM match")[0][0])
    c4.metric("Leagues",  query("SELECT COUNT(*) FROM league")[0][0])
    st.divider()
    st.subheader("🏆 Ligas disponíveis")
    rows = query("""
        SELECT l.name, c.name, COUNT(m.id) as jogos
        FROM league l
        JOIN country c ON l.country_id = c.id
        LEFT JOIN match m ON m.league_id = l.id
        GROUP BY l.name, c.name ORDER BY jogos DESC
    """)
    st.dataframe([{"Liga": r[0], "País": r[1], "Total de jogos": r[2]} for r in rows],
                 use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PLAYERS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "👤 Players":
    st.subheader("👤 Players")
    aba = st.tabs(["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Deletar"])

    with aba[0]:
        busca = st.text_input("Buscar por nome")
        rows = query(
            "SELECT id, player_name, birthday, height, weight FROM player WHERE player_name ILIKE :q ORDER BY player_name LIMIT 50",
            {"q": f"%{busca}%"}
        ) if busca else query(
            "SELECT id, player_name, birthday, height, weight FROM player ORDER BY id DESC LIMIT 50"
        )
        st.dataframe([{"ID": r[0], "Nome": r[1], "Nascimento": r[2],
                       "Altura (cm)": r[3], "Peso (lbs)": r[4]} for r in rows],
                     use_container_width=True)

    with aba[1]:
        with st.form("form_insert_player"):
            nome     = st.text_input("Nome do jogador")
            birthday = st.date_input("Data de nascimento")
            height   = st.number_input("Altura (cm)", min_value=0)
            weight   = st.number_input("Peso (lbs)", min_value=0)
            if st.form_submit_button("💾 Salvar"):
                query("INSERT INTO player (player_name, birthday, height, weight) VALUES (:n,:b,:h,:w)",
                      {"n": nome, "b": str(birthday), "h": int(height), "w": int(weight)})
                st.success(f"Jogador **{nome}** inserido!")

    with aba[2]:
        pid = st.number_input("ID do jogador a editar", min_value=1, step=1)
        if st.button("Buscar jogador"):
            r = query("SELECT player_name, birthday, height, weight FROM player WHERE id=:id", {"id": pid})
            st.session_state["edit_player"] = r[0] if r else None
            if not r: st.error("Jogador não encontrado.")
        if st.session_state.get("edit_player"):
            r = st.session_state["edit_player"]
            with st.form("form_edit_player"):
                nome   = st.text_input("Nome", value=r[0])
                height = st.number_input("Altura", value=int(r[2]) if r[2] else 0)
                weight = st.number_input("Peso",   value=int(r[3]) if r[3] else 0)
                if st.form_submit_button("✏️ Atualizar"):
                    query("UPDATE player SET player_name=:n, height=:h, weight=:w WHERE id=:id",
                          {"n": nome, "h": int(height), "w": int(weight), "id": pid})
                    st.success("Jogador atualizado!")
                    del st.session_state["edit_player"]

    with aba[3]:
        pid_del = st.number_input("ID do jogador a deletar", min_value=1, step=1, key="del_player")
        r = query("SELECT player_name FROM player WHERE id=:id", {"id": pid_del})
        if r:
            st.warning(f"Deletar: **{r[0][0]}**")
            if st.button("🗑️ Confirmar exclusão", key="btn_del_player"):
                query("DELETE FROM player WHERE id=:id", {"id": pid_del})
                st.success("Jogador deletado!")
        else:
            st.info("Digite um ID válido.")

# ══════════════════════════════════════════════════════════════════════════════
# TEAMS
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🏟️ Teams":
    st.subheader("🏟️ Teams")
    aba = st.tabs(["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Deletar"])

    with aba[0]:
        busca = st.text_input("Buscar por nome")
        rows = query(
            "SELECT id, team_long_name, team_short_name FROM team WHERE team_long_name ILIKE :q ORDER BY team_long_name LIMIT 50",
            {"q": f"%{busca}%"}
        ) if busca else query(
            "SELECT id, team_long_name, team_short_name FROM team ORDER BY team_long_name LIMIT 50"
        )
        st.dataframe([{"ID": r[0], "Nome": r[1], "Abrev.": r[2]} for r in rows],
                     use_container_width=True)

    with aba[1]:
        with st.form("form_insert_team"):
            nome_longo = st.text_input("Nome completo")
            nome_curto = st.text_input("Abreviação (ex: FCB)")
            if st.form_submit_button("💾 Salvar"):
                query("INSERT INTO team (team_long_name, team_short_name) VALUES (:n,:s)",
                      {"n": nome_longo, "s": nome_curto})
                st.success(f"Time **{nome_longo}** inserido!")

    with aba[2]:
        tid = st.number_input("ID do time a editar", min_value=1, step=1)
        if st.button("Buscar time"):
            r = query("SELECT team_long_name, team_short_name FROM team WHERE id=:id", {"id": tid})
            st.session_state["edit_team"] = r[0] if r else None
            if not r: st.error("Time não encontrado.")
        if st.session_state.get("edit_team"):
            r = st.session_state["edit_team"]
            with st.form("form_edit_team"):
                nome_longo = st.text_input("Nome completo", value=r[0])
                nome_curto = st.text_input("Abreviação",    value=r[1])
                if st.form_submit_button("✏️ Atualizar"):
                    query("UPDATE team SET team_long_name=:n, team_short_name=:s WHERE id=:id",
                          {"n": nome_longo, "s": nome_curto, "id": tid})
                    st.success("Time atualizado!")
                    del st.session_state["edit_team"]

    with aba[3]:
        tid_del = st.number_input("ID do time a deletar", min_value=1, step=1, key="del_team")
        r = query("SELECT team_long_name FROM team WHERE id=:id", {"id": tid_del})
        if r:
            st.warning(f"Deletar: **{r[0][0]}**")
            if st.button("🗑️ Confirmar exclusão", key="btn_del_team"):
                query("DELETE FROM team WHERE id=:id", {"id": tid_del})
                st.success("Time deletado!")
        else:
            st.info("Digite um ID válido.")

# ══════════════════════════════════════════════════════════════════════════════
# LEAGUES
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "🏆 Leagues":
    st.subheader("🏆 Leagues")
    aba = st.tabs(["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Deletar"])

    with aba[0]:
        rows = query("""
            SELECT l.id, l.name, c.name FROM league l
            JOIN country c ON l.country_id = c.id ORDER BY l.name
        """)
        st.dataframe([{"ID": r[0], "Liga": r[1], "País": r[2]} for r in rows],
                     use_container_width=True)

    with aba[1]:
        countries   = query("SELECT id, name FROM country ORDER BY name")
        country_map = {c[1]: c[0] for c in countries}
        with st.form("form_insert_league"):
            nome    = st.text_input("Nome da liga")
            country = st.selectbox("País", list(country_map.keys()))
            if st.form_submit_button("💾 Salvar"):
                query("INSERT INTO league (name, country_id) VALUES (:n,:c)",
                      {"n": nome, "c": country_map[country]})
                st.success(f"Liga **{nome}** inserida!")

    with aba[2]:
        lid = st.number_input("ID da liga a editar", min_value=1, step=1)
        if st.button("Buscar liga"):
            r = query("SELECT name, country_id FROM league WHERE id=:id", {"id": lid})
            st.session_state["edit_league"] = r[0] if r else None
            if not r: st.error("Liga não encontrada.")
        if st.session_state.get("edit_league"):
            r        = st.session_state["edit_league"]
            countries   = query("SELECT id, name FROM country ORDER BY name")
            country_map = {c[1]: c[0] for c in countries}
            country_rev = {c[0]: c[1] for c in countries}
            current     = country_rev.get(r[1], list(country_map.keys())[0])
            with st.form("form_edit_league"):
                nome    = st.text_input("Nome", value=r[0])
                country = st.selectbox("País", list(country_map.keys()),
                                       index=list(country_map.keys()).index(current))
                if st.form_submit_button("✏️ Atualizar"):
                    query("UPDATE league SET name=:n, country_id=:c WHERE id=:id",
                          {"n": nome, "c": country_map[country], "id": lid})
                    st.success("Liga atualizada!")
                    del st.session_state["edit_league"]

    with aba[3]:
        lid_del = st.number_input("ID da liga a deletar", min_value=1, step=1, key="del_league")
        r = query("SELECT name FROM league WHERE id=:id", {"id": lid_del})
        if r:
            st.warning(f"Deletar: **{r[0][0]}**")
            if st.button("🗑️ Confirmar exclusão", key="btn_del_league"):
                query("DELETE FROM league WHERE id=:id", {"id": lid_del})
                st.success("Liga deletada!")
        else:
            st.info("Digite um ID válido.")

# ══════════════════════════════════════════════════════════════════════════════
# MATCHES  (JOIN corrigido: team_api_id::bigint)
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "⚽ Matches":
    st.subheader("⚽ Matches")
    aba = st.tabs(["📋 Listar", "➕ Inserir", "✏️ Editar", "🗑️ Deletar"])

    with aba[0]:
        c1, c2   = st.columns(2)
        seasons  = [r[0] for r in query("SELECT DISTINCT season FROM match ORDER BY season DESC")]
        season   = c1.selectbox("Temporada", seasons)
        leagues  = query("SELECT id, name FROM league ORDER BY name")
        league_map = {"Todas": None} | {l[1]: l[0] for l in leagues}
        liga_sel = c2.selectbox("Liga", list(league_map.keys()))

        sql = """
            SELECT m.id, m.date, m.season, l.name,
                   ht.team_long_name, at.team_long_name,
                   m.home_team_goal, m.away_team_goal
            FROM match m
            JOIN team ht ON m.home_team_api_id = ht.team_api_id::bigint
            JOIN team at ON m.away_team_api_id = at.team_api_id::bigint
            JOIN league l ON m.league_id = l.id
            WHERE m.season = :s
        """
        params = {"s": season}
        if league_map[liga_sel]:
            sql += " AND m.league_id = :l"
            params["l"] = league_map[liga_sel]
        sql += " ORDER BY m.date DESC LIMIT 100"

        rows = query(sql, params)
        st.dataframe(
            [{"ID": r[0], "Data": r[1], "Temporada": r[2], "Liga": r[3],
              "Mandante": r[4], "Visitante": r[5],
              "Gols M": r[6], "Gols V": r[7]} for r in rows],
            use_container_width=True
        )
        st.caption(f"{len(rows)} partidas encontradas")

    with aba[1]:
        teams      = query("SELECT team_api_id, team_long_name FROM team ORDER BY team_long_name")
        leagues    = query("SELECT id, name FROM league ORDER BY name")
        team_map   = {t[1]: t[0] for t in teams}
        league_map = {l[1]: l[0] for l in leagues}
        with st.form("form_insert_match"):
            data       = st.date_input("Data da partida")
            season_new = st.text_input("Temporada", value="2015/2016")
            liga       = st.selectbox("Liga", list(league_map.keys()))
            mandante   = st.selectbox("Time Mandante",  list(team_map.keys()))
            visitante  = st.selectbox("Time Visitante", list(team_map.keys()))
            c1, c2     = st.columns(2)
            gols_m     = c1.number_input("Gols Mandante",  min_value=0)
            gols_v     = c2.number_input("Gols Visitante", min_value=0)
            if st.form_submit_button("💾 Salvar"):
                query("""INSERT INTO match (date, season, league_id, home_team_api_id,
                         away_team_api_id, home_team_goal, away_team_goal)
                         VALUES (:d,:s,:l,:h,:a,:hg,:ag)""",
                      {"d": str(data), "s": season_new, "l": league_map[liga],
                       "h": team_map[mandante], "a": team_map[visitante],
                       "hg": int(gols_m), "ag": int(gols_v)})
                st.success("Partida inserida!")

    with aba[2]:
        mid = st.number_input("ID da partida a editar", min_value=1, step=1)
        if st.button("Buscar partida"):
            r = query("SELECT date, season, home_team_goal, away_team_goal FROM match WHERE id=:id", {"id": mid})
            st.session_state["edit_match"] = r[0] if r else None
            if not r: st.error("Partida não encontrada.")
        if st.session_state.get("edit_match"):
            r = st.session_state["edit_match"]
            with st.form("form_edit_match"):
                season_e = st.text_input("Temporada", value=r[1])
                c1, c2   = st.columns(2)
                gols_m   = c1.number_input("Gols Mandante",  value=int(r[2]), min_value=0)
                gols_v   = c2.number_input("Gols Visitante", value=int(r[3]), min_value=0)
                if st.form_submit_button("✏️ Atualizar"):
                    query("UPDATE match SET season=:s, home_team_goal=:hg, away_team_goal=:ag WHERE id=:id",
                          {"s": season_e, "hg": int(gols_m), "ag": int(gols_v), "id": mid})
                    st.success("Partida atualizada!")
                    del st.session_state["edit_match"]

    with aba[3]:
        mid_del = st.number_input("ID da partida a deletar", min_value=1, step=1, key="del_match")
        r = query("""
            SELECT ht.team_long_name, at.team_long_name, m.home_team_goal, m.away_team_goal
            FROM match m
            JOIN team ht ON m.home_team_api_id = ht.team_api_id::bigint
            JOIN team at ON m.away_team_api_id = at.team_api_id::bigint
            WHERE m.id=:id""", {"id": mid_del})
        if r:
            st.warning(f"Deletar: **{r[0][0]} {r[0][2]} x {r[0][3]} {r[0][1]}**")
            if st.button("🗑️ Confirmar exclusão", key="btn_del_match"):
                query("DELETE FROM match WHERE id=:id", {"id": mid_del})
                st.success("Partida deletada!")
        else:
            st.info("Digite um ID válido.")

# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISES
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📊 Análises":
    st.subheader("📊 Análises")

    analise = st.selectbox("Escolha a análise", [
        "🥅 Gols marcados por time",
        "⚡ Top jogadores por atributo",
        "🏆 Classificação de times (vitórias/derrotas)",
        "📅 Partidas de um time específico",
        "🔥 Jogos com mais gols",
        "📈 Média de gols por temporada e liga",
        "👟 Pé preferido dos jogadores",
        "🆚 Confronto direto entre dois times",
        "📊 Evolução de atributo de um jogador",
    ])

    seasons    = [r[0] for r in query("SELECT DISTINCT season FROM match ORDER BY season DESC")]
    leagues    = query("SELECT id, name FROM league ORDER BY name")
    league_map = {l[1]: l[0] for l in leagues}

    # ── Artilheiros ────────────────────────────────────────────────────────────
    if analise == "🥅 Gols marcados por time":
        st.info("Gols somados por time como mandante e visitante.")
        c1, c2 = st.columns(2)
        season = c1.selectbox("Temporada", seasons)
        liga   = c2.selectbox("Liga", list(league_map.keys()))
        top_n  = st.slider("Top N times", 5, 20, 10)
        rows   = query_df("""
            SELECT t.team_long_name as "Time",
                   SUM(CASE WHEN m.home_team_api_id = t.team_api_id::bigint
                            THEN m.home_team_goal ELSE m.away_team_goal END) as "Gols"
            FROM match m
            JOIN team t ON m.home_team_api_id = t.team_api_id::bigint
                        OR m.away_team_api_id = t.team_api_id::bigint
            WHERE m.season = :s AND m.league_id = :l
            GROUP BY t.team_long_name
            ORDER BY "Gols" DESC
            LIMIT :n
        """, {"s": season, "l": league_map[liga], "n": top_n})
        st.dataframe(rows, use_container_width=True)
        st.bar_chart(rows.set_index("Time")["Gols"])

    # ── Top por atributo ───────────────────────────────────────────────────────
    elif analise == "⚡ Top jogadores por atributo":
        atributos = ["overall_rating", "potential", "crossing", "finishing",
                     "dribbling", "sprint_speed", "stamina", "strength",
                     "volleys", "shot_power", "long_shots", "agility",
                     "reactions", "balance", "jumping", "heading_accuracy"]
        c1, c2 = st.columns(2)
        attr   = c1.selectbox("Atributo", atributos)
        top_n  = c2.slider("Top N", 5, 30, 10)
        rows   = query_df(f"""
            SELECT p.player_name as "Jogador", MAX(pa.{attr}) as "Valor"
            FROM player_attributes pa
            JOIN player p ON pa.player_api_id = p.player_api_id
            WHERE pa.{attr} IS NOT NULL
            GROUP BY p.player_name
            ORDER BY "Valor" DESC
            LIMIT :n
        """, {"n": top_n})
        st.dataframe(rows, use_container_width=True)
        st.bar_chart(rows.set_index("Jogador")["Valor"])

    # ── Classificação ──────────────────────────────────────────────────────────
    elif analise == "🏆 Classificação de times (vitórias/derrotas)":
        c1, c2 = st.columns(2)
        season = c1.selectbox("Temporada", seasons)
        liga   = c2.selectbox("Liga", list(league_map.keys()))
        rows   = query_df("""
            SELECT t.team_long_name as "Time",
                COUNT(*) as "Jogos",
                SUM(CASE
                    WHEN m.home_team_api_id = t.team_api_id::bigint AND m.home_team_goal > m.away_team_goal THEN 1
                    WHEN m.away_team_api_id = t.team_api_id::bigint AND m.away_team_goal > m.home_team_goal THEN 1
                    ELSE 0 END) as "Vitórias",
                SUM(CASE WHEN m.home_team_goal = m.away_team_goal THEN 1 ELSE 0 END) as "Empates",
                SUM(CASE
                    WHEN m.home_team_api_id = t.team_api_id::bigint AND m.home_team_goal < m.away_team_goal THEN 1
                    WHEN m.away_team_api_id = t.team_api_id::bigint AND m.away_team_goal < m.home_team_goal THEN 1
                    ELSE 0 END) as "Derrotas",
                SUM(CASE WHEN m.home_team_api_id = t.team_api_id::bigint THEN m.home_team_goal
                         ELSE m.away_team_goal END) as "Gols Pró",
                SUM(CASE WHEN m.home_team_api_id = t.team_api_id::bigint THEN m.away_team_goal
                         ELSE m.home_team_goal END) as "Gols Contra"
            FROM match m
            JOIN team t ON m.home_team_api_id = t.team_api_id::bigint
                        OR m.away_team_api_id = t.team_api_id::bigint
            WHERE m.season = :s AND m.league_id = :l
            GROUP BY t.team_long_name
        """, {"s": season, "l": league_map[liga]})
        rows["Pontos"] = rows["Vitórias"] * 3 + rows["Empates"]
        rows["Saldo"]  = rows["Gols Pró"] - rows["Gols Contra"]
        rows = rows.sort_values("Pontos", ascending=False).reset_index(drop=True)
        rows.index += 1
        st.dataframe(rows[["Time","Jogos","Vitórias","Empates","Derrotas",
                            "Gols Pró","Gols Contra","Saldo","Pontos"]],
                     use_container_width=True)

    # ── Partidas de um time ────────────────────────────────────────────────────
    elif analise == "📅 Partidas de um time específico":
        teams    = [r[0] for r in query("SELECT team_long_name FROM team ORDER BY team_long_name")]
        c1, c2   = st.columns(2)
        time_sel = c1.selectbox("Time", teams)
        season   = c2.selectbox("Temporada", seasons)
        rows     = query_df("""
            SELECT m.date as "Data", ht.team_long_name as "Mandante",
                   m.home_team_goal as "Gols M", m.away_team_goal as "Gols V",
                   at.team_long_name as "Visitante", l.name as "Liga"
            FROM match m
            JOIN team ht ON m.home_team_api_id = ht.team_api_id::bigint
            JOIN team at ON m.away_team_api_id = at.team_api_id::bigint
            JOIN league l ON m.league_id = l.id
            WHERE (ht.team_long_name = :t OR at.team_long_name = :t) AND m.season = :s
            ORDER BY m.date
        """, {"t": time_sel, "s": season})
        if not rows.empty:
            v = len(rows[((rows["Mandante"]==time_sel) & (rows["Gols M"] > rows["Gols V"])) |
                         ((rows["Visitante"]==time_sel) & (rows["Gols V"] > rows["Gols M"]))])
            e = len(rows[rows["Gols M"] == rows["Gols V"]])
            d = len(rows) - v - e
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Jogos", len(rows))
            c2.metric("Vitórias", v)
            c3.metric("Empates", e)
            c4.metric("Derrotas", d)
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("Nenhuma partida encontrada.")

    # ── Jogos com mais gols ────────────────────────────────────────────────────
    elif analise == "🔥 Jogos com mais gols":
        season = st.selectbox("Temporada", seasons)
        top_n  = st.slider("Top N jogos", 5, 30, 10)
        rows   = query_df("""
            SELECT m.date as "Data", l.name as "Liga",
                   ht.team_long_name as "Mandante",
                   m.home_team_goal as "Gols M",
                   m.away_team_goal as "Gols V",
                   at.team_long_name as "Visitante",
                   (m.home_team_goal + m.away_team_goal) as "Total Gols"
            FROM match m
            JOIN team ht ON m.home_team_api_id = ht.team_api_id::bigint
            JOIN team at ON m.away_team_api_id = at.team_api_id::bigint
            JOIN league l ON m.league_id = l.id
            WHERE m.season = :s
            ORDER BY "Total Gols" DESC
            LIMIT :n
        """, {"s": season, "n": top_n})
        st.dataframe(rows, use_container_width=True)

    # ── Média de gols ──────────────────────────────────────────────────────────
    elif analise == "📈 Média de gols por temporada e liga":
        liga = st.selectbox("Liga", list(league_map.keys()))
        rows = query_df("""
            SELECT season as "Temporada",
                   ROUND(AVG(home_team_goal + away_team_goal)::numeric, 2) as "Média de Gols",
                   COUNT(*) as "Jogos"
            FROM match WHERE league_id = :l
            GROUP BY season ORDER BY season
        """, {"l": league_map[liga]})
        st.dataframe(rows, use_container_width=True)
        st.line_chart(rows.set_index("Temporada")["Média de Gols"])

    # ── Pé preferido ──────────────────────────────────────────────────────────
    elif analise == "👟 Pé preferido dos jogadores":
        rows = query_df("""
            SELECT preferred_foot as "Pé", COUNT(*) as "Jogadores",
                   ROUND(AVG(overall_rating)::numeric,1) as "Rating Médio",
                   ROUND(AVG(finishing)::numeric,1) as "Finishing Médio",
                   ROUND(AVG(dribbling)::numeric,1) as "Dribbling Médio"
            FROM player_attributes
            WHERE preferred_foot IS NOT NULL
            GROUP BY preferred_foot
        """)
        st.dataframe(rows, use_container_width=True)
        st.bar_chart(rows.set_index("Pé")["Jogadores"])

    # ── Confronto direto ───────────────────────────────────────────────────────
    elif analise == "🆚 Confronto direto entre dois times":
        teams  = [r[0] for r in query("SELECT team_long_name FROM team ORDER BY team_long_name")]
        c1, c2 = st.columns(2)
        time1  = c1.selectbox("Time 1", teams, index=0)
        time2  = c2.selectbox("Time 2", teams, index=1)
        rows   = query_df("""
            SELECT m.date as "Data", m.season as "Temporada",
                   ht.team_long_name as "Mandante",
                   m.home_team_goal as "Gols M",
                   m.away_team_goal as "Gols V",
                   at.team_long_name as "Visitante"
            FROM match m
            JOIN team ht ON m.home_team_api_id = ht.team_api_id::bigint
            JOIN team at ON m.away_team_api_id = at.team_api_id::bigint
            WHERE (ht.team_long_name = :t1 AND at.team_long_name = :t2)
               OR (ht.team_long_name = :t2 AND at.team_long_name = :t1)
            ORDER BY m.date DESC
        """, {"t1": time1, "t2": time2})
        if not rows.empty:
            v1 = len(rows[((rows["Mandante"]==time1) & (rows["Gols M"] > rows["Gols V"])) |
                          ((rows["Visitante"]==time1) & (rows["Gols V"] > rows["Gols M"]))])
            v2 = len(rows[((rows["Mandante"]==time2) & (rows["Gols M"] > rows["Gols V"])) |
                          ((rows["Visitante"]==time2) & (rows["Gols V"] > rows["Gols M"]))])
            e  = len(rows[rows["Gols M"] == rows["Gols V"]])
            c1.metric(f"Vitórias {time1}", v1)
            c2.metric(f"Vitórias {time2}", v2)
            st.metric("Empates", e)
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("Nenhum confronto encontrado entre esses times.")

    # ── Evolução de atributo ───────────────────────────────────────────────────
    elif analise == "📊 Evolução de atributo de um jogador":
        atributos = ["overall_rating", "potential", "crossing", "finishing",
                     "dribbling", "sprint_speed", "stamina", "strength",
                     "shot_power", "long_shots", "agility", "reactions"]
        busca = st.text_input("Nome do jogador")
        attr  = st.selectbox("Atributo", atributos)
        if busca:
            rows = query_df(f"""
                SELECT pa.date as "Data", pa.{attr} as "Valor", p.player_name as "Jogador"
                FROM player_attributes pa
                JOIN player p ON pa.player_api_id = p.player_api_id
                WHERE p.player_name ILIKE :q AND pa.{attr} IS NOT NULL
                ORDER BY pa.date
            """, {"q": f"%{busca}%"})
            if not rows.empty:
                jogador = st.selectbox("Selecionar jogador", rows["Jogador"].unique())
                df_jog  = rows[rows["Jogador"] == jogador].set_index("Data")
                st.line_chart(df_jog["Valor"])
                st.dataframe(df_jog[["Valor"]], use_container_width=True)
            else:
                st.info("Jogador não encontrado.")
