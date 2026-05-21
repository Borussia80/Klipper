from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from models.investment import Investment, InvestmentType


class LiquidityBucket(str, Enum):
    IMEDIATA = "IMEDIATA"
    CURTA = "CURTA"
    TRAVADA = "TRAVADA"


@dataclass(frozen=True)
class EmergencyReserve:
    immediate: float
    short_term: float
    locked: float
    eligible_total: float
    monthly_expenses: float
    coverage_months: float
    status: str


def classify_liquidity(inv: Investment) -> LiquidityBucket:
    if inv.type == InvestmentType.CAIXA or inv.liquidity_days <= 1:
        return LiquidityBucket.IMEDIATA
    if inv.liquidity_days <= 30:
        return LiquidityBucket.CURTA
    return LiquidityBucket.TRAVADA


def calculate_emergency_reserve(
    investments: list[Investment],
    monthly_expenses: float,
    target_months: float = 6.0,
) -> EmergencyReserve:
    if monthly_expenses < 0:
        raise ValueError("monthly_expenses não pode ser negativo")
    if target_months <= 0:
        raise ValueError("target_months deve ser positivo")

    totals = {
        LiquidityBucket.IMEDIATA: 0.0,
        LiquidityBucket.CURTA: 0.0,
        LiquidityBucket.TRAVADA: 0.0,
    }
    for inv in investments:
        totals[classify_liquidity(inv)] += inv.current_value

    immediate = round(totals[LiquidityBucket.IMEDIATA], 2)
    short_term = round(totals[LiquidityBucket.CURTA], 2)
    locked = round(totals[LiquidityBucket.TRAVADA], 2)
    eligible = round(immediate + short_term, 2)
    coverage = round(eligible / monthly_expenses, 2) if monthly_expenses > 0 else 0.0

    if coverage >= target_months:
        status = "OK"
    elif coverage >= target_months / 2:
        status = "ATENCAO"
    else:
        status = "CRITICO"

    return EmergencyReserve(
        immediate=immediate,
        short_term=short_term,
        locked=locked,
        eligible_total=eligible,
        monthly_expenses=round(monthly_expenses, 2),
        coverage_months=coverage,
        status=status,
    )
