from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DebtRisk(str, Enum):
    BAIXO = "BAIXO"
    ATENCAO = "ATENCAO"
    ALTO = "ALTO"
    CRITICO = "CRITICO"


@dataclass(frozen=True)
class DebtSummary:
    principal: float
    installment_amount: float
    n_installments: int
    total_paid: float
    total_interest_and_fees: float
    monthly_cet_pct: float
    annual_cet_pct: float


def estimate_cet(
    principal: float,
    installment_amount: float,
    n_installments: int,
) -> DebtSummary:
    if principal <= 0:
        raise ValueError("principal deve ser positivo")
    if installment_amount <= 0:
        raise ValueError("installment_amount deve ser positivo")
    if n_installments < 1:
        raise ValueError("n_installments deve ser ≥ 1")

    monthly_rate = _solve_monthly_rate(principal, installment_amount, n_installments)
    total_paid = round(installment_amount * n_installments, 2)
    monthly_pct = round(monthly_rate * 100, 4)
    annual_pct = round(((1 + monthly_rate) ** 12 - 1) * 100, 4)
    return DebtSummary(
        principal=round(principal, 2),
        installment_amount=round(installment_amount, 2),
        n_installments=n_installments,
        total_paid=total_paid,
        total_interest_and_fees=round(total_paid - principal, 2),
        monthly_cet_pct=monthly_pct,
        annual_cet_pct=annual_pct,
    )


def classify_debt_burden(monthly_debt_payments: float, monthly_income: float) -> DebtRisk:
    if monthly_income <= 0:
        return DebtRisk.CRITICO if monthly_debt_payments > 0 else DebtRisk.BAIXO
    burden = monthly_debt_payments / monthly_income
    if burden >= 0.45:
        return DebtRisk.CRITICO
    if burden >= 0.30:
        return DebtRisk.ALTO
    if burden >= 0.15:
        return DebtRisk.ATENCAO
    return DebtRisk.BAIXO


def _solve_monthly_rate(principal: float, payment: float, periods: int) -> float:
    if payment * periods <= principal:
        return 0.0

    low = 0.0
    high = 1.0
    while _present_value(payment, periods, high) > principal:
        high *= 2
        if high > 100:
            break

    for _ in range(80):
        mid = (low + high) / 2
        pv = _present_value(payment, periods, mid)
        if pv > principal:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _present_value(payment: float, periods: int, rate: float) -> float:
    if rate == 0:
        return payment * periods
    return payment * (1 - (1 + rate) ** -periods) / rate
