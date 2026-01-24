\"\"\"
Utilitários para Gestão de Regras de Temporada
\"\"\"

import sqlite3
import logging
from typing import Optional, Dict
from db.connection_pool import get_pool

logger = logging.getLogger(__name__)


def init_rules_table():
    \"\"\"Cria a tabela de regras se não existir\"\"\"
    with get_pool().get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS regras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_regra TEXT NOT NULL UNIQUE,
                quantidade_fichas INTEGER NOT NULL DEFAULT 15,
                mesma_equipe INTEGER NOT NULL DEFAULT 0,
                fichas_por_piloto INTEGER NOT NULL DEFAULT 15,
                descarte INTEGER NOT NULL DEFAULT 0,
                pontos_11_colocado INTEGER NOT NULL DEFAULT 25,
                qtd_minima_pilotos INTEGER NOT NULL DEFAULT 3,
                penalidade_abandono INTEGER NOT NULL DEFAULT 0,
                pontos_penalidade INTEGER DEFAULT 0,
                regra_sprint INTEGER NOT NULL DEFAULT 0,
                provas_wildcard INTEGER NOT NULL DEFAULT 0,
                pontos_campeao INTEGER NOT NULL DEFAULT 150,
                pontos_vice INTEGER NOT NULL DEFAULT 100,
                pontos_equipe INTEGER NOT NULL DEFAULT 80,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS temporadas_regras (
                temporada TEXT PRIMARY KEY,
                regra_id INTEGER NOT NULL,
                FOREIGN KEY(regra_id) REFERENCES regras(id)
            )
        ''')
        
        conn.commit()
        logger.info(\"✓ Tabelas de regras inicializadas\")


def criar_regra(
    nome_regra: str,
    quantidade_fichas: int = 15,
    mesma_equipe: bool = False,
    fichas_por_piloto: int = 15,
    descarte: bool = False,
    pontos_11_colocado: int = 25,
    qtd_minima_pilotos: int = 3,
    penalidade_abandono: bool = False,
    pontos_penalidade: int = 0,
    regra_sprint: bool = False,
    provas_wildcard: bool = False,
    pontos_campeao: int = 150,
    pontos_vice: int = 100,
    pontos_equipe: int = 80
) -> bool:
    \"\"\"Cria uma nova regra\"\"\"
    try:
        with get_pool().get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO regras (
                    nome_regra, quantidade_fichas, mesma_equipe, fichas_por_piloto,
                    descarte, pontos_11_colocado, qtd_minima_pilotos,
                    penalidade_abandono, pontos_penalidade, regra_sprint,
                    provas_wildcard, pontos_campeao, pontos_vice, pontos_equipe
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nome_regra, quantidade_fichas, int(mesma_equipe), fichas_por_piloto,
                int(descarte), pontos_11_colocado, qtd_minima_pilotos,
                int(penalidade_abandono), pontos_penalidade, int(regra_sprint),
                int(provas_wildcard), pontos_campeao, pontos_vice, pontos_equipe
            ))
            conn.commit()
            logger.info(f\"✓ Regra criada: {nome_regra}\")
            return True
    except sqlite3.IntegrityError:
        logger.error(f\"Regra com nome '{nome_regra}' já existe\")
        return False
    except Exception as e:
        logger.error(f\"Erro ao criar regra: {e}\")
        return False


def atualizar_regra(
    regra_id: int,
    nome_regra: str,
    quantidade_fichas: int,
    mesma_equipe: bool,
    fichas_por_piloto: int,
    descarte: bool,
    pontos_11_colocado: int,
    qtd_minima_pilotos: int,
    penalidade_abandono: bool,
    pontos_penalidade: int,
    regra_sprint: bool,
    provas_wildcard: bool,
    pontos_campeao: int,
    pontos_vice: int,
    pontos_equipe: int
) -> bool:
    \"\"\"Atualiza uma regra existente\"\"\"
    try:
        with get_pool().get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE regras SET
                    nome_regra = ?,
                    quantidade_fichas = ?,
                    mesma_equipe = ?,
                    fichas_por_piloto = ?,
                    descarte = ?,
                    pontos_11_colocado = ?,
                    qtd_minima_pilotos = ?,
                    penalidade_abandono = ?,
                    pontos_penalidade = ?,
                    regra_sprint = ?,
                    provas_wildcard = ?,
                    pontos_campeao = ?,
                    pontos_vice = ?,
                    pontos_equipe = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                nome_regra, quantidade_fichas, int(mesma_equipe), fichas_por_piloto,
                int(descarte), pontos_11_colocado, qtd_minima_pilotos,
                int(penalidade_abandono), pontos_penalidade, int(regra_sprint),
                int(provas_wildcard), pontos_campeao, pontos_vice, pontos_equipe,
                regra_id
            ))
            conn.commit()
            logger.info(f\"✓ Regra ID {regra_id} atualizada\")
            return True
    except Exception as e:
        logger.error(f\"Erro ao atualizar regra: {e}\")
        return False


def excluir_regra(regra_id: int) -> bool:
    \"\"\"Exclui uma regra (apenas se não estiver em uso)\"\"\"
    try:
        with get_pool().get_connection() as conn:
            c = conn.cursor()
            # Verifica se está em uso
            c.execute('SELECT COUNT(*) FROM temporadas_regras WHERE regra_id = ?', (regra_id,))
            if c.fetchone()[0] > 0:
                logger.warning(f\"Regra ID {regra_id} está em uso e não pode ser excluída\")
                return False
            
            c.execute('DELETE FROM regras WHERE id = ?', (regra_id,))
            conn.commit()
            logger.info(f\"✓ Regra ID {regra_id} excluída\")
            return True
    except Exception as e:
        logger.error(f\"Erro ao excluir regra: {e}\")
        return False


def get_regra_by_id(regra_id: int) -> Optional[Dict]:
    \"\"\"Retorna uma regra pelo ID\"\"\"
    with get_pool().get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM regras WHERE id = ?', (regra_id,))
        row = c.fetchone()
        return dict(row) if row else None


def get_regra_by_nome(nome_regra: str) -> Optional[Dict]:
    \"\"\"Retorna uma regra pelo nome\"\"\"
    with get_pool().get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM regras WHERE nome_regra = ?', (nome_regra,))
        row = c.fetchone()
        return dict(row) if row else None


def listar_regras():
    \"\"\"Lista todas as regras cadastradas\"\"\"
    with get_pool().get_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM regras ORDER BY nome_regra')
        return [dict(row) for row in c.fetchall()]


def associar_regra_temporada(temporada: str, regra_id: int) -> bool:
    \"\"\"Associa uma regra a uma temporada\"\"\"
    try:
        with get_pool().get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO temporadas_regras (temporada, regra_id)
                VALUES (?, ?)
            ''', (temporada, regra_id))
            conn.commit()
            logger.info(f\"✓ Regra ID {regra_id} associada à temporada {temporada}\")
            return True
    except Exception as e:
        logger.error(f\"Erro ao associar regra: {e}\")
        return False


def get_regra_temporada(temporada: str) -> Optional[Dict]:
    \"\"\"Retorna a regra associada a uma temporada\"\"\"
    with get_pool().get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT r.* FROM regras r
            INNER JOIN temporadas_regras tr ON r.id = tr.regra_id
            WHERE tr.temporada = ?
        ''', (temporada,))
        row = c.fetchone()
        return dict(row) if row else None


def criar_regra_padrao():
    \"\"\"Cria regra padrão caso não exista\"\"\"
    regra_padrao = get_regra_by_nome(\"Padrão BF1\")
    if not regra_padrao:
        criar_regra(
            nome_regra=\"Padrão BF1\",
            quantidade_fichas=15,
            mesma_equipe=False,
            fichas_por_piloto=15,
            descarte=False,
            pontos_11_colocado=25,
            qtd_minima_pilotos=3,
            penalidade_abandono=False,
            pontos_penalidade=0,
            regra_sprint=False,
            provas_wildcard=False,
            pontos_campeao=150,
            pontos_vice=100,
            pontos_equipe=80
        )
        logger.info(\"✓ Regra padrão criada\")
