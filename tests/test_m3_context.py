from __future__ import annotations

import pytest
from core.m3_context import Confidence, MarketRegime, ajustar_prudencia


class TestAjustarPrudencia:
    def test_risk_on_moderate_nao_altera_muito(self):
        ajustado = ajustar_prudencia(0.80, MarketRegime.RISK_ON, Confidence.MODERATE)
        assert ajustado < 0.80  # sempre reduz ou mantém
        assert ajustado > 0.60  # não reduz demais

    def test_liquidiy_crisis_reduz_significativamente(self):
        base = 0.80
        ajustado = ajustar_prudencia(base, MarketRegime.LIQUIDITY_CRISIS, Confidence.LOW)
        assert ajustado < base * 0.65

    def test_contexto_nunca_aumenta_score(self):
        base = 0.50
        for regime in MarketRegime:
            for conf in Confidence:
                ajustado = ajustar_prudencia(base, regime, conf)
                assert ajustado <= base, f"Score aumentou: {regime} / {conf}"

    def test_score_sempre_positivo(self):
        ajustado = ajustar_prudencia(0.10, MarketRegime.LIQUIDITY_CRISIS, Confidence.VERY_LOW)
        assert ajustado >= 0.0
