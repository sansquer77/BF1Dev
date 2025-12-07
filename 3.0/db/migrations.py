"""
Sistema de Migrations para Criar e Otimizar Tabelas
Adiciona índices para melhor performance
"""

from pathlib import Path
from db.connection_pool import get_pool
from db.db_config import INDICES
import logging

logger = logging.getLogger(__name__)

def run_migrations():
    """
    Executa todas as migrations de banco de dados
    Cria índices para otimização de queries
    """
    pool = get_pool()
    
    with pool.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
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
