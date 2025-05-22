import streamlit as st
import sqlite3
import bcrypt
import jwt
import pandas as pd
from datetime import datetime, timedelta
import requests
import ast
import os
import re

DB_PATH = 'bolao_f1.db'
JWT_SECRET = os.getenv('JWT_SECRET', 'sua_chave_secreta_supersegura')
JWT_EXP_MINUTES = 120

def db_connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = db_connect()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        email TEXT UNIQUE,
                        senha_hash TEXT,
                        perfil TEXT,
                        status TEXT DEFAULT 'Ativo')''')
    senha_hash = bcrypt.hashpw('ADMIN'.encode(), bcrypt.gensalt()).decode('utf-8')
    c.execute('''INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil, status)
                 VALUES (?, ?, ?, ?, ?)''',
              ('Password', 'master@bolao.com', senha_hash, 'master', 'Ativo'))
    c.execute('''CREATE TABLE IF NOT EXISTS equipes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pilotos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        equipe_id INTEGER,
                        FOREIGN KEY(equipe_id) REFERENCES equipes(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS provas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT,
                        data TEXT,
                        session_key INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS apostas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER,
                        prova_id INTEGER,
                        data_envio TEXT,
                        pilotos TEXT,
                        fichas TEXT,
                        piloto_11 TEXT,
                        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                        FOREIGN KEY(prova_id) REFERENCES provas(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS resultados (
                        prova_id INTEGER PRIMARY KEY,
                        pontos_pilotos TEXT,
                        piloto_11 TEXT,
                        FOREIGN KEY(prova_id) REFERENCES provas(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS log_apostas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        apostador TEXT,
                        ip TEXT,
                        data TEXT,
                        horario TEXT,
                        aposta TEXT)''')
    conn.commit()
    conn.close()

# --- Funções de autenticação e usuários ---
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode(), hashed)

def generate_token(user_id, perfil, status):
    payload = {
        'user_id': user_id,
        'perfil': perfil,
        'status': status,
        'exp': datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None

def get_user_by_email(email):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, senha_hash, perfil, status FROM usuarios WHERE email=?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('SELECT id, nome, email, perfil, status FROM usuarios WHERE id=?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validar_senha(senha):
    return len(senha) >= 6

def cadastrar_usuario(nome, email, senha, perfil='participante'):
    if not validar_email(email):
        return "Email inválido"
    if not validar_senha(senha):
        return "Senha muito curta"
    conn = db_connect()
    c = conn.cursor()
    try:
        senha_hash = hash_password(senha)
        c.execute('INSERT INTO usuarios (nome, email, senha_hash, perfil, status) VALUES (?, ?, ?, ?, ?)', 
                  (nome, email, senha_hash, perfil, 'Ativo'))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def autenticar_usuario(email, senha):
    user = get_user_by_email(email)
    if user and check_password(senha, user[3]):
        return user
    return None

def listar_usuarios():
    conn = db_connect()
    df = pd.read_sql('SELECT id, nome, email, perfil, status FROM usuarios', conn)
    conn.close()
    return df

def alterar_status_usuario(user_id, novo_status):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE usuarios SET status=? WHERE id=?', (novo_status, user_id))
    conn.commit()
    conn.close()

def alterar_perfil_usuario(user_id, novo_perfil):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE usuarios SET perfil=? WHERE id=?', (novo_perfil, user_id))
    conn.commit()
    conn.close()

def editar_usuario(user_id, nome, email):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE usuarios SET nome=?, email=? WHERE id=?', (nome, email, user_id))
    conn.commit()
    conn.close()

def excluir_usuario(user_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM usuarios WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

# --- CRUD Equipes ---
def listar_equipes():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM equipes', conn)
    conn.close()
    return df

def adicionar_equipe(nome):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO equipes (nome) VALUES (?)', (nome,))
    conn.commit()
    conn.close()

def editar_equipe(equipe_id, novo_nome):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE equipes SET nome=? WHERE id=?', (novo_nome, equipe_id))
    conn.commit()
    conn.close()

def excluir_equipe(equipe_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM equipes WHERE id=?', (equipe_id,))
    conn.commit()
    conn.close()

# --- CRUD Pilotos ---
def listar_pilotos():
    conn = db_connect()
    df = pd.read_sql('SELECT p.id, p.nome, e.nome as equipe, p.equipe_id FROM pilotos p LEFT JOIN equipes e ON p.equipe_id=e.id', conn)
    conn.close()
    return df

def adicionar_piloto(nome, equipe_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO pilotos (nome, equipe_id) VALUES (?, ?)', (nome, equipe_id))
    conn.commit()
    conn.close()

def editar_piloto(piloto_id, novo_nome, nova_equipe_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE pilotos SET nome=?, equipe_id=? WHERE id=?', (novo_nome, nova_equipe_id, piloto_id))
    conn.commit()
    conn.close()

def excluir_piloto(piloto_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM pilotos WHERE id=?', (piloto_id,))
    conn.commit()
    conn.close()

# --- CRUD Provas ---
def listar_provas():
    conn = db_connect()
    df = pd.read_sql('SELECT * FROM provas', conn)
    conn.close()
    return df

def adicionar_prova(nome, data, session_key):
    conn = db_connect()
    c = conn.cursor()
    c.execute('INSERT INTO provas (nome, data, session_key) VALUES (?, ?, ?)', (nome, data, session_key))
    conn.commit()
    conn.close()

def editar_prova(prova_id, novo_nome, nova_data, nova_session_key):
    conn = db_connect()
    c = conn.cursor()
    c.execute('UPDATE provas SET nome=?, data=?, session_key=? WHERE id=?', (novo_nome, nova_data, nova_session_key, prova_id))
    conn.commit()
    conn.close()

def excluir_prova(prova_id):
    conn = db_connect()
    c = conn.cursor()
    c.execute('DELETE FROM provas WHERE id=?', (prova_id,))
    conn.commit()
    conn.close()

# --- CRUD Resultados ---
def salvar_resultado(prova_id, pontos_pilotos, piloto_11):
    conn = db_connect()
    c = conn.cursor()
    c.execute('REPLACE INTO resultados (prova_id, pontos_pilotos, piloto_11) VALUES (?, ?, ?)',
              (prova_id, str(pontos_pilotos), str(piloto_11)))
    conn.commit()
    conn.close()

# --- Log de*
