import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from db.db_utils import db_connect
import streamlit as st
import extra_streamlit_components as stx

JWT_SECRET = st.secrets["JWT_SECRET"]
JWT_EXP_MINUTES = 120

# --- HASH E CHECK DE SENHA ---
def hash_password(password: str) -> str:
    """Gera um hash bcrypt para a senha fornecida."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Valida uma senha em texto puro contra um hash bcrypt."""
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(password.encode(), hashed)

# --- AUTENTICAÇÃO ---
def autenticar_usuario(email: str, senha: str):
    """Retorna o usuário autenticado (tupla de dados) ou None."""
    conn = db_connect()
    c = conn.cursor()
    c.execute(
        "SELECT id, nome, email, senha_hash, perfil, status FROM usuarios WHERE email=?",
        (email,)
    )
    user = c.fetchone()
    conn.close()
    if user and check_password(senha, user[3]):
        return user
    return None

# --- GERAÇÃO E DECODIFICAÇÃO DE TOKEN JWT ---
def generate_token(user_id: int, nome: str, perfil: str, status: str) -> str:
    """Gera um JWT para o usuário autenticado, incluindo o nome."""
    payload = {
        "user_id": user_id,
        "nome": nome,     # Incluído o nome no payload
        "perfil": perfil,
        "status": status,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token: str):
    """Decodifica e valida um JWT; retorna o payload, ou None se inválido/expirado."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except Exception:
        return None

# --- REGISTRO DE USUÁRIO ---
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

# --- BUSCA DE USUÁRIOS ---
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

# --- GESTÃO DE COOKIES (para login) ---
def set_auth_cookies(token, expires_minutes=JWT_EXP_MINUTES):
    """Salva o token JWT em cookie para restaurar a sessão."""
    cookie_manager = stx.CookieManager()
    expires_at = datetime.now() + timedelta(minutes=expires_minutes)
    cookie_manager.set(
        "session_token",
        token,
        expires_at=expires_at,
        key="session_token"
    )

def clear_auth_cookies():
    cookie_manager = stx.CookieManager()
    cookie_manager.delete("session_token", key="session_token")
