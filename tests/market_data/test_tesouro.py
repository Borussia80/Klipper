"""
Tesouro Direto — parse, cache e fallback.

_fetch_tesouro_raw é sempre mockada: fronteira de I/O HTTP real.
"""
from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from core.market_data import TesouroBond, _parse_bond_type, _parse_tesouro_bond

_TESOURO_RAW = [
    {"TrsrBd": {
        "nm": "Tesouro Selic 2029",
        "anulInvstmtRate": "12.35",
        "untrInvstmtVal": "14523.45",
        "mtrtyDt": "2029-03-01T00:00:00",
        "minInvstmtAmt": "41.65",
    }},
    {"TrsrBd": {
        "nm": "Tesouro IPCA+ 2035",
        "anulInvstmtRate": "6.80",
        "untrInvstmtVal": "3421.10",
        "mtrtyDt": "2035-05-15T00:00:00",
        "minInvstmtAmt": "34.21",
    }},
    {"TrsrBd": {
        "nm": "Tesouro Prefixado 2027",
        "anulInvstmtRate": "13.10",
        "untrInvstmtVal": "876.32",
        "mtrtyDt": "2027-01-01T00:00:00",
        "minInvstmtAmt": "30.00",
    }},
]


class TestTesouroParse:

    @pytest.mark.parametrize("nome,esperado", [
        ("Tesouro Selic 2029",      "LFT"),
        ("Tesouro IPCA+ 2035",      "NTN-B"),
        ("Tesouro Prefixado 2027",  "LTN"),
        ("Desconhecido",            "OUTRO"),
    ])
    def test_parse_bond_type(self, nome, esperado):
        assert _parse_bond_type(nome) == esperado

    def test_parse_campos_numericos(self):
        bond = _parse_tesouro_bond(_TESOURO_RAW[0])
        assert bond is not None
        assert bond.rate      == pytest.approx(12.35)
        assert bond.price     == pytest.approx(14523.45)
        assert bond.maturity  == date(2029, 3, 1)
        assert bond.min_amount == pytest.approx(41.65)


class TestTesouroBonds:

    def test_get_retorna_lista_de_bonds(self, svc):
        with patch("core.market_data._fetch_tesouro_raw", return_value=_TESOURO_RAW):
            bonds = svc.get_tesouro_bonds()
        assert len(bonds) == 3
        assert all(isinstance(b, TesouroBond) for b in bonds)

    def test_nomes_corretos(self, svc):
        with patch("core.market_data._fetch_tesouro_raw", return_value=_TESOURO_RAW):
            bonds = svc.get_tesouro_bonds()
        names = {b.name for b in bonds}
        assert "Tesouro Selic 2029" in names
        assert "Tesouro IPCA+ 2035" in names

    def test_salvo_no_cache_apos_api(self, svc, cache):
        with patch("core.market_data._fetch_tesouro_raw", return_value=_TESOURO_RAW):
            svc.get_tesouro_bonds()
        cached = cache.get("tesouro:bonds")
        assert cached is not None
        assert len(cached) == 3

    def test_servido_do_cache_sem_chamar_api(self, svc, cache):
        with patch("core.market_data._fetch_tesouro_raw", return_value=_TESOURO_RAW):
            svc.get_tesouro_bonds()
        mock_fetch = MagicMock()
        with patch("core.market_data._fetch_tesouro_raw", mock_fetch):
            bonds = svc.get_tesouro_bonds()
        mock_fetch.assert_not_called()
        assert len(bonds) == 3

    def test_usa_fallback_quando_api_falha(self, svc, cache):
        with patch("core.market_data._fetch_tesouro_raw", return_value=_TESOURO_RAW):
            svc.get_tesouro_bonds()
        cache.invalidate("tesouro:bonds")
        with patch("core.market_data._fetch_tesouro_raw", side_effect=RuntimeError("timeout")):
            bonds = svc.get_tesouro_bonds()
        assert len(bonds) == 3

    def test_lista_vazia_sem_cache_e_api_fora(self, svc):
        with patch("core.market_data._fetch_tesouro_raw", side_effect=RuntimeError("timeout")):
            assert svc.get_tesouro_bonds() == []
