from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.investment import Investment


@dataclass
class FragilityBreakdown:
    liquidez: float
    governanca: float
    concentracao: float
    risco_regulatorio: float
    estabilidade_caixa: float
    dependencia_credito: float
    total: float


def calcular_fragility_score(
    inv: Investment,
    peso_portfolio_pct: float = 0.0,
    risco_regulatorio: float = 0.0,
    governanca: float = 0.5,
    estabilidade_caixa: float = 0.5,
    dependencia_credito: float = 0.5,
) -> FragilityBreakdown:
    """
    Calcula Fragility Score (0 = sólido, 1 = frágil).
    Fragilidade alta reduz exposição mesmo com score M1 elevado.

    Parâmetros subjetivos (0.0–1.0) devem ser estimados pelo usuário.
    """
    # Liquidez: baixa liquidez = alta fragilidade
    score_liquidez = max(0.0, 1.0 - inv.liquidity_daily / 1_000_000)

    # Concentração no portfólio
    score_concentracao = min(peso_portfolio_pct / 10.0, 1.0)

    total = round(
        score_liquidez * 0.25
        + governanca * 0.20
        + score_concentracao * 0.20
        + risco_regulatorio * 0.15
        + estabilidade_caixa * 0.10
        + dependencia_credito * 0.10,
        4,
    )

    return FragilityBreakdown(
        liquidez=round(score_liquidez, 4),
        governanca=round(governanca, 4),
        concentracao=round(score_concentracao, 4),
        risco_regulatorio=round(risco_regulatorio, 4),
        estabilidade_caixa=round(estabilidade_caixa, 4),
        dependencia_credito=round(dependencia_credito, 4),
        total=total,
    )


def reduzir_exposicao_por_fragilidade(
    score_m1: float, fragility_total: float
) -> float:
    """
    Reduz o score M1 baseado na fragilidade.
    Fragilidade alta (> 0.7) reduz exposição mesmo com M1 elevado.
    """
    reducao = fragility_total * 0.40  # fragilidade máxima reduz 40% do score
    return round(max(0.0, score_m1 - reducao), 4)
