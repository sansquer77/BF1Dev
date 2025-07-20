import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from db.db_utils import db_connect

# Configuração do segredo JWT — recomendável carregar do Streamlit Secrets ou config.py
import streamlit as st
JWT_SECRET = st.secrets["JWT_SECRET"]
JWT_EXP_MINUTES = 120

def hash_password(password: str) -> str:
    """Gera um hash bcrypt para a senha fornecida."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Valida uma senha em texto puro contra um hash bcrypt."""
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(password.encode(), hashed)

def autenticar_usuario(email: str, senha: str):
    """Retorna o usuário autenticado (tupla de dados) ou None."""
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, nome, email, senha_hash, perfil, status FROM usuarios WHERE email=?", (email,)
    )
    user = c.fetchone()
    conn.close()
    if user and check_password(senha, user[3]):
        return user
    return None

def generate_token(user_id: int, perfil: str, status: str) -> str:
    """Gera um JWT para o usuário autenticado."""
    payload = {
        "user_id": user_id,
        "perfil": perfil,
        "status": status,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token: str):
    """Decodifica e valida um JWT; retorna o payload em caso de sucesso."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except Exception:
        return None

def cadastrar_usuario(nome: str, email: str, senha: str, perfil="participante", status="Ativo") -> bool:
    """Cria novo usuário, garantindo unicidade de email."""
    conn = db_connect()
    c = conn.cursor()
    try:
        senha_hash = hash_password(senha)
        c.execute(
            'INSERT INTO usuarios (nome, email, senha_hash, perfil, status, faltas) VALUES (?, ?, ?, ?, ?, ?)',
            (nome, email, senha_hash, perfil, status, 0)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_user_by_email(email: str):
    """Busca e retorna dados do usuário pelo email."""
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, nome, email, senha_hash, perfil, status, faltas FROM usuarios WHERE email=?",
        (email,)
    )
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Busca e retorna dados do usuário pelo id."""
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, nome, email, perfil, status, faltas FROM usuarios WHERE id=?",
        (user_id,)
    )
    user = c.fetchone()
    conn.close()
    return user
