"""TDD Sprint 6 — Tesouro Direto histórico: CSV público + chart."""
from __future__ import annotations

from datetime import date
from io import StringIO
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest


# CSV mínimo com formato real do Tesouro (sep=';', encoding latin-1, decimal=',')
_CSV_SAMPLE = (
    "Tipo Título;Data Venda;Taxa Compra Manha;Taxa Venda Manha;"
    "PU Compra Manha;PU Venda Manha;PU Base Manha\n"
    "Tesouro IPCA+ 2029;01/04/2024;5,42;5,47;3814,25;3801,10;3814,25\n"
    "Tesouro IPCA+ 2029;02/04/2024;5,38;5,43;3825,60;3812,00;3825,60\n"
    "Tesouro Selic 2027;01/04/2024;0,0015;0,0020;13543,21;13535,10;13543,21\n"
    "Tesouro Selic 2027;02/04/2024;0,0015;0,0020;13561,44;13553,20;13561,44\n"
)


def _mock_csv_response(content: str = _CSV_SAMPLE):
    """Retorna um mock de requests.get com o conteúdo CSV."""
    mock_resp = MagicMock()
    mock_resp.content = content.encode("latin-1")
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


# ── get_tesouro_history ───────────────────────────────────────────────────────

class TestGetTesouroCsvHistory:

    def _make_service(self):
        from core.market_data import MarketDataService
        from core.market_cache import MarketCache
        return MarketDataService(cache=MarketCache())

    def test_method_exists(self):
        svc = self._make_service()
        assert hasattr(svc, "get_tesouro_history")
        assert callable(svc.get_tesouro_history)

    def test_returns_list(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history()
        assert isinstance(result, list)

    def test_result_not_empty_with_valid_csv(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history()
        assert len(result) > 0

    def test_row_has_required_keys(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history()
        row = result[0]
        for key in ("date", "bond_type", "rate_buy", "rate_sell", "price_buy"):
            assert key in row, f"chave '{key}' ausente"

    def test_date_is_date_object(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history()
        assert isinstance(result[0]["date"], date)

    def test_rate_is_float(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history()
        assert isinstance(result[0]["rate_buy"], float)

    def test_price_is_float(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history()
        assert isinstance(result[0]["price_buy"], float)

    def test_filter_by_bond_type(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history(bond_type="Tesouro Selic 2027")
        types = {r["bond_type"] for r in result}
        assert types == {"Tesouro Selic 2027"}

    def test_filter_by_start_date(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history(start_date=date(2024, 4, 2))
        assert all(r["date"] >= date(2024, 4, 2) for r in result)

    def test_network_error_returns_empty(self):
        svc = self._make_service()
        with patch("requests.get", side_effect=Exception("timeout")):
            result = svc.get_tesouro_history()
        assert result == []

    def test_ordered_chronologically(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history(bond_type="Tesouro IPCA+ 2029")
        dates = [r["date"] for r in result]
        assert dates == sorted(dates)

    def test_unique_bond_types_returned(self):
        svc = self._make_service()
        with patch("requests.get", return_value=_mock_csv_response()):
            result = svc.get_tesouro_history()
        types = {r["bond_type"] for r in result}
        assert "Tesouro IPCA+ 2029" in types
        assert "Tesouro Selic 2027" in types


# ── preparar_dados_tesouro_historico ─────────────────────────────────────────

class TestPrepararDadosTesouroCsvHistorico:

    def _hist(self, n: int = 3, bond: str = "Tesouro IPCA+ 2029") -> list[dict]:
        return [
            {
                "date": date(2024, 4, i + 1),
                "bond_type": bond,
                "rate_buy": 5.40 + i * 0.02,
                "rate_sell": 5.45 + i * 0.02,
                "price_buy": 3800.0 + i * 15,
            }
            for i in range(n)
        ]

    def test_returns_list(self):
        from core.analytics import preparar_dados_tesouro_historico
        result = preparar_dados_tesouro_historico(self._hist(), "Tesouro IPCA+ 2029")
        assert isinstance(result, list)

    def test_empty_input_returns_empty(self):
        from core.analytics import preparar_dados_tesouro_historico
        result = preparar_dados_tesouro_historico([], "Tesouro IPCA+ 2029")
        assert result == []

    def test_length_matches_input(self):
        from core.analytics import preparar_dados_tesouro_historico
        result = preparar_dados_tesouro_historico(self._hist(5), "Tesouro IPCA+ 2029")
        assert len(result) == 5

    def test_row_has_required_keys(self):
        from core.analytics import preparar_dados_tesouro_historico
        result = preparar_dados_tesouro_historico(self._hist(), "Tesouro IPCA+ 2029")
        row = result[0]
        assert "date" in row
        assert "Taxa (%)" in row
        assert "Preço (R$)" in row

    def test_date_is_string(self):
        from core.analytics import preparar_dados_tesouro_historico
        result = preparar_dados_tesouro_historico(self._hist(), "Tesouro IPCA+ 2029")
        assert isinstance(result[0]["date"], str)

    def test_taxa_is_float(self):
        from core.analytics import preparar_dados_tesouro_historico
        result = preparar_dados_tesouro_historico(self._hist(), "Tesouro IPCA+ 2029")
        assert isinstance(result[0]["Taxa (%)"], float)

    def test_preco_is_float(self):
        from core.analytics import preparar_dados_tesouro_historico
        result = preparar_dados_tesouro_historico(self._hist(), "Tesouro IPCA+ 2029")
        assert isinstance(result[0]["Preço (R$)"], float)

    def test_filters_to_requested_bond(self):
        from core.analytics import preparar_dados_tesouro_historico
        mixed = self._hist(2, "Tesouro IPCA+ 2029") + self._hist(2, "Tesouro Selic 2027")
        result = preparar_dados_tesouro_historico(mixed, "Tesouro Selic 2027")
        assert len(result) == 2

    def test_ordered_chronologically(self):
        from core.analytics import preparar_dados_tesouro_historico
        hist = list(reversed(self._hist(4)))
        result = preparar_dados_tesouro_historico(hist, "Tesouro IPCA+ 2029")
        dates = [r["date"] for r in result]
        assert dates == sorted(dates)

    def test_taxa_value_correct(self):
        from core.analytics import preparar_dados_tesouro_historico
        hist = [{"date": date(2024, 4, 1), "bond_type": "T", "rate_buy": 5.42,
                 "rate_sell": 5.47, "price_buy": 3814.25}]
        result = preparar_dados_tesouro_historico(hist, "T")
        assert abs(result[0]["Taxa (%)"] - 5.42) < 0.001

    def test_preco_value_correct(self):
        from core.analytics import preparar_dados_tesouro_historico
        hist = [{"date": date(2024, 4, 1), "bond_type": "T", "rate_buy": 5.42,
                 "rate_sell": 5.47, "price_buy": 3814.25}]
        result = preparar_dados_tesouro_historico(hist, "T")
        assert abs(result[0]["Preço (R$)"] - 3814.25) < 0.01
