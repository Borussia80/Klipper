from __future__ import annotations

import pytest
from models.investment import Investment, InvestmentType
from core.fragility import calcular_fragility_score, reduzir_exposicao_por_fragilidade


def _inv(liquidity_daily: float = 500_000) -> Investment:
    return Investment(
        ticker="TEST11", type=InvestmentType.FII,
        quantity=100, avg_price=10.0, current_price=10.0,
        liquidity_daily=liquidity_daily,
    )


class TestCalcularFragilityScore:
    def test_score_entre_zero_e_um(self):
        inv = _inv()
        fb = calcular_fragility_score(inv)
        assert 0.0 <= fb.total <= 1.0

    def test_liquidez_alta_reduz_fragilidade(self):
        inv_liquido = _inv(liquidity_daily=1_000_000)
        inv_iliquido = _inv(liquidity_daily=10_000)
        fb_liq = calcular_fragility_score(inv_liquido)
        fb_iliq = calcular_fragility_score(inv_iliquido)
        assert fb_liq.total < fb_iliq.total

    def test_concentracao_alta_aumenta_fragilidade(self):
        inv = _inv()
        fb_baixa = calcular_fragility_score(inv, peso_portfolio_pct=1.0)
        fb_alta = calcular_fragility_score(inv, peso_portfolio_pct=9.0)
        assert fb_alta.total > fb_baixa.total

    def test_componentes_somam_corretamente(self):
        inv = _inv(liquidity_daily=500_000)
        fb = calcular_fragility_score(
            inv, peso_portfolio_pct=5.0,
            risco_regulatorio=0.3, governanca=0.4,
            estabilidade_caixa=0.5, dependencia_credito=0.2,
        )
        esperado = round(
            fb.liquidez * 0.25 + fb.governanca * 0.20 + fb.concentracao * 0.20
            + fb.risco_regulatorio * 0.15 + fb.estabilidade_caixa * 0.10
            + fb.dependencia_credito * 0.10, 4
        )
        assert abs(fb.total - esperado) < 0.001


class TestReduzirExposicaoPorFragilidade:
    def test_fragilidade_zero_nao_altera_score(self):
        score = reduzir_exposicao_por_fragilidade(0.70, fragility_total=0.0)
        assert score == pytest.approx(0.70)

    def test_fragilidade_maxima_reduz_score_significativamente(self):
        score_original = 0.80
        score = reduzir_exposicao_por_fragilidade(score_original, fragility_total=1.0)
        assert score < score_original
        assert score == pytest.approx(score_original - 0.40, abs=0.01)

    def test_score_nunca_fica_negativo(self):
        score = reduzir_exposicao_por_fragilidade(0.10, fragility_total=1.0)
        assert score >= 0.0

    def test_fragilidade_moderada_reduz_proporcionalmente(self):
        score_original = 0.70
        score = reduzir_exposicao_por_fragilidade(score_original, fragility_total=0.5)
        assert score < score_original
        assert score > 0.0
