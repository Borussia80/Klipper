"""
Circuit Breaker — máquina de estados CLOSED/OPEN/HALF_OPEN.

Todos os testes de transição de tempo usam monkeypatch em
core.circuit_breaker.monotonic para eliminar time.sleep().
Asserções validam comportamento público — nunca atributos privados.
"""
from __future__ import annotations

import threading
from unittest.mock import MagicMock

import pytest

from core.circuit_breaker import CircuitBreaker, CircuitOpenError, get_breaker


class TestCircuitBreakerEstados:

    def test_estado_inicial_e_closed(self):
        cb = CircuitBreaker("cb_initial", failure_threshold=3)
        assert cb.state.value == "closed"

    def test_aceita_chamadas_em_estado_closed(self):
        cb = CircuitBreaker("cb_calls_ok", failure_threshold=3)
        assert cb.call(lambda: 42) == 42

    def test_abre_apos_threshold_de_falhas(self):
        cb = CircuitBreaker("cb_open", failure_threshold=3, recovery_timeout=999)
        failing = MagicMock(side_effect=RuntimeError("boom"))
        for _ in range(3):
            with pytest.raises(RuntimeError):
                cb.call(failing)
        assert cb.state.value == "open"

    def test_rejeita_chamadas_quando_aberto(self):
        cb = CircuitBreaker("cb_blocked", failure_threshold=1, recovery_timeout=999)
        with pytest.raises(RuntimeError):
            cb.call(MagicMock(side_effect=RuntimeError("first")))
        with pytest.raises(CircuitOpenError):
            cb.call(lambda: "nunca chega aqui")

    def test_sucesso_mantem_circuito_fechado(self):
        cb = CircuitBreaker("cb_stays_closed", failure_threshold=3)
        cb.call(lambda: None)
        assert cb.state.value == "closed"

    def test_reset_restaura_comportamento_normal(self):
        cb = CircuitBreaker("cb_reset", failure_threshold=1, recovery_timeout=999)
        with pytest.raises(RuntimeError):
            cb.call(MagicMock(side_effect=RuntimeError("x")))
        assert cb.state.value == "open"

        cb.reset()

        assert cb.state.value == "closed"
        assert cb.call(lambda: 99) == 99   # chamadas voltam a funcionar


class TestCircuitBreakerHalfOpen:
    """Transições envolvendo tempo são controladas via monkeypatch de monotonic."""

    def test_transiciona_para_half_open_apos_recovery_timeout(self, monkeypatch):
        cb = CircuitBreaker("cb_half_mono", failure_threshold=1, recovery_timeout=1.0)
        with pytest.raises(RuntimeError):
            cb.call(MagicMock(side_effect=RuntimeError("x")))
        assert cb.state.value == "open"

        # Avança tempo virtual bem além do recovery_timeout — sem sleep real
        monkeypatch.setattr("core.circuit_breaker.monotonic", lambda: 1e18)

        assert cb.state.value == "half_open"

    def test_sucesso_em_half_open_fecha_circuito(self, monkeypatch):
        cb = CircuitBreaker("cb_recover", failure_threshold=1, recovery_timeout=1.0)
        with pytest.raises(RuntimeError):
            cb.call(MagicMock(side_effect=RuntimeError("x")))

        monkeypatch.setattr("core.circuit_breaker.monotonic", lambda: 1e18)

        cb.call(lambda: "ok")
        assert cb.state.value == "closed"

    def test_falha_em_half_open_reabre_circuito(self, monkeypatch):
        cb = CircuitBreaker("cb_reopen", failure_threshold=1, recovery_timeout=1.0)
        with pytest.raises(RuntimeError):
            cb.call(MagicMock(side_effect=RuntimeError("first")))

        monkeypatch.setattr("core.circuit_breaker.monotonic", lambda: 1e18)

        with pytest.raises(RuntimeError):
            cb.call(MagicMock(side_effect=RuntimeError("second")))
        assert cb.state.value == "open"


class TestCircuitBreakerRegistry:

    def test_get_breaker_retorna_mesma_instancia(self):
        b1 = get_breaker("registry_singleton_test")
        b2 = get_breaker("registry_singleton_test")
        assert b1 is b2

    def test_thread_safety_sem_erros_de_concorrencia(self):
        cb = CircuitBreaker("cb_threads", failure_threshold=100, recovery_timeout=999)
        unexpected_errors: list[Exception] = []

        def _fail():
            try:
                cb.call(MagicMock(side_effect=RuntimeError("x")))
            except RuntimeError:
                pass  # esperado
            except Exception as e:
                unexpected_errors.append(e)

        threads = [threading.Thread(target=_fail) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert unexpected_errors == [], f"Erros de threading: {unexpected_errors}"
        # 20 falhas < threshold 100 → circuito ainda fechado
        assert cb.state.value == "closed"
        assert cb.call(lambda: True) is True
