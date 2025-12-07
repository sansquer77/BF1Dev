"""
Utilitários de Banco de Dados - Versão 3.0
Melhorias: bcrypt para senhas, pool de conexões, caching
"""

import sqlite3
import pandas as pd
from pathlib import Path
import bcrypt
import logging
from typing import Optional, Dict
from db.connection_pool import get_pool, init_pool
from db.db_config import BCRYPT_ROUNDS, DB_PATH

logger = logging.getLogger(__name__)

# Inicializar pool ao importar
init_pool(str(DB_PATH))

# ============ FUNÇÕES DE CONEXÃO ============

def db_connect():
    """Retorna uma conexão do pool"""
    return get_pool().get_connection()

# ============ FUNÇÕES DE SEGURANÇA (BCRYPT) ============

def hash_password(senha: str) -> str:
    """
    Hash seguro de senha usando bcrypt
    
    Args:
        senha: Senha em texto plano
    
    Returns:
        Hash da senha (bcrypt)
    """
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

def check_password(senha: str, hash_senha: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    
    Args:
        senha: Senha em texto plano
        hash_senha: Hash do bcrypt
    
    Returns:
        True se a senha é válida
    """
    try:
        return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))
    except (ValueError, TypeError):
        logger.error("Erro ao verificar password - hash inválido")
        return False

# ============ TABELAS ============

def init_db():
    """Inicializa o banco de dados com todas as tabelas necessárias"""
    with db_connect() as conn:
        c = conn.cursor()
        
        # Tabela de usuários
        c.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                perfil TEXT NOT NULL,
                status TEXT DEFAULT 'Ativo',
                faltas INTEGER DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de pilotos
        c.execute('''
            CREATE TABLE IF NOT EXISTS pilotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                numero INTEGER UNIQUE NOT NULL,
                equipe_id INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(equipe_id) REFERENCES equipes(id)
            )
        ''')
        
        # Tabela de equipes
        c.execute('''
            CREATE TABLE IF NOT EXISTS equipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de provas
        c.execute('''
            CREATE TABLE IF NOT EXISTS provas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data DATE NOT NULL,
                status TEXT DEFAULT 'Aberta',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de apostas
        c.execute('''
            CREATE TABLE IF NOT EXISTS apostas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                prova_id INTEGER NOT NULL,
                piloto_id INTEGER NOT NULL,
                pontos INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY(prova_id) REFERENCES provas(id),
                FOREIGN KEY(piloto_id) REFERENCES pilotos(id)
            )
        ''')
        
        # Tabela de resultados
        c.execute('''
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prova_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                piloto_id INTEGER NOT NULL,
                posicao INTEGER,
                pontos_ganhos INTEGER DEFAULT 0,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(prova_id) REFERENCES provas(id),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY(piloto_id) REFERENCES pilotos(id)
            )
        ''')
        
        # Tabela de log de tentativas de login (para rate limiting)
        c.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                tentativa_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sucesso BOOLEAN DEFAULT 0,
                ip_address TEXT
            )
        ''')
        
        conn.commit()
        logger.info("✓ Banco de dados inicializado com sucesso")

# ============ OPERAÇÕES CRUD ============

def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Retorna usuário pelo email
    
    Args:
        email: Email do usuário
    
    Returns:
        Dict com dados do usuário ou None
    """
    with db_connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        row = c.fetchone()
        
        if row:
            return dict(row)
        return None

def get_master_user() -> Optional[Dict]:
    """Retorna o usuário Master se existir"""
    return get_user_by_email('master@sistema.local')

def cadastrar_usuario(nome: str, email: str, senha: str, perfil: str = "participante"):
    """Registra novo usuário com senha bcrypt"""
    senha_hash = hash_password(senha)
    with db_connect() as conn:
        c = conn.cursor()
        c.execute(
            'INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)',
            (nome, email, senha_hash, perfil)
        )
        conn.commit()
        logger.info(f"✓ Usuário cadastrado: {email}")

def autenticar_usuario(email: str, senha: str) -> dict:
    """Autentica usuário com bcrypt"""
