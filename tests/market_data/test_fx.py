"""
Câmbio — PTAX (BCB) e taxas em tempo real.

_fetch_ptax_raw e _fetch_fx_raw são sempre mockadas: fronteira de I/O HTTP.
"""
from __future__ import annotations

from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from core.market_data import ExchangeRate

_FIXED_TS = datetime(2026, 5, 22, 12, 0, 0)

_PTAX_RAW = {
    "cotacaoCompra": 5.7300,
    "cotacaoVenda": 5.7320,
    "dataHoraCotacao": "2026-05-21 13:07:43.929",
}
_PTAX_DATE = date(2026, 5, 21)


class TestPTAX:

    def test_retorna_exchange_rate_correto(self, svc):
        with patch("core.market_data._fetch_ptax_raw", return_value=_PTAX_RAW):
            rate = svc.get_ptax(reference_date=_PTAX_DATE)
        assert rate is not None
        assert rate.pair == "BRL/USD"
        assert rate.bid  == pytest.approx(5.73)
        assert rate.ask  == pytest.approx(5.732)
        assert rate.mid  == pytest.approx((5.73 + 5.732) / 2, rel=1e-4)
        assert rate.source == "bcb_ptax"

    def test_salvo_no_cache(self, svc, cache):
        with patch("core.market_data._fetch_ptax_raw", return_value=_PTAX_RAW):
            svc.get_ptax(reference_date=_PTAX_DATE)
        cached = cache.get("ptax:2026-05-21")
        assert cached is not None
        assert cached["pair"] == "BRL/USD"

    def test_servido_do_cache_sem_chamar_api(self, svc):
        with patch("core.market_data._fetch_ptax_raw", return_value=_PTAX_RAW):
            svc.get_ptax(reference_date=_PTAX_DATE)
        mock_fetch = MagicMock()
        with patch("core.market_data._fetch_ptax_raw", mock_fetch):
            rate = svc.get_ptax(reference_date=_PTAX_DATE)
        mock_fetch.assert_not_called()
        assert rate is not None


class TestExchangeRateTaxas:

    def test_get_brl_usd(self, svc):
        fx = {"price": 0.1748, "change_abs": 0.001, "change_pct": 0.5}
        with patch("core.market_data._fetch_fx_raw", return_value=fx):
            rate = svc.get_exchange_rate("BRL/USD")
        assert rate is not None
        assert rate.pair == "BRL/USD"
        assert rate.mid  == pytest.approx(0.1748)

    def test_spread_gera_bid_menor_que_ask(self, svc):
        fx = {"price": 5.73, "change_abs": 0.0, "change_pct": 0.0}
        with patch("core.market_data._fetch_fx_raw", return_value=fx):
            rate = svc.get_exchange_rate("USD/BRL", spread_pct=2.0)
        assert rate.bid < rate.mid < rate.ask

    def test_par_invalido_levanta_value_error(self, svc):
        with pytest.raises(ValueError, match="não suportado"):
            svc.get_exchange_rate("XYZ/ABC")

    def test_with_spread_calcula_bid_ask(self):
        rate = ExchangeRate(
            pair="BRL/USD", bid=5.73, ask=5.73, mid=5.73,
            source="test", timestamp=_FIXED_TS,
        )
        spread = rate.with_spread(2.0)
        assert spread.bid == pytest.approx(5.73 * 0.99, rel=1e-4)
        assert spread.ask == pytest.approx(5.73 * 1.01, rel=1e-4)
        assert spread.mid == 5.73


class TestConversao:

    @pytest.mark.parametrize("amount,from_ccy,to_ccy,expected", [
        (1000.0, "BRL", "BRL", 1000.0),
    ])
    def test_mesma_moeda_identidade(self, svc, amount, from_ccy, to_ccy, expected):
        assert svc.convert(amount, from_ccy, to_ccy) == pytest.approx(expected)

    def test_usd_para_brl(self, svc):
        fx = {"price": 5.73, "change_abs": 0.0, "change_pct": 0.0}
        with patch("core.market_data._fetch_fx_raw", return_value=fx):
            brl = svc.convert(100.0, "USD", "BRL")
        assert brl == pytest.approx(573.0, rel=1e-2)

    def test_brl_para_usd(self, svc):
        fx = {"price": 0.1748, "change_abs": 0.0, "change_pct": 0.0}
        with patch("core.market_data._fetch_fx_raw", return_value=fx):
            usd = svc.convert(573.0, "BRL", "USD")
        assert usd == pytest.approx(100.07, rel=1e-2)

    def test_spread_aumenta_custo_da_conversao(self, svc):
        fx = {"price": 5.73, "change_abs": 0.0, "change_pct": 0.0}
        with patch("core.market_data._fetch_fx_raw", return_value=fx):
            sem_spread  = svc.convert(100.0, "USD", "BRL", spread_pct=0.0)
            com_spread  = svc.convert(100.0, "USD", "BRL", spread_pct=2.0)
        assert com_spread > sem_spread
