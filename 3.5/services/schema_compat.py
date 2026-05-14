"""Camada de compatibilidade de schema para tabelas com colunas opcionais.

Centraliza toda a lógica de detecção e normalização de schema, eliminando
ramificações defensivas espalhadas no código de negócio.
"""

from __future__ import annotations

import pandas as pd


# ---------------------------------------------------------------------------
# Detecção de colunas opcionais
# ---------------------------------------------------------------------------

def has_coluna_temporada_apostas(ap_df: pd.DataFrame) -> bool:
    """Retorna True se o DataFrame de apostas possui a coluna 'temporada'."""
    return "temporada" in ap_df.columns


def has_coluna_temporada_provas(prov_df: pd.DataFrame) -> bool:
    """Retorna True se o DataFrame de provas possui a coluna 'temporada'."""
    return "temporada" in prov_df.columns


def has_coluna_temporada_tabela(conn, tabela: str) -> bool:
    """Retorna True se a tabela no banco possui a coluna 'temporada'."""
    from db.db_schema import get_table_columns
    return "temporada" in get_table_columns(conn, tabela)


# ---------------------------------------------------------------------------
# Normalização de DataFrames
# ---------------------------------------------------------------------------

def normalizar_apostas(
        ap_df: pd.DataFrame,
        temporada_fallback: str | None = None) -> pd.DataFrame:
    """Garante que o DataFrame de apostas sempre possua a coluna 'temporada'.

    Se a coluna não existir, é criada com o valor de *temporada_fallback*.
    Se existir, valores nulos são substituídos por *temporada_fallback*.
    """
    df = ap_df.copy()
    if "temporada" not in df.columns:
        df["temporada"] = temporada_fallback
    else:
        if temporada_fallback is not None:
            df["temporada"] = df["temporada"].fillna(temporada_fallback)
    return df


def normalizar_provas(
        prov_df: pd.DataFrame,
        temporada_fallback: str | None = None) -> pd.DataFrame:
    """Garante que o DataFrame de provas sempre possua a coluna 'temporada'."""
    from datetime import datetime
    fallback = temporada_fallback or str(datetime.now().year)
    df = prov_df.copy()
    if "temporada" not in df.columns:
        df["temporada"] = fallback
    else:
        df["temporada"] = df["temporada"].fillna(fallback)
    return df


# ---------------------------------------------------------------------------
# Resolução de temporada por aposta / prova
# ---------------------------------------------------------------------------

def resolver_temporada_aposta(
    aposta: pd.Series,
    temporadas_prova: dict,
    fallback_year: str,
) -> str:
    """Resolve a temporada correta para uma aposta.

    Prioridade:
    1. Coluna 'temporada' da própria aposta (se preenchida).
    2. Temporada herdada da prova correspondente.
    3. *fallback_year*.
    """
    try:
        t = aposta.get("temporada", None)
        if t is not None and str(t).strip() and not pd.isna(t):
            return str(t).strip()
    except Exception:
        pass
    return temporadas_prova.get(aposta["prova_id"], fallback_year)


__all__ = [
    "has_coluna_temporada_apostas",
    "has_coluna_temporada_provas",
    "has_coluna_temporada_tabela",
    "normalizar_apostas",
    "normalizar_provas",
    "resolver_temporada_aposta",
]
