"""Testes unitários para services/bets_scoring.py.

Cobertura:
    - calcular_pontuacao_lote: pontuação normal, sprint, bônus 11º, penalidade
      abandono, dobrada sprint, penalidade automática, sem resultado, fichas
    - salvar_classificacao_prova: delegado a test_integration (requer banco)
    - _calcular_pontos_aposta (indireto via calcular_pontuacao_lote)
    - _mapear_primeira_prova_por_temporada
    - _aplicar_penalidade_primeira_prova
    - _ordenar_e_classificar

Execute:
    pytest tests/test_bets_scoring.py -v
"""
from __future__ import annotations


import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Stubs para dependências externas (banco de dados / regras)
# ---------------------------------------------------------------------------

REGRAS_PADRAO = {
    "pontos_posicoes": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],
    "pontos_sprint_posicoes": [8, 7, 6, 5, 4, 3, 2, 1],
    "pontos_11_colocado": 25,
    "penalidade_abandono": False,
    "pontos_penalidade": 0,
    "pontos_dobrada": False,
    "penalidade_auto_percent": 20,
    "mesma_equipe": False,
}


def _regras_mock(temporada=None, tipo=None):
    return REGRAS_PADRAO.copy()


# ---------------------------------------------------------------------------
# Fixtures de DataFrames reutilizáveis
# ---------------------------------------------------------------------------

@pytest.fixture()
def prova_normal_df():
    return pd.DataFrame([{"id": 1,
                          "nome": "GP Brasil",
                          "data": "2025-11-02",
                          "tipo": "Normal",
                          "temporada": "2025"}])


@pytest.fixture()
def prova_sprint_df():
    return pd.DataFrame([{"id": 2,
                          "nome": "GP Sprint",
                          "data": "2025-11-01",
                          "tipo": "Sprint",
                          "temporada": "2025"}])


@pytest.fixture()
def resultado_normal_df():
    posicoes = {1: "Hamilton", 2: "Verstappen", 3: "Leclerc", 4: "Sainz",
                5: "Norris", 6: "Russell", 7: "Piastri", 8: "Alonso",
                9: "Stroll", 10: "Perez", 11: "Bottas"}
    return pd.DataFrame(
        [{"prova_id": 1, "posicoes": str(posicoes), "abandono_pilotos": ""}])


@pytest.fixture()
def resultado_sprint_df():
    posicoes = {1: "Verstappen", 2: "Hamilton", 3: "Leclerc", 4: "Sainz",
                5: "Norris", 6: "Russell", 7: "Piastri", 8: "Alonso",
                11: "Bottas"}
    return pd.DataFrame(
        [{"prova_id": 2, "posicoes": str(posicoes), "abandono_pilotos": ""}])


def _aposta_df(prova_id: int, pilotos: list, fichas: list, piloto_11: str,
               automatica: int = 0, temporada: str = "2025") -> pd.DataFrame:
    return pd.DataFrame([{
        "usuario_id": 1,
        "prova_id": prova_id,
        "pilotos": ",".join(pilotos),
        "fichas": ",".join(str(f) for f in fichas),
        "piloto_11": piloto_11,
        "automatica": automatica,
        "data_envio": "2025-11-01 10:00:00",
        "temporada": temporada,
    }])


# ---------------------------------------------------------------------------
# Importação do módulo sob teste (com patch no módulo de regras)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_regras(monkeypatch):
    """Substitui get_regras_aplicaveis para não depender do banco."""
    monkeypatch.setattr(
        "services.bets_scoring.get_regras_aplicaveis",
        _regras_mock,
    )


# ---------------------------------------------------------------------------
# Testes de calcular_pontuacao_lote
# ---------------------------------------------------------------------------

class TestCalcularPontuacaoLote:

    def test_prova_sem_resultado_retorna_none(self, prova_normal_df):
        """Aposta para prova sem resultado deve retornar None na lista."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap = _aposta_df(1, ["Hamilton", "Verstappen",
                        "Leclerc"], [7, 5, 3], "Bottas")
        res_vazio = pd.DataFrame(
            columns=[
                "prova_id",
                "posicoes",
                "abandono_pilotos"])
        resultado = calcular_pontuacao_lote(ap, res_vazio, prova_normal_df)
        assert resultado == [None]

    def test_pontuacao_basica_corrida_normal(
            self, prova_normal_df, resultado_normal_df):
        """Hamilton 1º (25pts) × 7=175 | Verstappen 2º (18pts) × 5=90 | Leclerc 3º (15pts) × 3=45 → 310."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap = _aposta_df(1, ["Hamilton", "Verstappen",
                        "Leclerc"], [7, 5, 3], "Stroll")
        resultado = calcular_pontuacao_lote(
            ap, resultado_normal_df, prova_normal_df)
        assert resultado == [310.0]

    def test_bonus_11o_colocado_aplicado(
            self, prova_normal_df, resultado_normal_df):
        """Bônus de 25 pts adicionado quando piloto_11 coincide com 11º real (Bottas)."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap = _aposta_df(1, ["Hamilton", "Verstappen",
                        "Leclerc"], [7, 5, 3], "Bottas")
        resultado = calcular_pontuacao_lote(
            ap, resultado_normal_df, prova_normal_df)
        assert resultado == [335.0]  # 310 + 25

    def test_bonus_11o_nao_aplicado_quando_errado(
            self, prova_normal_df, resultado_normal_df):
        """Bônus NÃO adicionado quando piloto_11 não coincide com 11º real."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap = _aposta_df(1, ["Hamilton", "Verstappen",
                        "Leclerc"], [7, 5, 3], "Perez")
        resultado = calcular_pontuacao_lote(
            ap, resultado_normal_df, prova_normal_df)
        assert resultado == [310.0]

    def test_piloto_fora_top10_nao_pontua(
            self, prova_normal_df, resultado_normal_df):
        """Piloto fora do top-10 não contribui para a pontuação."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap = _aposta_df(1, ["Hamilton", "Bottas", "Leclerc"], [
                        7, 5, 3], "Stroll")
        resultado = calcular_pontuacao_lote(
            ap, resultado_normal_df, prova_normal_df)
        # Hamilton 1º × 7=175 | Bottas = 0 | Leclerc 3º × 3=45 → 220
        assert resultado == [220.0]

    def test_penalidade_abandono_aplicada(self, prova_normal_df, monkeypatch):
        """Penalidade por abandono deduz pontos_penalidade por piloto abandonado apostado."""
        from services.bets_scoring import calcular_pontuacao_lote

        regras = {
            **REGRAS_PADRAO,
            "penalidade_abandono": True,
            "pontos_penalidade": 10}
        monkeypatch.setattr(
            "services.bets_scoring.get_regras_aplicaveis",
            lambda *a,
            **k: regras)

        posicoes = {1: "Hamilton", 2: "Verstappen", 3: "Leclerc", 11: "Bottas"}
        res_df = pd.DataFrame(
            [{"prova_id": 1, "posicoes": str(posicoes), "abandono_pilotos": "Verstappen"}])
        ap = _aposta_df(1, ["Hamilton", "Verstappen",
                        "Leclerc"], [7, 5, 3], "Bottas")
        resultado = calcular_pontuacao_lote(ap, res_df, prova_normal_df)
        # 175 + 90 + 45 + 25(bônus 11) - 10(penalidade Verstappen) = 325
        assert resultado == [325.0]

    def test_dobrada_sprint_dobra_pontuacao(
            self,
            prova_sprint_df,
            resultado_sprint_df,
            monkeypatch):
        """pontos_dobrada=True deve duplicar a pontuação da prova sprint."""
        from services.bets_scoring import calcular_pontuacao_lote

        regras = {**REGRAS_PADRAO, "pontos_dobrada": True}
        monkeypatch.setattr(
            "services.bets_scoring.get_regras_aplicaveis",
            lambda *a,
            **k: regras)

        ap = _aposta_df(2, ["Verstappen", "Hamilton",
                        "Leclerc"], [7, 5, 3], "Stroll")
        resultado = calcular_pontuacao_lote(
            ap, resultado_sprint_df, prova_sprint_df)
        # Verstappen 1º=8 × 7=56 | Hamilton 2º=7 × 5=35 | Leclerc 3º=6 × 3=18 →
        # 109 × 2 = 218
        assert resultado == [218.0]

    def test_penalidade_aposta_automatica_segunda_geracao(
            self, prova_normal_df, resultado_normal_df):
        """Aposta automática de 2ª geração recebe redução de 20%."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap = _aposta_df(1, ["Hamilton", "Verstappen", "Leclerc"], [
                        7, 5, 3], "Stroll", automatica=2)
        resultado = calcular_pontuacao_lote(
            ap, resultado_normal_df, prova_normal_df)
        assert resultado == [248.0]  # 310 * 0.80

    def test_aposta_automatica_primeira_geracao_sem_penalidade(
            self, prova_normal_df, resultado_normal_df):
        """Aposta automática de 1ª geração NÃO sofre penalidade percentual."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap = _aposta_df(1, ["Hamilton", "Verstappen", "Leclerc"], [
                        7, 5, 3], "Stroll", automatica=1)
        resultado = calcular_pontuacao_lote(
            ap, resultado_normal_df, prova_normal_df)
        assert resultado == [310.0]

    def test_lote_multiplas_apostas(
            self,
            prova_normal_df,
            resultado_normal_df):
        """Lote com duas apostas retorna lista com dois elementos independentes."""
        from services.bets_scoring import calcular_pontuacao_lote

        ap1 = _aposta_df(1, ["Hamilton", "Verstappen",
                         "Leclerc"], [7, 5, 3], "Stroll")
        ap2 = _aposta_df(1, ["Norris", "Russell", "Piastri"], [
                         5, 5, 5], "Stroll")
        ap2["usuario_id"] = 2
        ap = pd.concat([ap1, ap2], ignore_index=True)
        resultado = calcular_pontuacao_lote(
            ap, resultado_normal_df, prova_normal_df)
        assert len(resultado) == 2
        # Norris 5º=10 × 5=50 | Russell 6º=8 × 5=40 | Piastri 7º=6 × 5=30 → 120
        assert resultado[1] == 120.0


# ---------------------------------------------------------------------------
# Testes de _mapear_primeira_prova_por_temporada
# ---------------------------------------------------------------------------

class TestMapearPrimeiraPorTemporada:

    def test_retorna_prova_mais_antiga_por_temporada(self):
        from services.bets_scoring import _mapear_primeira_prova_por_temporada

        provs = pd.DataFrame([{"id": 10,
                               "nome": "GP A",
                               "data": "2025-03-15",
                               "tipo": "Normal",
                               "temporada": "2025"},
                              {"id": 11,
                               "nome": "GP B",
                               "data": "2025-04-20",
                               "tipo": "Normal",
                               "temporada": "2025"},
                              {"id": 20,
                               "nome": "GP C",
                               "data": "2024-11-20",
                               "tipo": "Normal",
                               "temporada": "2024"},
                              ])
        resultado = _mapear_primeira_prova_por_temporada(provs)
        assert resultado["2025"] == 10
        assert resultado["2024"] == 20

    def test_df_vazio_retorna_dict_vazio(self):
        from services.bets_scoring import _mapear_primeira_prova_por_temporada

        assert _mapear_primeira_prova_por_temporada(pd.DataFrame()) == {}

    def test_sem_coluna_data_retorna_dict_vazio(self):
        from services.bets_scoring import _mapear_primeira_prova_por_temporada

        provs = pd.DataFrame(
            [{"id": 1, "nome": "GP X", "tipo": "Normal", "temporada": "2025"}])
        resultado = _mapear_primeira_prova_por_temporada(provs)
        assert resultado == {}


# ---------------------------------------------------------------------------
# Testes de _aplicar_regra_primeira_prova
# ---------------------------------------------------------------------------

class TestAplicarRegraPrimeiraProva:

    def test_usuario_sem_aposta_recebe_pior_pontuador_x085(self):
        from services.bets_scoring import _aplicar_regra_primeira_prova

        tab = [
            {"usuario_id": 1, "pontos": 200.0, "_sem_aposta_primeira_prova": False},
            {"usuario_id": 2, "pontos": 150.0, "_sem_aposta_primeira_prova": False},
            {"usuario_id": 3, "pontos": 0, "_sem_aposta_primeira_prova": True},
        ]
        _aplicar_regra_primeira_prova(tab)
        assert tab[2]["pontos"] == round(150.0 * 0.85, 2)

    def test_sem_usuarios_sem_aposta_nao_altera_tabela(self):
        from services.bets_scoring import _aplicar_regra_primeira_prova

        tab = [
            {"usuario_id": 1, "pontos": 200.0, "_sem_aposta_primeira_prova": False},
            {"usuario_id": 2, "pontos": 150.0, "_sem_aposta_primeira_prova": False},
        ]
        original = [t["pontos"] for t in tab]
        _aplicar_regra_primeira_prova(tab)
        assert [t["pontos"] for t in tab] == original


# ---------------------------------------------------------------------------
# Testes de _ordenar_e_posicionar
# ---------------------------------------------------------------------------

class TestOrdenarEPosicionar:

    def test_ordena_por_pontos_decrescente(self):
        from services.bets_scoring import _ordenar_e_posicionar

        tab = [{"usuario_id": 1,
                "pontos": 100.0,
                "acerto_11": 0,
                "data_envio": "2025-11-01 10:00:00"},
               {"usuario_id": 2,
                "pontos": 200.0,
                "acerto_11": 0,
                "data_envio": "2025-11-01 09:00:00"},
               {"usuario_id": 3,
                "pontos": 150.0,
                "acerto_11": 0,
                "data_envio": "2025-11-01 11:00:00"},
               ]
        df = _ordenar_e_posicionar(tab)
        assert list(df["usuario_id"]) == [2, 3, 1]
        assert list(df["posicao"]) == [1, 2, 3]

    def test_empate_desempatado_por_acerto_11(self):
        from services.bets_scoring import _ordenar_e_posicionar

        tab = [{"usuario_id": 1,
                "pontos": 100.0,
                "acerto_11": 0,
                "data_envio": "2025-11-01 10:00:00"},
               {"usuario_id": 2,
                "pontos": 100.0,
                "acerto_11": 1,
                "data_envio": "2025-11-01 09:00:00"},
               ]
        df = _ordenar_e_posicionar(tab)
        assert df.iloc[0]["usuario_id"] == 2

    def test_empate_desempatado_por_data_envio_mais_antiga(self):
        from services.bets_scoring import _ordenar_e_posicionar

        tab = [{"usuario_id": 1,
                "pontos": 100.0,
                "acerto_11": 1,
                "data_envio": "2025-11-01 12:00:00"},
               {"usuario_id": 2,
                "pontos": 100.0,
                "acerto_11": 1,
                "data_envio": "2025-11-01 09:00:00"},
               ]
        df = _ordenar_e_posicionar(tab)
        assert df.iloc[0]["usuario_id"] == 2
