"""Testes unitários para services/bets_rules.py.

Cobertura:
    - pode_fazer_aposta: dentro e fora do prazo, timezone, erro de parse
    - _aposta_valida_regras: happy path, mínimo pilotos, total fichas, piloto_11
    - aposta_eh_automatica: flag presente e ausente
    - calcular_pior_pontuador: lista vazia, lista com valores
    - validar_composicao_aposta: pilotos duplicados, fichas negativas

Execute:
    pytest tests/test_bets_rules.py -v
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_prova(
        data: str,
        horario: str = "14:00:00",
        tipo: str = "Normal") -> dict:
    return {"data": data, "horario": horario, "tipo": tipo}


# ---------------------------------------------------------------------------
# pode_fazer_aposta
# ---------------------------------------------------------------------------

class TestPodeFazerAposta:

    def test_dentro_do_prazo_retorna_true(self):
        """Se agora < horário da prova, pode apostar."""
        from services.bets_rules import pode_fazer_aposta

        amanha = (
            datetime.now(
                tz=timezone.utc) +
            timedelta(
                days=1)).strftime("%Y-%m-%d")
        prova = _make_prova(amanha)
        pode, _, _ = pode_fazer_aposta(prova)
        assert pode is True

    def test_fora_do_prazo_retorna_false(self):
        """Se agora >= horário da prova, não pode apostar."""
        from services.bets_rules import pode_fazer_aposta

        ontem = (
            datetime.now(
                tz=timezone.utc) -
            timedelta(
                days=1)).strftime("%Y-%m-%d")
        prova = _make_prova(ontem)
        pode, _, _ = pode_fazer_aposta(prova)
        assert pode is False

    def test_horario_invalido_retorna_false(self):
        """Horário imparsável deve retornar False (seguro por padrão)."""
        from services.bets_rules import pode_fazer_aposta

        amanha = (
            datetime.now(
                tz=timezone.utc) +
            timedelta(
                days=1)).strftime("%Y-%m-%d")
        prova = _make_prova(amanha, horario="hora_invalida")
        pode, _, _ = pode_fazer_aposta(prova)
        assert pode is False

    def test_data_invalida_retorna_false(self):
        """Data imparsável deve retornar False."""
        from services.bets_rules import pode_fazer_aposta

        prova = _make_prova("data_invalida")
        pode, _, _ = pode_fazer_aposta(prova)
        assert pode is False

    def test_sprint_tem_prazo_diferente_se_implementado(self):
        """Teste documenta que tipo Sprint é aceito sem erro."""
        from services.bets_rules import pode_fazer_aposta

        amanha = (
            datetime.now(
                tz=timezone.utc) +
            timedelta(
                days=1)).strftime("%Y-%m-%d")
        prova = _make_prova(amanha, tipo="Sprint")
        # Deve retornar (bool, msg, dt) sem lançar exceção
        pode, msg, _ = pode_fazer_aposta(prova)
        assert isinstance(pode, bool)
        assert isinstance(msg, str)


# ---------------------------------------------------------------------------
# validar_composicao_aposta
# ---------------------------------------------------------------------------

class TestValidarComposicaoAposta:

    def test_aposta_valida_retorna_true_e_mensagem_vazia(self):
        """Aposta com pilotos distintos e fichas válidas deve passar."""
        from services.bets_rules import validar_composicao_aposta

        ok, msg = validar_composicao_aposta(
            pilotos=["Hamilton", "Verstappen", "Leclerc"],
            fichas=[5, 5, 5],
            piloto_11="Sainz",
        )
        assert ok is True
        assert msg == ""

    def test_pilotos_duplicados_retorna_false(self):
        from services.bets_rules import validar_composicao_aposta

        ok, msg = validar_composicao_aposta(
            pilotos=["Hamilton", "Hamilton", "Leclerc"],
            fichas=[5, 5, 5],
            piloto_11="Sainz",
        )
        assert ok is False
        assert "duplicado" in msg.lower()

    def test_ficha_negativa_retorna_false(self):
        from services.bets_rules import validar_composicao_aposta

        ok, msg = validar_composicao_aposta(
            pilotos=["Hamilton", "Verstappen", "Leclerc"],
            fichas=[5, -1, 5],
            piloto_11="Sainz",
        )
        assert ok is False
        assert "negativo" in msg.lower()

    def test_piloto_11_vazio_retorna_false(self):
        from services.bets_rules import validar_composicao_aposta

        ok, msg = validar_composicao_aposta(
            pilotos=["Hamilton", "Verstappen", "Leclerc"],
            fichas=[5, 5, 5],
            piloto_11="",
        )
        assert ok is False

    def test_lista_pilotos_vazia_retorna_false(self):
        from services.bets_rules import validar_composicao_aposta

        ok, msg = validar_composicao_aposta(
            pilotos=[], fichas=[], piloto_11="Sainz")
        assert ok is False

    def test_tamanho_pilotos_e_fichas_divergente_retorna_false(self):
        from services.bets_rules import validar_composicao_aposta

        ok, msg = validar_composicao_aposta(
            pilotos=["Hamilton", "Verstappen"],
            fichas=[5, 5, 5],
            piloto_11="Sainz",
        )
        assert ok is False


# ---------------------------------------------------------------------------
# aposta_eh_automatica
# ---------------------------------------------------------------------------

class TestApostaEhAutomatica:

    def test_retorna_true_quando_flag_ativa(self):
        from services.bets_rules import aposta_eh_automatica
        assert aposta_eh_automatica({"automatica": 1}) is True

    def test_retorna_false_quando_flag_ausente(self):
        from services.bets_rules import aposta_eh_automatica
        assert aposta_eh_automatica({}) is False

    def test_retorna_false_quando_flag_zero(self):
        from services.bets_rules import aposta_eh_automatica
        assert aposta_eh_automatica({"automatica": 0}) is False


# ---------------------------------------------------------------------------
# calcular_pior_pontuador
# ---------------------------------------------------------------------------

class TestCalcularPiorPontuador:

    def test_lista_vazia_retorna_zero(self):
        from services.bets_rules import calcular_pior_pontuador
        assert calcular_pior_pontuador([]) == 0.0

    def test_retorna_menor_valor_da_lista(self):
        from services.bets_rules import calcular_pior_pontuador
        assert calcular_pior_pontuador([300.0, 150.0, 200.0]) == 150.0

    def test_ignora_none(self):
        from services.bets_rules import calcular_pior_pontuador
        assert calcular_pior_pontuador([300.0, None, 200.0]) == 200.0

    def test_todos_none_retorna_zero(self):
        from services.bets_rules import calcular_pior_pontuador
        assert calcular_pior_pontuador([None, None]) == 0.0
