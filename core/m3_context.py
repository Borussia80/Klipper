from __future__ import annotations

from enum import Enum


class MarketRegime(str, Enum):
    RISK_ON = "RISK_ON"
    RISK_OFF = "RISK_OFF"
    CREDIT_STRESS = "CREDIT_STRESS"
    LIQUIDITY_CRISIS = "LIQUIDITY_CRISIS"
    EUPHORIA = "EUPHORIA"


class Confidence(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Multiplicadores de prudência por regime
# "Contexto não compra ativo. Contexto altera prudência."
_REGIME_MULTIPLIER: dict[MarketRegime, float] = {
    MarketRegime.RISK_ON: 1.00,
    MarketRegime.EUPHORIA: 0.85,       # cautela extra em euforia
    MarketRegime.RISK_OFF: 0.90,
    MarketRegime.CREDIT_STRESS: 0.75,
    MarketRegime.LIQUIDITY_CRISIS: 0.60,
}

_CONFIDENCE_MULTIPLIER: dict[Confidence, float] = {
    Confidence.CRITICAL: 1.00,
    Confidence.HIGH: 0.95,
    Confidence.MODERATE: 0.88,
    Confidence.LOW: 0.78,
    Confidence.VERY_LOW: 0.65,
}


def ajustar_prudencia(
    score_base: float,
    regime: MarketRegime,
    confidence: Confidence,
) -> float:
    """
    Aplica multiplicadores de contexto ao score M1.
    Nunca eleva o score — apenas reduz conforme prudência.
    """
    regime_mult = _REGIME_MULTIPLIER[regime]
    conf_mult = _CONFIDENCE_MULTIPLIER[confidence]
    ajustado = score_base * regime_mult * conf_mult
    return round(min(ajustado, score_base), 4)
