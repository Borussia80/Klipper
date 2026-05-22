"""
Comportamento de fallback e invalidação de cache.

Valida o contrato público: API falhou → último valor conhecido retornado.
"""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from core.market_cache import STOCK_TTL

_TS = datetime(2026, 5, 22, 12, 0, 0)


def _stock_raw(price: float = 10.0) -> dict:
    return {"price": price, "change_pct": 0.5, "change_abs": 0.05, "volume": 1_000_000}


def _seed_stock(cache, ticker: str, price: float) -> None:
    cache.set(f"stock:{ticker}", {
        "ticker": ticker, "price": price, "change_pct": 0.5, "change_abs": 0.10,
        "volume": 500_000, "timestamp": _TS.isoformat(), "source": "cache", "is_fallback": False,
    }, STOCK_TTL)


class TestFallbackBehavior:

    def test_stock_usa_fallback_quando_api_falha(self, svc, cache):
        with patch("core.market_data._yf_batch", return_value={"PETR4.SA": _stock_raw(35.0)}):
            q1 = svc.get_stock("PETR4")
        assert q1.price == 35.0

        cache.invalidate("stock:PETR4")
        with patch("core.market_data._yf_batch", side_effect=RuntimeError("timeout")):
            q2 = svc.get_stock("PETR4")

        assert q2 is not None
        assert q2.price == 35.0
        assert q2.is_fallback is True

    def test_retorna_none_sem_fallback_e_api_fora(self, svc):
        with patch("core.market_data._yf_batch", side_effect=RuntimeError("timeout")):
            q = svc.get_stock("TICKER_INEXISTENTE_9999")
        assert q is None

    def test_circuit_aberto_usa_fallback_sem_chamar_api(self, svc, cache):
        # 1. Prime the _fallback store for VALE3
        with patch("core.market_data._yf_batch", return_value={"VALE3.SA": _stock_raw(67.0)}):
            svc.get_stock("VALE3")
        cache.invalidate("stock:VALE3")

        # 2. Open the circuit via 5 consecutive public-API failures (failure_threshold=5)
        with patch("core.market_data._yf_batch", side_effect=RuntimeError("x")):
            for i in range(5):
                svc.get_stock(f"OPEN_CB_{i:04d}")

        # 3. Circuit is OPEN — must serve fallback without calling yfinance
        fetch_mock = MagicMock()
        with patch("core.market_data._yf_batch", fetch_mock):
            q = svc.get_stock("VALE3")

        fetch_mock.assert_not_called()
        assert q is not None
        assert q.is_fallback is True

    def test_tesouro_usa_fallback_quando_circuit_aberto(self, svc, cache):
        raw = [{"TrsrBd": {
            "nm": "Tesouro Selic 2029", "anulInvstmtRate": "12.0",
            "untrInvstmtVal": "14000.0", "mtrtyDt": "2029-03-01T00:00:00",
            "minInvstmtAmt": "40.0",
        }}]
        # 1. Prime the _fallback store
        with patch("core.market_data._fetch_tesouro_raw", return_value=raw):
            svc.get_tesouro_bonds()
        cache.invalidate("tesouro:bonds")

        # 2. Open the circuit via 3 consecutive failures (failure_threshold=3)
        with patch("core.market_data._fetch_tesouro_raw", side_effect=RuntimeError("timeout")):
            for _ in range(3):
                svc.get_tesouro_bonds()

        # 3. Circuit is OPEN — must serve _fallback store
        bonds = svc.get_tesouro_bonds()
        assert len(bonds) == 1
        assert bonds[0].name == "Tesouro Selic 2029"


class TestCacheInvalidation:

    def test_invalidate_forca_nova_busca_na_api(self, svc, cache):
        with patch("core.market_data._yf_batch", return_value={"WEGE3.SA": _stock_raw(45.0)}):
            q1 = svc.get_stock("WEGE3")
        assert q1.price == 45.0

        cache.invalidate("stock:WEGE3")

        with patch("core.market_data._yf_batch", return_value={"WEGE3.SA": _stock_raw(47.0)}):
            q2 = svc.get_stock("WEGE3")
        assert q2.price == 47.0

    def test_force_refresh_atualiza_cache(self, svc, cache):
        _seed_stock(cache, "BBAS3", price=50.0)
        with patch("core.market_data._yf_batch", return_value={"BBAS3.SA": _stock_raw(52.5)}):
            q = svc.get_stock("BBAS3", force_refresh=True)
        assert q.price == 52.5
        assert cache.get("stock:BBAS3")["price"] == 52.5

    def test_invalidate_pattern_remove_multiplos(self, svc, cache):
        for t in ["PETR4", "VALE3", "ITUB4"]:
            _seed_stock(cache, t, price=30.0)
        cache.invalidate_pattern("stock:*")
        for t in ["PETR4", "VALE3", "ITUB4"]:
            assert cache.get(f"stock:{t}") is None

    def test_ttl_stock_respeita_limite_configurado(self, svc):
        from core.market_cache import STOCK_TTL
        with patch("core.market_data._yf_batch", return_value={"MGLU3.SA": _stock_raw(2.5)}):
            svc.get_stock("MGLU3")
        remaining = svc._cache.ttl("stock:MGLU3")
        assert 0 < remaining <= STOCK_TTL
