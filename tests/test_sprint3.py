"""TDD Sprint 3 — line chart portfolio vs benchmarks + bubble chart DY×P/VP."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_investment(
    ticker: str,
    tipo: str = "FII",
    qty: float = 100,
    avg: float = 10.0,
    current: float = 11.0,
    dy: float = 8.5,
    pvp: float = 0.92,
    sector: str = "Logística",
):
    from models.investment import Investment, InvestmentType
    return Investment(
        ticker=ticker,
        type=InvestmentType(tipo),
        quantity=qty,
        avg_price=Decimal(str(avg)),
        current_price=Decimal(str(current)),
        dy_12m=dy,
        pvp=pvp,
        liquidity_daily=500_000.0,
        volatility=10.0,
        spread_vs_cdi=2.0,
        sector=sector,
    )


def _make_hist(ticker: str, prices: list[float], start: date | None = None) -> list[dict]:
    """Gera histórico sintético de preços."""
    d = start or date(2030, 4, 1)
    return [
        {"date": d + timedelta(days=i), "close": p}
        for i, p in enumerate(prices)
    ]


# ── preparar_dados_bolha ──────────────────────────────────────────────────────

class TestPrepararDadosBolha:

    def test_returns_list(self):
        from core.analytics import preparar_dados_bolha
        inv = [_make_investment("MXRF11")]
        result = preparar_dados_bolha(inv, Decimal("1100"))
        assert isinstance(result, list)

    def test_one_asset_one_row(self):
        from core.analytics import preparar_dados_bolha
        inv = [_make_investment("MXRF11")]
        result = preparar_dados_bolha(inv, Decimal("1100"))
        assert len(result) == 1

    def test_row_has_required_keys(self):
        from core.analytics import preparar_dados_bolha
        inv = [_make_investment("MXRF11")]
        result = preparar_dados_bolha(inv, Decimal("1100"))
        row = result[0]
        for key in ("ticker", "dy_12m", "pvp", "valor", "peso_pct", "tipo"):
            assert key in row, f"chave '{key}' ausente"

    def test_dy_and_pvp_are_floats(self):
        from core.analytics import preparar_dados_bolha
        inv = [_make_investment("MXRF11", dy=8.5, pvp=0.92)]
        result = preparar_dados_bolha(inv, Decimal("1100"))
        assert isinstance(result[0]["dy_12m"], float)
        assert isinstance(result[0]["pvp"], float)

    def test_valor_equals_current_value(self):
        from core.analytics import preparar_dados_bolha
        inv = _make_investment("MXRF11", qty=100, current=11.0)
        result = preparar_dados_bolha([inv], Decimal("1100"))
        assert abs(result[0]["valor"] - 1100.0) < 0.01

    def test_peso_pct_soma_100(self):
        from core.analytics import preparar_dados_bolha
        portfolio = [
            _make_investment("MXRF11", qty=100, current=10.0),
            _make_investment("HGLG11", qty=200, current=5.0),
        ]
        total = Decimal("2000")
        result = preparar_dados_bolha(portfolio, total)
        soma = sum(r["peso_pct"] for r in result)
        assert abs(soma - 100.0) < 0.1

    def test_exclui_ativos_sem_dy_e_pvp(self):
        from core.analytics import preparar_dados_bolha
        inv = [
            _make_investment("MXRF11", dy=8.5, pvp=0.92),
            _make_investment("BOVA11", dy=0.0, pvp=0.0),  # ETF sem dados fundamentais
        ]
        total = Decimal("2200")
        result = preparar_dados_bolha(inv, total)
        tickers = [r["ticker"] for r in result]
        assert "MXRF11" in tickers
        assert "BOVA11" not in tickers

    def test_tipo_propagado(self):
        from core.analytics import preparar_dados_bolha
        inv = [_make_investment("PETR4", tipo="Ação", dy=3.0, pvp=1.5)]
        result = preparar_dados_bolha(inv, Decimal("1100"))
        assert result[0]["tipo"] == "Ação"

    def test_empty_portfolio_returns_empty(self):
        from core.analytics import preparar_dados_bolha
        result = preparar_dados_bolha([], Decimal("0"))
        assert result == []

    def test_multiple_assets_sorted_by_value(self):
        from core.analytics import preparar_dados_bolha
        portfolio = [
            _make_investment("SMALL", qty=10, current=5.0, dy=5.0, pvp=0.8),
            _make_investment("BIG",   qty=100, current=20.0, dy=6.0, pvp=1.0),
        ]
        total = Decimal(str(10 * 5 + 100 * 20))
        result = preparar_dados_bolha(portfolio, total)
        assert result[0]["valor"] >= result[-1]["valor"]


# ── preparar_dados_linha_normalizado ─────────────────────────────────────────

class TestPrepararDadosLinhaNormalizado:

    def _port_hist(self, prices: list[float]) -> list[dict]:
        d = date(2030, 4, 1)
        return [{"date": d + timedelta(days=i), "valor": p} for i, p in enumerate(prices)]

    def _bench_hist(self, ticker: str, prices: list[float]) -> dict[str, list[dict]]:
        return {ticker: _make_hist(ticker, prices, start=date(2030, 4, 1))}

    def test_returns_list(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([1000, 1010, 1020])
        bh = self._bench_hist("BOVA11", [100, 101, 102])
        result = preparar_dados_linha_normalizado(ph, bh)
        assert isinstance(result, list)

    def test_length_matches_portfolio_hist(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([1000, 1010, 1020])
        bh = self._bench_hist("BOVA11", [100, 101, 102])
        result = preparar_dados_linha_normalizado(ph, bh)
        assert len(result) == 3

    def test_row_has_date_key(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([1000, 1010])
        bh = self._bench_hist("BOVA11", [100, 101])
        result = preparar_dados_linha_normalizado(ph, bh)
        assert "date" in result[0]

    def test_portfolio_starts_at_100(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([5000, 5100, 5250])
        bh = self._bench_hist("BOVA11", [110, 112, 115])
        result = preparar_dados_linha_normalizado(ph, bh)
        assert abs(result[0]["Portfólio"] - 100.0) < 0.01

    def test_benchmark_starts_at_100(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([5000, 5100])
        bh = self._bench_hist("BOVA11", [110, 112])
        result = preparar_dados_linha_normalizado(ph, bh)
        assert abs(result[0]["BOVA11"] - 100.0) < 0.01

    def test_portfolio_gain_reflected(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([1000, 1100])  # +10%
        bh = self._bench_hist("BOVA11", [100, 103])
        result = preparar_dados_linha_normalizado(ph, bh)
        assert abs(result[-1]["Portfólio"] - 110.0) < 0.01

    def test_multiple_benchmarks(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([1000, 1010])
        bh = {
            "BOVA11": _make_hist("BOVA11", [100, 101], date(2030, 4, 1)),
            "IFIX11": _make_hist("IFIX11", [200, 202], date(2030, 4, 1)),
        }
        result = preparar_dados_linha_normalizado(ph, bh)
        assert "BOVA11" in result[0]
        assert "IFIX11" in result[0]

    def test_empty_portfolio_returns_empty(self):
        from core.analytics import preparar_dados_linha_normalizado
        result = preparar_dados_linha_normalizado([], {})
        assert result == []

    def test_date_formatted_as_string(self):
        from core.analytics import preparar_dados_linha_normalizado
        ph = self._port_hist([1000, 1010])
        bh = self._bench_hist("BOVA11", [100, 101])
        result = preparar_dados_linha_normalizado(ph, bh)
        assert isinstance(result[0]["date"], str)


# ── get_price_history ─────────────────────────────────────────────────────────

class TestGetPriceHistory:

    def _make_service(self):
        from core.market_data import MarketDataService
        from core.market_cache import MarketCache
        cache = MarketCache()
        return MarketDataService(cache=cache)

    def test_method_exists(self):
        svc = self._make_service()
        assert hasattr(svc, "get_price_history")
        assert callable(svc.get_price_history)

    def test_empty_tickers_returns_empty(self):
        svc = self._make_service()
        result = svc.get_price_history([], days=30)
        assert result == {}

    def test_returns_dict(self):
        import pandas as pd
        import numpy as np

        dates = pd.date_range("2030-04-01", periods=5, freq="B")
        prices = [10.0, 10.5, 10.3, 10.8, 11.0]
        idx = pd.MultiIndex.from_product([["Close"], ["MXRF11.SA"]])
        df = pd.DataFrame(
            {("Close", "MXRF11.SA"): prices},
            index=dates,
        )
        df.columns = pd.MultiIndex.from_tuples(df.columns)

        svc = self._make_service()
        with patch("yfinance.download", return_value=df):
            result = svc.get_price_history(["MXRF11"], days=5)

        assert isinstance(result, dict)

    def test_ticker_in_result(self):
        import pandas as pd

        dates = pd.date_range("2030-04-01", periods=5, freq="B")
        prices = [10.0, 10.5, 10.3, 10.8, 11.0]
        df = pd.DataFrame(
            {("Close", "MXRF11.SA"): prices},
            index=dates,
        )
        df.columns = pd.MultiIndex.from_tuples(df.columns)

        svc = self._make_service()
        with patch("yfinance.download", return_value=df):
            result = svc.get_price_history(["MXRF11"], days=5)

        assert "MXRF11" in result

    def test_result_entries_have_date_and_close(self):
        import pandas as pd

        dates = pd.date_range("2030-04-01", periods=3, freq="B")
        prices = [10.0, 10.5, 11.0]
        df = pd.DataFrame(
            {("Close", "MXRF11.SA"): prices},
            index=dates,
        )
        df.columns = pd.MultiIndex.from_tuples(df.columns)

        svc = self._make_service()
        with patch("yfinance.download", return_value=df):
            result = svc.get_price_history(["MXRF11"], days=3)

        if "MXRF11" in result and result["MXRF11"]:
            entry = result["MXRF11"][0]
            assert "date" in entry
            assert "close" in entry

    def test_result_ordered_chronologically(self):
        import pandas as pd

        dates = pd.date_range("2030-04-01", periods=4, freq="B")
        prices = [10.0, 11.0, 9.0, 12.0]
        df = pd.DataFrame(
            {("Close", "MXRF11.SA"): prices},
            index=dates,
        )
        df.columns = pd.MultiIndex.from_tuples(df.columns)

        svc = self._make_service()
        with patch("yfinance.download", return_value=df):
            result = svc.get_price_history(["MXRF11"], days=4)

        if "MXRF11" in result and len(result["MXRF11"]) > 1:
            dates_out = [e["date"] for e in result["MXRF11"]]
            assert dates_out == sorted(dates_out)

    def test_yfinance_error_returns_empty_for_ticker(self):
        svc = self._make_service()
        with patch("yfinance.download", side_effect=Exception("network error")):
            result = svc.get_price_history(["MXRF11"], days=30)
        assert result == {} or "MXRF11" not in result
