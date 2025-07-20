import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("bolao_f1Dev.db")


def db_connect(db_path: Path = DB_PATH):
    """Retorna uma conexão SQLite com o banco principal do bolão e campeonato."""
    return sqlite3.connect(str(db_path))


def init_db():
    """Cria todas as tabelas necessárias, inclusive as de campeonato."""
    conn = db_connect()
    c = conn.cursor()

    # Tabelas principais
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT UNIQUE,
        senha_hash TEXT,
        perfil TEXT,
        status TEXT DEFAULT 'Ativo',
        faltas INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pilotos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        equipe TEXT,
        status TEXT DEFAULT 'Ativo'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS provas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        data TEXT,
        horario_prova TEXT,
        status TEXT DEFAULT 'Ativo',
        tipo TEXT DEFAULT 'Normal'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS apostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        prova_id INTEGER,
        data_envio TEXT,
        pilotos TEXT,
        fichas TEXT,
        piloto_11 TEXT,
        nome_prova TEXT,
        automatica INTEGER DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(prova_id) REFERENCES provas(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
        prova_id INTEGER PRIMARY KEY,
        posicoes TEXT,
        FOREIGN KEY(prova_id) REFERENCES provas(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS posicoes_participantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prova_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        posicao INTEGER NOT NULL,
        pontos REAL NOT NULL,
        data_registro TEXT DEFAULT (datetime('now')),
        UNIQUE(prova_id, usuario_id),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (prova_id) REFERENCES provas(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS log_apostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apostador TEXT,
        data TEXT,
        horario TEXT,
        aposta TEXT,
        piloto_11 TEXT,
        nome_prova TEXT,
        tipo_aposta INTEGER DEFAULT 0,
        automatica INTEGER DEFAULT 0
    )''')

    # Tabelas do campeonato (unificadas)
    c.execute('''CREATE TABLE IF NOT EXISTS championship_bets (
        user_id INTEGER PRIMARY KEY,
        user_nome TEXT NOT NULL,
        champion TEXT NOT NULL,
        vice TEXT NOT NULL,
        team TEXT NOT NULL,
        bet_time TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS championship_bets_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_nome TEXT NOT NULL,
        champion TEXT NOT NULL,
        vice TEXT NOT NULL,
        team TEXT NOT NULL,
        bet_time TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS championship_results (
        season INTEGER PRIMARY KEY DEFAULT 2025,
        champion TEXT NOT NULL,
        vice TEXT NOT NULL,
        team TEXT NOT NULL
    )''')

    conn.commit()
    conn.close()


# Funções utilitárias para DataFrames (pandas) das tabelas principais
def get_usuarios_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM usuarios', conn)
    conn.close()
    return df

def get_pilotos_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM pilotos', conn)
    conn.close()
    return df

def get_provas_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM provas', conn)
    conn.close()
    return df

def get_apostas_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM apostas', conn)
    conn.close()
    return df

def get_resultados_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()
    return df


# Funções utilitárias para as tabelas de championship
def get_championship_bets_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM championship_bets', conn)
    conn.close()
    return df

def get_championship_bets_log_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM championship_bets_log', conn)
    conn.close()
    return df

def get_championship_results_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM championship_results', conn)
    conn.close()
    return df


# Utilitários extras para championship (usando uma única conexão)
def get_user_name(user_id: int) -> str:
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM usuarios WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "Nome não encontrado"
    except Exception:
        return "Erro ao buscar nome"
