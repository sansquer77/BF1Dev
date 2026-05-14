"""Validações e ajustes de regras de apostas."""

from __future__ import annotations

import random
from zoneinfo import ZoneInfo

import pandas as pd

from utils.datetime_utils import SAO_PAULO_TZ, now_sao_paulo, parse_datetime_sao_paulo


def _parse_datetime_sp(date_str: str, time_str: str):
    return parse_datetime_sao_paulo(date_str, time_str)


def pode_fazer_aposta(
        prova_ou_data,
        horario_prova_str: str | None = None,
        horario_usuario=None):
    """Verifica se ainda é possível fazer aposta para a prova.

    Aceita dict com chaves ``data``/``horario`` ou strings separadas (forma legada).
    Retorna ``(bool, mensagem, horario_limite_sp)``.
    """
    try:
        if isinstance(prova_ou_data, dict):
            data_str = str(prova_ou_data.get("data", "")).strip()
            horario_str = str(prova_ou_data.get("horario", "00:00:00")).strip()
        else:
            data_str = str(prova_ou_data).strip()
            horario_str = str(horario_prova_str or "00:00:00").strip()

        horario_limite_sp = _parse_datetime_sp(data_str, horario_str)

        if horario_usuario is None:
            horario_usuario = now_sao_paulo()
        elif not horario_usuario.tzinfo:
            horario_usuario = horario_usuario.replace(tzinfo=SAO_PAULO_TZ)

        horario_usuario_utc = horario_usuario.astimezone(ZoneInfo("UTC"))
        horario_limite_utc = horario_limite_sp.astimezone(ZoneInfo("UTC"))

        pode = horario_usuario_utc <= horario_limite_utc
        mensagem = (
            f"Aposta {
                'permitida' if pode else 'bloqueada'} " f"(Horário limite SP: {
                horario_limite_sp.strftime('%d/%m/%Y %H:%M:%S')})")
        return pode, mensagem, horario_limite_sp
    except Exception as e:
        return False, f"Erro ao validar horário: {str(e)}", None


def validar_composicao_aposta(
    pilotos: list[str],
    fichas: list[int],
    piloto_11: str,
    pilotos_df: pd.DataFrame | None = None,
    regras: dict | None = None,
) -> tuple[bool, str]:
    """Valida a composição de uma aposta, retornando (ok, mensagem).

    Verifica: lista não vazia, tamanhos compatíveis, sem duplicatas,
    fichas sem negativos, piloto_11 preenchido e fora da lista principal.
    """
    if not pilotos:
        return False, "A lista de pilotos não pode estar vazia."

    if len(pilotos) != len(fichas):
        return False, (f"Número de pilotos ({
            len(pilotos)}) diferente do número de fichas ({
            len(fichas)}).")

    duplicados = [p for p in set(pilotos) if pilotos.count(p) > 1]
    if duplicados:
        return False, f"Pilotos duplicados: {', '.join(duplicados)}."

    negativos = [str(f) for f in fichas if int(f) < 0]
    if negativos:
        return False, f"Fichas com valor negativo: {', '.join(negativos)}."

    if not str(piloto_11).strip():
        return False, "O 11º colocado (piloto_11) é obrigatório."

    if piloto_11 in pilotos:
        return False, f"O piloto '{piloto_11}' não pode estar na aposta e como 11º."

    if regras is not None and pilotos_df is not None:
        ok = _aposta_valida_regras(
            pilotos, [
                int(f) for f in fichas], piloto_11, pilotos_df, regras)
        if not ok:
            return False, "A aposta viola as regras configuradas para esta temporada."

    return True, ""


def aposta_eh_automatica(aposta: dict) -> bool:
    """Retorna True se a aposta foi gerada automaticamente (flag automatica != 0)."""
    return bool(int(aposta.get("automatica", 0)))


def calcular_pior_pontuador(pontos: list) -> float:
    """Retorna a menor pontuação válida da lista; 0.0 se vazia ou toda None."""
    validos = [p for p in pontos if p is not None]
    return float(min(validos)) if validos else 0.0


def _aposta_valida_regras(
    pilotos_sel: list[str],
    fichas_sel: list[int],
    piloto_11: str,
    pilotos_df: pd.DataFrame,
    regras: dict,
) -> bool:
    """Validação completa das regras configuradas (uso interno)."""
    if not pilotos_sel or not fichas_sel or not piloto_11:
        return False

    min_pilotos = int(regras.get("qtd_minima_pilotos")
                      or regras.get("min_pilotos", 3))
    qtd_fichas = int(regras.get("quantidade_fichas", 15))
    fichas_max = int(regras.get("fichas_por_piloto", qtd_fichas))
    permite_mesma_equipe = bool(regras.get("mesma_equipe", False))

    if len(pilotos_sel) < min_pilotos:
        return False
    if len(pilotos_sel) != len(fichas_sel):
        return False
    if len(set(pilotos_sel)) != len(pilotos_sel):
        return False
    if sum(int(f) for f in fichas_sel) != qtd_fichas:
        return False
    if fichas_sel and max(int(f) for f in fichas_sel) > fichas_max:
        return False
    if piloto_11 in pilotos_sel:
        return False

    pilotos_disponiveis = set(pilotos_df["nome"].astype(
        str).tolist()) if not pilotos_df.empty else set()
    if pilotos_disponiveis and any(
            str(p) not in pilotos_disponiveis for p in pilotos_sel):
        return False
    if pilotos_disponiveis and str(piloto_11) not in pilotos_disponiveis:
        return False

    if not permite_mesma_equipe and not pilotos_df.empty and "equipe" in pilotos_df.columns:
        mapa_eq: dict[str, str] = {str(nome): str(eq) for nome, eq in zip(
            pilotos_df["nome"].astype(str), pilotos_df["equipe"].astype(str))}
        equipes = [mapa_eq.get(str(p), "") for p in pilotos_sel]
        equipes_validas = [e for e in equipes if e]
        if len(set(equipes_validas)) < len(equipes_validas):
            return False

    return True


def ajustar_aposta_para_regras(
    pilotos: list[str],
    fichas: list[int],
    regras: dict,
    pilotos_df: pd.DataFrame,
) -> tuple[list[str], list[int]]:
    """Ajusta pilotos e fichas para que a aposta respeite as regras configuradas."""
    if not pilotos:
        return [], []
    qtd_fichas = int(regras.get("quantidade_fichas", 15))
    fichas_max = int(regras.get("fichas_por_piloto", qtd_fichas))
    min_pilotos = int(regras.get("qtd_minima_pilotos")
                      or regras.get("min_pilotos", 3))

    n = min(len(pilotos), len(fichas))
    pilotos = [p.strip() for p in pilotos[:n]]
    fichas = [int(x) for x in fichas[:n]]
    fichas = [max(0, x) for x in fichas]

    if len(pilotos) < min_pilotos:
        todos_pilotos = pilotos_df["nome"].tolist()
        candidatos = [p for p in todos_pilotos if p not in set(pilotos)]
        safety = 10000
        while len(pilotos) < min_pilotos and candidatos and safety > 0:
            safety -= 1
            novo = random.choice(candidatos)
            candidatos.remove(novo)
            pilotos.append(novo)
            fichas.append(0)
        if len(pilotos) < min_pilotos:
            return [], []

    fichas = [min(x, fichas_max) for x in fichas]
    soma = sum(fichas)
    if soma > qtd_fichas:
        for _ in range(soma - qtd_fichas):
            idx_max = max(range(len(fichas)), key=lambda i: fichas[i])
            if fichas[idx_max] > 0:
                fichas[idx_max] -= 1
    elif soma < qtd_fichas:
        faltam = qtd_fichas - soma
        safety = 100000
        while faltam > 0 and safety > 0:
            safety -= 1
            idx = random.randint(0, len(fichas) - 1)
            if fichas[idx] < fichas_max:
                fichas[idx] += 1
                faltam -= 1
            if safety % 1000 == 0 and faltam > 0:
                todos_pilotos = pilotos_df["nome"].tolist()
                candidatos = [
                    p for p in todos_pilotos if p not in set(pilotos)]
                if candidatos:
                    novo = random.choice(candidatos)
                    pilotos.append(novo)
                    fichas.append(0)

    if sum(fichas) != qtd_fichas or len(pilotos) < min_pilotos:
        return [], []
    return pilotos, fichas


__all__ = [
    "pode_fazer_aposta",
    "validar_composicao_aposta",
    "aposta_eh_automatica",
    "calcular_pior_pontuador",
    "_aposta_valida_regras",
    "ajustar_aposta_para_regras",
]
