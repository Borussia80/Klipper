from __future__ import annotations

import pytest
from core.m1_quant import calcular_score_m1, classificar_score, Decisao


class TestCalcularScoreM1:
    def test_score_perfeito(self):
        score = calcular_score_m1(dy=15.0, pvp=0.4, liquidez=1_000_000, volatilidade=0, spread_cdi=5.0)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_score_zero(self):
        score = calcular_score_m1(dy=0, pvp=2.0, liquidez=0, volatilidade=60, spread_cdi=-5)
        assert score == pytest.approx(0.0, abs=0.05)

    def test_score_entre_limites(self):
        score = calcular_score_m1(dy=8.0, pvp=0.9, liquidez=300_000, volatilidade=15, spread_cdi=2.0)
        assert 0.0 <= score <= 1.0

    def test_dy_alto_nao_ultrapassa_1(self):
        score = calcular_score_m1(dy=99.0, pvp=0.5, liquidez=500_000, volatilidade=5, spread_cdi=3.0)
        assert score <= 1.0


class TestClassificarScore:
    def test_score_alto_comprar(self):
        assert classificar_score(0.65) == Decisao.COMPRAR

    def test_score_medio_manter(self):
        assert classificar_score(0.45) == Decisao.MANTER

    def test_score_baixo_reduzir(self):
        assert classificar_score(0.20) == Decisao.REDUZIR

    def test_limiar_exato_comprar(self):
        assert classificar_score(0.60) == Decisao.COMPRAR

    def test_limiar_exato_reduzir(self):
        assert classificar_score(0.30) == Decisao.MANTER
