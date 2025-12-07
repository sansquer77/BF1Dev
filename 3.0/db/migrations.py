"""
Sistema de Migrations para Criar e Otimizar Tabelas
Adiciona índices para melhor performance
"""

from pathlib import Path
import datetime
from db.connection_pool import get_pool
from db.db_config import INDICES
import logging

logger = logging.getLogger(__name__)


def add_temporada_columns_if_missing():
    """
    Adiciona coluna `temporada` a tabelas de provas, apostas e resultados.
    Idempotent: não faz nada se a coluna já existe.
    """
    pool = get_pool()
    tables_to_update = {
        'provas': 'Adiciona temporada às provas',
        'apostas': 'Adiciona temporada às apostas',
        'resultados': 'Adiciona temporada aos resultados',
        'posicoes_participantes': 'Adiciona temporada às posições'
    }
    
    current_year = str(datetime.datetime.now().year)
    
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        for table_name, description in tables_to_update.items():
            try:
                # Check if table exists and if temporada column is missing
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                cols = [r[1] for r in cursor.fetchall()]
                
                if 'temporada' not in cols:
                    # Add temporada column with default value
                    cursor.execute(
                        f"ALTER TABLE {table_name} ADD COLUMN temporada TEXT DEFAULT '{current_year}'"
                    )
                    logger.info(f"✓ Coluna `temporada` adicionada a `{table_name}`")
                else:
                    logger.debug(f"  Coluna `temporada` já existe em `{table_name}`, pulando...")
            except Exception as e:
                logger.debug(f"  Skipping {table_name}: {e}")
        
        conn.commit()

def run_migrations():
    """
    Executa todas as migrations de banco de dados
    Cria índices para otimização de queries
    """
    pool = get_pool()
    
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Adicionar colunas temporada (plurianual support)
            add_temporada_columns_if_missing()
            
            # Criar índices para usuários
            for idx in INDICES.get("usuarios", []):
                cursor.execute(idx)
                logger.info(f"✓ Índice criado: {idx.split('IF NOT EXISTS')[1].strip()}")
            
            # Criar índices para apostas
            for idx in INDICES.get("apostas", []):
                cursor.execute(idx)
                logger.info(f"✓ Índice criado: {idx.split('IF NOT EXISTS')[1].strip()}")
            
            # Criar índices para provas
            for idx in INDICES.get("provas", []):
                cursor.execute(idx)
                logger.info(f"✓ Índice criado: {idx.split('IF NOT EXISTS')[1].strip()}")
            
            # Criar índices para resultados
            for idx in INDICES.get("resultados", []):
                cursor.execute(idx)
                logger.info(f"✓ Índice criado: {idx.split('IF NOT EXISTS')[1].strip()}")
            
            conn.commit()
            logger.info("✓ Todas as migrations executadas com sucesso!")
            
        except Exception as e:
            logger.error(f"✗ Erro ao executar migrations: {e}")
            conn.rollback()
            raise
