# ⚽ European Soccer Database

Projeto Final da disciplina de **Banco de Dados** — Universidade Federal da Paraíba (UFPB)

> Aplicação web com operações CRUD e análises interativas sobre o dataset [European Soccer Database](https://www.kaggle.com/datasets/hugomathien/soccer) do Kaggle.

---

## 🔗 Demo

Acesse a aplicação em produção:  
**[european-soccer-db.streamlit.app](https://european-soccer-db.streamlit.app)**

---

## 📋 Sobre o Projeto

O projeto consiste em quatro etapas principais:

1. **Dataset** — European Soccer Database (Kaggle · Hugo Mathien), com dados reais de futebol europeu cobrindo 11 ligas entre 2008 e 2016
2. **Modelo Relacional** — 7 tabelas normalizadas com chaves primárias e estrangeiras
3. **Projeto Físico** — PostgreSQL hospedado no Neon (cloud), com importação dos dados via Python
4. **Aplicação CRUD** — Interface web em Streamlit com operações de inserção, consulta, edição e exclusão, além de análises avançadas

---

## 🗄️ Modelo Relacional

```
COUNTRY ──< LEAGUE
COUNTRY ──< MATCH
LEAGUE  ──< MATCH
TEAM    ──< MATCH (mandante e visitante)
TEAM    ──< TEAM_ATTRIBUTES
PLAYER  ──< PLAYER_ATTRIBUTES
```

| Tabela | Registros |
|--------|-----------|
| Country | 11 |
| League | 11 |
| Team | 299 |
| Team_Attributes | 1.458 |
| Player | 11.060 |
| Player_Attributes | 183.978 |
| Match | 25.979 |

---

## 🚀 Como rodar localmente

### Pré-requisitos

- Python 3.10+
- Conta no [Neon](https://neon.tech) com o banco populado (ou PostgreSQL local)

### Instalação

```bash
git clone https://github.com/pedroveloso25/european_soccer_db.git
cd european_soccer_db
pip install -r requirements.txt
```

### Configuração

No arquivo `app.py`, substitua a `DATABASE_URL` pela sua connection string:

```python
DATABASE_URL = "postgresql://usuario:senha@host/banco?sslmode=require"
```

### Executar

```bash
streamlit run app.py
```

Acesse em `http://localhost:8501`

---

## 📦 Importação dos dados

O dataset original está no formato SQLite. Para importar para o PostgreSQL:

1. Baixe o dataset no [Kaggle](https://www.kaggle.com/datasets/hugomathien/soccer)
2. Extraia o arquivo `database.sqlite`
3. Execute o script de importação:

```python
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

SQLITE_PATH = "caminho/para/database.sqlite"
DATABASE_URL = "sua_connection_string_aqui"

sqlite_conn = sqlite3.connect(SQLITE_PATH)
engine      = create_engine(DATABASE_URL)

tabelas = ['Country', 'League', 'Team', 'Team_Attributes',
           'Player', 'Player_Attributes', 'Match']

for tabela in tabelas:
    df = pd.read_sql(f"SELECT * FROM {tabela}", sqlite_conn)
    df.columns = df.columns.str.lower()
    df.to_sql(tabela.lower(), engine, if_exists='replace', index=False)
    print(f"{tabela}: {len(df)} linhas importadas ✓")

sqlite_conn.close()
```

---

## 🧩 Funcionalidades

### CRUD

| Tabela | Inserir | Consultar | Editar | Deletar |
|--------|---------|-----------|--------|---------|
| Players | ✅ | ✅ | ✅ | ✅ |
| Teams | ✅ | ✅ | ✅ | ✅ |
| Leagues | ✅ | ✅ | ✅ | ✅ |
| Matches | ✅ | ✅ | ✅ | ✅ |

### Análises

- 🥅 Gols marcados por time (por temporada e liga)
- ⚡ Top jogadores por atributo (drible, velocidade, finalização...)
- 🏆 Tabela de classificação com pontos e saldo de gols
- 📅 Todas as partidas de um time específico
- 🔥 Jogos com mais gols por temporada
- 📈 Média de gols por temporada e liga
- 👟 Distribuição por pé preferido com médias de atributos
- 🆚 Confronto direto entre dois times
- 📊 Evolução de atributo de um jogador ao longo do tempo

---

## 🛠️ Stack

| Tecnologia | Uso |
|------------|-----|
| Python 3.13 | Linguagem principal |
| Streamlit | Interface web |
| SQLAlchemy | ORM e gerenciamento de conexão |
| psycopg2-binary | Driver PostgreSQL |
| Pandas | Manipulação de dados e importação |
| PostgreSQL 17 | SGBD relacional |
| Neon | Hospedagem do banco na nuvem |
| Streamlit Cloud | Deploy da aplicação |

---

## 👥 Equipe

- Pedro Veloso
- Vitor Batista

---

## 📚 Disciplina

**Banco de Dados** — Prof. Dr. José Jorge Dias  
