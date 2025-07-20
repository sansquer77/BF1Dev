import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
import streamlit as st

# Parâmetros sensíveis
JWT_SECRET = st.secrets["JWT_SECRET"]
JWT_EXP_MINUTES = 120

def hash_password(password: str) -> str:
    """Gera um hash seguro para a senha usando bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Valida uma senha em texto puro contra seu hash."""
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(password.encode(), hashed)

def generate_token(user_id: int, perfil: str, status: str) -> str:
    """Gera um JWT para autenticação, com expiração."""
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
    """Valida e decodifica um JWT. Retorna o payload ou None se expirado/inválido."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except Exception:
        return None
