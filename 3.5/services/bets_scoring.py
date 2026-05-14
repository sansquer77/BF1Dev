"""Cálculo de pontuação e classificação de apostas."""

from __future__ import annotations

import ast
import logging
from datetime import datetime
from typing import Optional, cast

import pandas as pd

from db.db_schema import db_connect
from services.rules_service import get_regras_aplicaveis
from services.schema_compat import (
    has_coluna_temporada_tabela,
    normalizar_apostas,
    normalizar_provas,
    resolver_temporada_aposta,
)
from utils.datetime_utils import parse_datetime_sao_paulo

logger = logging.getLogger(__name__)

PONTOS_F1_NORMAL = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
PONTOS_SPRINT = [8, 7, 6, 5, 4, 3, 2, 1]


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _fetch_df(conn, query: str, params: tuple | None = None) -> pd.DataFrame:
    cur = conn.cursor()
    cur.execute(query, params or ())
    rows = cur.fetchall() or []
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])


def _parse_datetime_sp(date_str: str, time_str: str):
    return parse_datetime_sao_paulo(date_str, time_str)


# ---------------------------------------------------------------------------
# Construção de estruturas auxiliares a partir dos DataFrames brutos
# ---------------------------------------------------------------------------

def _construir_mapa_resultados(res_df: pd.DataFrame) -> tuple[dict, dict]:
    """Retorna (ress_map, abandonos_map) indexados por prova_id."""
    ress_map: dict = {}
    abandonos_map: dict = {}
    for _, r in res_df.iterrows():
        prova_id = r["prova_id"]
        try:
            ress_map[prova_id] = ast.literal_eval(r["posicoes"])
        except Exception:
            logger.exception(
                "Erro ao parsear posições da prova_id=%s", prova_id)
            continue
        try:
            if "abandono_pilotos" in res_df.columns:
                raw = r.get("abandono_pilotos", "") or ""
                abandonos_map[prova_id] = {
                    p.strip() for p in str(raw).split(",") if p.strip()}
            else:
                abandonos_map[prova_id] = set()
        except Exception:
            logger.exception(
                "Erro ao parsear abandonos da prova_id=%s",
                prova_id)
            abandonos_map[prova_id] = set()
    return ress_map, abandonos_map


def _construir_tipos_prova(prov_df: pd.DataFrame) -> dict:
    """Retorna {prova_id: 'Sprint'|'Normal'}."""
    tipos = prov_df["tipo"].fillna("").astype(str).tolist(
    ) if "tipo" in prov_df.columns else [""] * len(prov_df)
    nomes = prov_df["nome"].fillna("").astype(str).tolist(
    ) if "nome" in prov_df.columns else [""] * len(prov_df)
    result = {}
    for i, row in enumerate(prov_df.itertuples()):
        t = tipos[i].strip().lower()
        n = nomes[i].strip().lower()
        result[row.id] = "Sprint" if (
            t == "sprint" or "sprint" in n) else "Normal"
    return result


def _calcular_pontos_aposta(
        aposta: pd.Series,
        res: dict,
        tipo: str,
        temporada: str,
        abandonos: set) -> float:
    """Calcula os pontos de uma única aposta com base no resultado da prova."""
    regras = get_regras_aplicaveis(temporada, tipo)

    if tipo == "Sprint":
        pontos_tabela = regras.get("pontos_sprint_posicoes") or regras.get(
            "pontos_posicoes") or PONTOS_SPRINT
    else:
        pontos_tabela = regras.get("pontos_posicoes") or PONTOS_F1_NORMAL

    n_posicoes = len(pontos_tabela)
    bonus_11 = regras.get("pontos_11_colocado", 25)

    pilotos = [p.strip() for p in aposta["pilotos"].split(",")]
    fichas = list(map(int, aposta["fichas"].split(",")))
    piloto_11 = aposta["piloto_11"]
    automatica = int(aposta.get("automatica", 0))

    piloto_para_pos = {str(v).strip(): int(k) for k, v in res.items()}

    pt: float = 0.0
    for i, piloto in enumerate(pilotos):
        ficha = fichas[i] if i < len(fichas) else 0
        pos_real = piloto_para_pos.get(piloto)
        if pos_real is not None and 1 <= pos_real <= n_posicoes:
            pt += ficha * pontos_tabela[pos_real - 1]

    if piloto_11 == res.get(11, ""):
        pt += bonus_11

    if regras.get("penalidade_abandono") and abandonos:
        num_aband = sum(1 for p in pilotos if p in abandonos)
        pt -= regras.get("pontos_penalidade", 0) * num_aband

    if tipo == "Sprint" and regras.get("pontos_dobrada"):
        pt *= 2

    if automatica >= 2:
        fator = max(
            0.0,
            1 -
            float(
                regras.get(
                    "penalidade_auto_percent",
                    20)) /
            100)
        pt = round(pt * fator, 2)

    return pt


# ---------------------------------------------------------------------------
# API pública — cálculo em lote
# ---------------------------------------------------------------------------

def calcular_pontuacao_lote(
    ap_df: pd.DataFrame,
    res_df: pd.DataFrame,
    prov_df: pd.DataFrame,
    temporada_descarte: Optional[str] = None,
) -> list:
    """Calcula pontuação para todas as apostas do DataFrame.

    Retorna lista de pontos na mesma ordem que as linhas de *ap_df*.
    Linhas sem resultado correspondente recebem None.
    """
    year_fallback = str(datetime.now().year)
    ap_df = normalizar_apostas(ap_df)
    prov_df = normalizar_provas(prov_df, year_fallback)

    ress_map, abandonos_map = _construir_mapa_resultados(res_df)
    tipos_prova = _construir_tipos_prova(prov_df)
    temporadas_prova = dict(zip(prov_df["id"], prov_df["temporada"]))

    pontos = []
    for _, aposta in ap_df.iterrows():
        prova_id = aposta["prova_id"]
        if prova_id not in ress_map:
            pontos.append(None)
            continue

        temporada = resolver_temporada_aposta(
            aposta, temporadas_prova, year_fallback)
        tipo = tipos_prova.get(prova_id, "Normal")

        try:
            pt = _calcular_pontos_aposta(
                aposta,
                ress_map[prova_id],
                tipo,
                temporada,
                abandonos_map.get(prova_id, set()),
            )
            pontos.append(pt)
        except Exception:
            logger.exception(
                "Erro ao calcular pontuação para usuario_id=%s prova_id=%s",
                aposta.get("usuario_id"),
                prova_id,
            )
            pontos.append(None)

    return pontos


# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------

def salvar_classificacao_prova(
        p_id: int,
        df_c: pd.DataFrame,
        temp: Optional[str] = None) -> None:
    """Salva a classificação de uma prova no banco, compatível com schemas antigo e novo."""
    if temp is None:
        temp = str(datetime.now().year)

    with db_connect() as conn:
        c = conn.cursor()
        usa_temporada = has_coluna_temporada_tabela(
            conn, "posicoes_participantes")

        if usa_temporada:
            c.execute(
                "DELETE FROM posicoes_participantes WHERE prova_id=%s AND temporada=%s",
                (p_id, temp),
            )
        else:
            c.execute(
                "DELETE FROM posicoes_participantes WHERE prova_id=%s", (p_id,))

        for _, r in df_c.iterrows():
            if usa_temporada:
                c.execute(
                    "INSERT INTO posicoes_participantes (prova_id, usuario_id, posicao, pontos, temporada)"
                    " VALUES (%s,%s,%s,%s,%s)", (p_id, int(
                        r["usuario_id"]), int(
                        r["posicao"]), float(
                        r["pontos"]), temp), )
            else:
                c.execute(
                    "INSERT INTO posicoes_participantes (prova_id, usuario_id, posicao, pontos)"
                    " VALUES (%s,%s,%s,%s)", (p_id, int(
                        r["usuario_id"]), int(
                        r["posicao"]), float(
                        r["pontos"])), )
        conn.commit()


# ---------------------------------------------------------------------------
# Orquestração: atualizar_classificacoes_todas_as_provas
# (decomposta em funções nomeadas com responsabilidade única)
# ---------------------------------------------------------------------------

def _carregar_dados_base(conn,
                         temporada: Optional[str]) -> tuple[pd.DataFrame,
                                                            pd.DataFrame,
                                                            pd.DataFrame,
                                                            pd.DataFrame]:
    """Carrega e filtra os DataFrames base do banco de dados."""
    usrs = cast(
        pd.DataFrame,
        _fetch_df(
            conn,
            "SELECT id FROM usuarios WHERE lower(trim(coalesce(status, ''))) = 'ativo'"),
    )
    provs = cast(
        pd.DataFrame,
        _fetch_df(
            conn,
            "SELECT id, nome, data, tipo, temporada FROM provas"))
    apts = cast(
        pd.DataFrame,
        _fetch_df(
            conn,
            "SELECT usuario_id, prova_id, data_envio, pilotos, fichas, piloto_11, automatica, temporada FROM apostas"),
    )
    ress = cast(
        pd.DataFrame,
        _fetch_df(
            conn,
            "SELECT prova_id, posicoes, abandono_pilotos FROM resultados"))

    if temporada and "temporada" in provs.columns:
        provs = provs[provs["temporada"] == temporada]

    return usrs, provs, apts, ress


def _mapear_primeira_prova_por_temporada(
        provs: pd.DataFrame) -> dict[str, int]:
    """Retorna {temporada: prova_id} com a primeira prova de cada temporada."""
    if provs.empty or "data" not in provs.columns:
        return {}

    provs_dt = normalizar_provas(provs.copy())
    provs_dt["__data_dt"] = pd.to_datetime(provs_dt["data"], errors="coerce")

    primeira_prova: dict[str, int] = {}
    for temp_val, grp in provs_dt.groupby("temporada"):
        grp_sorted = cast(pd.DataFrame, grp).sort_values("__data_dt")
        if not grp_sorted.empty:
            primeira_prova[str(temp_val)] = int(grp_sorted.iloc[0]["id"])

    return primeira_prova


def _calcular_pontos_usuario(
    u: pd.Series,
    aps: pd.DataFrame,
    ress: pd.DataFrame,
    provs: pd.DataFrame,
    prova_id: int,
    temporada_prova: str,
    piloto_11_real: str,
    primeira_prova_por_temp: dict,
) -> dict:
    """Calcula os pontos de um usuário para uma prova específica.

    Retorna dicionário com usuario_id, pontos, data_envio, acerto_11.
    """
    ap = aps[aps["usuario_id"] == u["id"]]
    is_primeira = str(prova_id) == str(
        primeira_prova_por_temp.get(
            str(temporada_prova)))

    if ap.empty:
        return {
            "usuario_id": u["id"],
            "pontos": 0,
            "data_envio": None,
            "acerto_11": 0,
            "_sem_aposta_primeira_prova": is_primeira,
        }

    try:
        p_list = calcular_pontuacao_lote(ap, ress, provs)
        pontos_val = sum(p for p in p_list if p is not None)
    except Exception:
        logger.exception(
            "Erro ao calcular pontuação lote usuario_id=%s prova_id=%s",
            u["id"],
            prova_id)
        pontos_val = 0

    data_envio = ap.iloc[0].get("data_envio", None)
    acerto_11 = int(ap.iloc[0]["piloto_11"] == piloto_11_real)

    return {
        "usuario_id": u["id"],
        "pontos": pontos_val,
        "data_envio": data_envio,
        "acerto_11": acerto_11,
        "_sem_aposta_primeira_prova": False,
    }


def _aplicar_regra_primeira_prova(tab: list[dict]) -> None:
    """Aplica a regra de pior pontuador * 0.85 para entrantes sem aposta na 1ª prova.

    Modifica *tab* in-place.
    """
    sem_aposta_ids = {int(t["usuario_id"])
                      for t in tab if t.get("_sem_aposta_primeira_prova")}
    if not sem_aposta_ids:
        return

    try:
        pontos_validos = [
            t["pontos"]
            for t in tab
            if t["pontos"] is not None and int(t["usuario_id"]) not in sem_aposta_ids
        ]
        pior = min(pontos_validos) if pontos_validos else 0
    except Exception:
        logger.exception(
            "Erro ao calcular pior pontuador para regra de primeira prova")
        pior = 0

    for t in tab:
        if int(t["usuario_id"]) in sem_aposta_ids:
            t["pontos"] = round(pior * 0.85, 2)


def _ordenar_e_posicionar(tab: list[dict]) -> pd.DataFrame:
    """Converte a lista de resultados em DataFrame ordenado com posição calculada."""
    df = pd.DataFrame(tab)
    df.drop(
        columns=[
            c for c in ["_sem_aposta_primeira_prova"] if c in df.columns],
        inplace=True)
    df["data_envio"] = pd.to_datetime(df["data_envio"], errors="coerce")
    df = df.sort_values(
        by=["pontos", "acerto_11", "data_envio"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    df["posicao"] = df.index + 1
    return df


def _processar_prova(
    pr: pd.Series,
    usrs: pd.DataFrame,
    apts: pd.DataFrame,
    ress: pd.DataFrame,
    provs: pd.DataFrame,
    primeira_prova_por_temp: dict,
) -> None:
    """Calcula e persiste a classificação completa de uma prova."""
    pid = pr["id"]
    if pid not in ress["prova_id"].values:
        return

    temporada_prova = str(pr.get("temporada", datetime.now().year))
    aps = apts[apts["prova_id"] == pid]
    if "temporada" in aps.columns:
        aps = aps[(aps["temporada"] == temporada_prova)
                  | (aps["temporada"].isna())]
    if aps.empty:
        return

    try:
        res_row = ress[ress["prova_id"] == pid].iloc[0]
        res_p = ast.literal_eval(res_row["posicoes"])
    except Exception:
        logger.exception("Erro ao parsear posições da prova_id=%s", pid)
        return

    piloto_11_real = res_p.get(11, "")

    tab = [
        _calcular_pontos_usuario(
            u,
            aps,
            ress,
            provs,
            pid,
            temporada_prova,
            piloto_11_real,
            primeira_prova_por_temp) for _,
        u in usrs.iterrows()]

    _aplicar_regra_primeira_prova(tab)
    df = _ordenar_e_posicionar(tab)
    salvar_classificacao_prova(pid, df, temporada_prova)


def atualizar_classificacoes_todas_as_provas(
        temporada: Optional[str] = None) -> None:
    """Recalcula e persiste a classificação de todas as provas com resultado.

    Fluxo:
    1. Carrega dados base (usuários, provas, apostas, resultados).
    2. Mapeia a primeira prova por temporada (para regra do novato).
    3. Itera provas e delega o processamento para _processar_prova().
    """
    with db_connect() as conn:
        usrs, provs, apts, ress = _carregar_dados_base(conn, temporada)

    if provs.empty:
        logger.warning("Nenhuma prova encontrada para temporada=%s", temporada)
        return

    provs = normalizar_provas(provs)
    primeira_prova_por_temp = _mapear_primeira_prova_por_temporada(provs)

    for _, pr in provs.iterrows():
        try:
            _processar_prova(
                pr,
                usrs,
                apts,
                ress,
                provs,
                primeira_prova_por_temp)
        except Exception:
            logger.exception("Erro ao processar prova_id=%s", pr["id"])


__all__ = [
    "_parse_datetime_sp",
    "calcular_pontuacao_lote",
    "salvar_classificacao_prova",
    "atualizar_classificacoes_todas_as_provas",
]
