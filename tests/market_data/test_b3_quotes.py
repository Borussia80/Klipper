"""
Cotações B3 — ações, ETFs e FIIs.

Helpers de seed definidos localmente — setup explícito, sem indireção.
yfinance sempre mockado: fronteira de I/O.
"""
from __future__ import annotations

from datetime import datetime
from time import perf_counter
from unittest.mock import patch

import pytest

from core.market_cache import STOCK_TTL, FII_TTL
from core.market_data import StockQuote, FIIQuote

_TS = datetime(2026, 5, 22, 12, 0, 0)


def _stock_raw(price: float = 10.0, pct: float = 1.5) -> dict:
    return {"price": price, "change_pct": pct, "change_abs": round(price * pct / 100, 4), "volume": 1_000_000}


def _seed_stock(cache, ticker: str, price: float = 20.0) -> None:
    cache.set(f"stock:{ticker}", {
        "ticker": ticker, "price": price, "change_pct": 0.5, "change_abs": 0.10,
        "volume": 500_000, "timestamp": _TS.isoformat(), "source": "cache", "is_fallback": False,
    }, STOCK_TTL)


def _seed_fii(cache, ticker: str) -> None:
    cache.set(f"fii:{ticker}", {
        "ticker": ticker, "price": 11.50, "change_pct": 0.3, "change_abs": 0.03,
        "volume": 200_000, "dy_12m": 11.5, "last_income": 0.11, "pvp": 0.98,
        "timestamp": _TS.isoformat(), "source": "cache", "is_fallback": False,
    }, FII_TTL)


class TestStockQuote:

    def test_retorna_cotacao_do_cache(self, svc, cache):
        _seed_stock(cache, "PETR4", price=36.50)
        q = svc.get_stock("PETR4")
        assert q is not None
        assert q.ticker == "PETR4"
        assert q.price == 36.50

    def test_busca_api_em_cache_miss(self, svc):
        with patch("core.market_data._yf_batch", return_value={"PETR4.SA": _stock_raw(price=35.0, pct=2.1)}):
            q = svc.get_stock("PETR4")
        assert q is not None
        assert q.price == 35.0
        assert q.change_pct == 2.1
        assert q.source == "yfinance"

    def test_normaliza_ticker_para_maiusculo(self, svc):
        with patch("core.market_data._yf_batch", return_value={"VALE3.SA": _stock_raw(price=67.0)}):
            q = svc.get_stock("vale3")
        assert q.ticker == "VALE3"

    def test_grava_no_cache_apos_api(self, svc, cache):
        with patch("core.market_data._yf_batch", return_value={"WEGE3.SA": _stock_raw(price=45.0)}):
            svc.get_stock("WEGE3")
        cached = cache.get("stock:WEGE3")
        assert cached is not None
        assert cached["price"] == 45.0

    def test_force_refresh_ignora_cache(self, svc, cache):
        _seed_stock(cache, "ITUB4", price=28.0)
        with patch("core.market_data._yf_batch", return_value={"ITUB4.SA": _stock_raw(price=29.5)}):
            q = svc.get_stock("ITUB4", force_refresh=True)
        assert q.price == 29.5


class TestStockBatchPerformance:

    def _seed_n(self, cache, n: int) -> list[str]:
        tickers = [f"TICK{i:04d}" for i in range(n)]
        for t in tickers:
            _seed_stock(cache, t, price=float(10 + hash(t) % 90))
        return tickers

    def test_1000_ativos_do_cache_em_menos_de_2_segundos(self, svc, cache):
        tickers = self._seed_n(cache, 1000)
        start = perf_counter()
        result = svc.get_stocks_batch(tickers)
        elapsed = perf_counter() - start
        assert len(result) == 1000
        assert elapsed < 2.0, f"1000 cotações: {elapsed:.2f}s"

    def test_batch_consolida_resultados_corretamente(self, svc, cache):
        tickers = self._seed_n(cache, 50)
        result = svc.get_stocks_batch(tickers)
        assert set(result.keys()) == set(tickers)
        assert all(q.price > 0 for q in result.values())

    def test_batch_vazio_retorna_dict_vazio(self, svc):
        assert svc.get_stocks_batch([]) == {}

    def test_batch_busca_cache_misses_via_api(self, svc, cache):
        _seed_stock(cache, "PETR4", price=35.0)
        with patch("core.market_data._yf_batch", return_value={"VALE3.SA": _stock_raw(price=67.0)}):
            result = svc.get_stocks_batch(["PETR4", "VALE3"])
        assert result["PETR4"].price == 35.0
        assert result["VALE3"].price == 67.0

    def test_batch_parcial_quando_api_retorna_subset(self, svc):
        with patch("core.market_data._yf_batch", return_value={"PETR4.SA": _stock_raw(price=35.0)}):
            result = svc.get_stocks_batch(["PETR4", "VALE3"])
        assert "PETR4" in result


class TestFIIQuote:

    def test_retorna_fii_do_cache(self, svc, cache):
        _seed_fii(cache, "MXRF11")
        q = svc.get_fii("MXRF11")
        assert q is not None
        assert q.ticker == "MXRF11"
        assert q.dy_12m == pytest.approx(11.5)
        assert q.pvp == pytest.approx(0.98)

    def test_campos_fundamentais_nao_negativos(self, svc, cache):
        _seed_fii(cache, "HGLG11")
        q = svc.get_fii("HGLG11")
        assert q.dy_12m >= 0
        assert q.last_income >= 0
        assert q.pvp >= 0

    def test_batch_retorna_todos_do_cache(self, svc, cache):
        for t in ["MXRF11", "HGLG11", "XPML11"]:
            _seed_fii(cache, t)
        result = svc.get_fiis_batch(["MXRF11", "HGLG11", "XPML11"])
        assert set(result.keys()) == {"MXRF11", "HGLG11", "XPML11"}

    def test_ttl_positivo_apos_cache_hit(self, svc, cache):
        _seed_fii(cache, "KNRI11")
        svc.get_fii("KNRI11")
        assert cache.ttl("fii:KNRI11") > 0
