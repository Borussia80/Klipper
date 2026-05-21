from __future__ import annotations

import pytest
from models.investment import Investment, InvestmentType
from core.m2_governance import (
    verificar_limites, hard_fail,
    MAX_ATIVO_PCT, MAX_TESE_PCT, CAIXA_MIN_PCT,
)


def _inv(ticker: str, valor: float, setor: str = "Papel") -> Investment:
    preco = 10.0
    return Investment(
        ticker=ticker, type=InvestmentType.FII,
        quantity=valor / preco, avg_price=preco, current_price=preco,
        sector=setor,
    )


class TestVerificarLimites:
    def test_sem_alertas_portfolio_saudavel(self):
        # Total = 10000: cada ativo = 500 (5%), caixa = 3000 (30%), setores distintos
        portfolio = [
            _inv("MXRF11", 500, "Papel"),
            _inv("HGLG11", 500, "Logística"),
            _inv("VISC11", 500, "Shoppings"),
            _inv("KNRI11", 500, "Híbrido"),
        ]
        alertas = verificar_limites(portfolio, caixa_disponivel=3000)
        assert alertas == []

    def test_caixa_abaixo_do_minimo_gera_hard_fail(self):
        portfolio = [_inv("MXRF11", 900)]
        # caixa = 100, total = 1000 → 10% < 20% mínimo
        alertas = verificar_limites(portfolio, caixa_disponivel=100)
        codigos = [a.code for a in alertas]
        assert "M2_CAIXA" in codigos
        assert any(a.is_hard_fail for a in alertas if a.code == "M2_CAIXA")

    def test_ativo_acima_de_10pct_gera_hard_fail(self):
        # ativo = 1100, total = 2000 → 55% > 10%
        portfolio = [_inv("MXRF11", 1100), _inv("XPLG11", 500)]
        alertas = verificar_limites(portfolio, caixa_disponivel=400)
        codigos = [a.code for a in alertas]
        assert "M2_CONCENTRACAO_ATIVO" in codigos

    def test_setor_acima_de_25pct_gera_hard_fail(self):
        # Papel: 3000 de 4000 total = 75% > 25%
        portfolio = [
            _inv("MXRF11", 1500, "Papel"),
            _inv("KNCR11", 1500, "Papel"),
            _inv("HGLG11", 500, "Logística"),
        ]
        alertas = verificar_limites(portfolio, caixa_disponivel=500)
        codigos = [a.code for a in alertas]
        assert "M2_CONCENTRACAO_TESE" in codigos

    def test_portfolio_vazio_sem_alertas(self):
        alertas = verificar_limites([], caixa_disponivel=5000)
        assert alertas == []


class TestHardFail:
    def test_sem_hard_fail(self):
        portfolio = [_inv("MXRF11", 500)]
        alertas = verificar_limites(portfolio, caixa_disponivel=5000)
        falhou, motivo = hard_fail(alertas)
        assert not falhou
        assert motivo == ""

    def test_com_hard_fail_retorna_motivo(self):
        # caixa zero → hard fail
        portfolio = [_inv("MXRF11", 1000)]
        alertas = verificar_limites(portfolio, caixa_disponivel=0)
        falhou, motivo = hard_fail(alertas)
        assert falhou
        assert len(motivo) > 0
