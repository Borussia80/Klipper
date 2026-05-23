"""TDD Red — helpers para pages/13_Cotacoes.py."""

from __future__ import annotations

import pytest


class TestFmtChange:
    """fmt_change(pct: float) -> str — formata variação percentual."""

    def test_positive_returns_plus_prefix(self):
        from core.styles import fmt_change
        assert fmt_change(1.23).startswith("+")

    def test_negative_returns_minus_prefix(self):
        from core.styles import fmt_change
        assert fmt_change(-0.45).startswith("-")

    def test_zero_returns_plus_prefix(self):
        from core.styles import fmt_change
        assert fmt_change(0.0).startswith("+")

    def test_two_decimal_places(self):
        from core.styles import fmt_change
        assert fmt_change(1.23) == "+1.23%"

    def test_negative_two_decimal_places(self):
        from core.styles import fmt_change
        assert fmt_change(-0.45) == "-0.45%"

    def test_large_positive(self):
        from core.styles import fmt_change
        assert fmt_change(12.5) == "+12.50%"

    def test_zero_exact(self):
        from core.styles import fmt_change
        assert fmt_change(0.0) == "+0.00%"

    def test_small_negative(self):
        from core.styles import fmt_change
        assert fmt_change(-0.01) == "-0.01%"


class TestIsFii:
    """is_fii(ticker: str) -> bool — retorna True se ticker é FII (termina em 11)."""

    def test_fii_ticker_ends_11(self):
        from core.market_data import is_fii
        assert is_fii("MXRF11") is True

    def test_fii_ticker_hglg11(self):
        from core.market_data import is_fii
        assert is_fii("HGLG11") is True

    def test_stock_ticker_returns_false(self):
        from core.market_data import is_fii
        assert is_fii("PETR4") is False

    def test_etf_bova11_returns_true(self):
        from core.market_data import is_fii
        assert is_fii("BOVA11") is True

    def test_stock_ending_3(self):
        from core.market_data import is_fii
        assert is_fii("VALE3") is False

    def test_stock_ending_5(self):
        from core.market_data import is_fii
        assert is_fii("ITUB4") is False

    def test_lowercase_ticker_returns_false(self):
        from core.market_data import is_fii
        assert is_fii("mxrf11") is False

    def test_empty_string_returns_false(self):
        from core.market_data import is_fii
        assert is_fii("") is False
