import sqlite3
import pandas as pd
from pathlib import Path
import streamlit as st
import bcrypt

DB_PATH = Path("bolao_f1Dev.db")

def db_connect(db_path=DB_PATH):
    return sqlite3.connect(str(db_path))

def init_db():
    conn = db_connect()
    c = conn.cursor()
    # Tabela de usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT UNIQUE,
            senha_hash TEXT,
            perfil TEXT,
            status TEXT DEFAULT 'Ativo',
            faltas INTEGER DEFAULT 0
        )
    ''')
    # Tabela de pilotos
    c.execute('''
        CREATE TABLE IF NOT EXISTS pilotos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            equipe TEXT,
            status TEXT DEFAULT 'Ativo'
        )
    ''')
    # Tabela de provas/corridas
    c.execute('''
        CREATE TABLE IF NOT EXISTS provas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            data TEXT,
            horario_prova TEXT,
            status TEXT DEFAULT 'Ativo',
            tipo TEXT DEFAULT 'Normal'
        )
    ''')
    # Tabela de apostas
    c.execute('''
        CREATE TABLE IF NOT EXISTS apostas (
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
        )
    ''')
    # Tabela de resultados
    c.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            prova_id INTEGER PRIMARY KEY,
            posicoes TEXT,
            FOREIGN KEY(prova_id) REFERENCES provas(id)
        )
    ''')
    # Tabela de log de apostas
    c.execute('''
        CREATE TABLE IF NOT EXISTS log_apostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apostador TEXT,
            data TEXT,
            horario TEXT,
            aposta TEXT,
            nome_prova TEXT,
            piloto_11 TEXT,
            tipo_aposta INTEGER DEFAULT 0,
            automatica INTEGER DEFAULT 0
        )
    ''')

    # Usuário master se já houver st.secrets
    if hasattr(st, "secrets") and all(k in st.secrets for k in ["usuario_master", "email_master", "senha_master"]):
        usuario_master = st.secrets["usuario_master"]
        email_master = st.secrets["email_master"]
        senha_master = st.secrets["senha_master"]
        senha_hash = bcrypt.hashpw(senha_master.encode(), bcrypt.gensalt()).decode("utf-8")
        c.execute('''
            INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil, status, faltas)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (usuario_master, email_master, senha_hash, 'master', 'Ativo', 0))

    conn.commit()
    conn.close()

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

def get_horario_prova(prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT nome, data, horario_prova FROM provas WHERE id=?', (prova_id,))
    res = c.fetchone()
    conn.close()
    if not res:
        return None, None, None
    return res[0], res[1], res[2]

def get_user_by_id(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, perfil, status, faltas FROM usuarios WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_resultados_df():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM resultados', conn)
    conn.close()
    return df

def registrar_log_aposta(apostador, aposta, nome_prova, piloto_11, tipo_aposta, automatica, horario=None):
    from datetime import datetime
    from zoneinfo import ZoneInfo
    if horario is None:
        horario = datetime.now(ZoneInfo("America/Sao_Paulo"))
    data = horario.strftime('%Y-%m-%d')
    hora = horario.strftime('%H:%M:%S')
    conn = db_connect()
    c = conn.cursor()
    c.execute('''INSERT INTO log_apostas
                 (apostador, data, horario, aposta, nome_prova, piloto_11, tipo_aposta, automatica)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (apostador, data, hora, aposta, nome_prova, piloto_11, tipo_aposta, automatica))
    conn.commit()
    conn.close()

def log_aposta_existe(apostador, nome_prova, tipo_aposta, automatica, dados_aposta):
    conn = db_connect()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM log_apostas
                 WHERE apostador=? AND nome_prova=? AND tipo_aposta=? AND automatica=? AND aposta=?''',
              (apostador, nome_prova, tipo_aposta, automatica, dados_aposta))
    count = c.fetchone()[0]
    conn.close()
    return count > 0
