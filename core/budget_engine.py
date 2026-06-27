"""core/budget_engine.py — Motor de orçamento: 50/30/20, burn-rate e alertas.

Regras:
  - 50/30/20: necessidades 50%, desejos 30%, poupança/investimento 20%
  - Burn-rate separa fixo (recorrentes + parcelas) de variável
  - Alertas: > 80% gasto com > 15 dias restantes, ou já estourado
  - Sem side-effects: funções puras que recebem dados prontos
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date as Date
from decimal import Decimal
from typing import Sequence

from models.budget import Budget
from models.transaction import Transaction, TransactionType


# ── Categorias por pilar 50/30/20 ────────────────────────────────────────────

NEEDS_CATEGORIES  = {"Moradia", "Alimentação", "Transporte", "Saúde", "Educação"}
WANTS_CATEGORIES  = {"Lazer", "Outros"}
INVEST_CATEGORIES = {"Investimento"}


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class BurnRate:
    fixed_total:    Decimal
    variable_total: Decimal
    variable_daily: Decimal
    days_elapsed:   int
    days_in_month:  int

    @property
    def projected_close(self) -> Decimal:
        if self.days_in_month == 0:
            return self.variable_total
        remaining_days = self.days_in_month - self.days_elapsed
        return self.variable_total + self.variable_daily * remaining_days


@dataclass(frozen=True)
class BudgetAlert:
    category: str
    pct_used: float
    amount_spent: Decimal
    monthly_limit: Decimal
    overbudget: bool
    days_remaining: int


@dataclass(frozen=True)
class BudgetStatus:
    category: str
    monthly_limit: Decimal
    spent: Decimal
    pct_used: float
    projected_close: Decimal


# ── suggest_50_30_20 ──────────────────────────────────────────────────────────

def suggest_50_30_20(
    monthly_income: Decimal,
    categories: Sequence[str],
) -> dict[str, Decimal]:
    """Distributes `monthly_income` across categories using the 50/30/20 rule.

    Returns a dict category → suggested limit. Only includes categories passed
    in `categories` — unknown categories are ignored gracefully.
    """
    if monthly_income <= 0:
        return {}

    needs_budget  = monthly_income * Decimal("0.5")
    wants_budget  = monthly_income * Decimal("0.3")
    invest_budget = monthly_income * Decimal("0.2")

    needs_cats  = [c for c in categories if c in NEEDS_CATEGORIES]
    wants_cats  = [c for c in categories if c in WANTS_CATEGORIES]
    invest_cats = [c for c in categories if c in INVEST_CATEGORIES]

    result: dict[str, Decimal] = {}

    def _split_evenly(cats: list[str], total: Decimal) -> None:
        if not cats:
            return
        per_cat = (total / Decimal(len(cats))).quantize(Decimal("0.01"))
        for c in cats:
            result[c] = per_cat

    _split_evenly(needs_cats,  needs_budget)
    _split_evenly(wants_cats,  wants_budget)
    _split_evenly(invest_cats, invest_budget)

    return result


# ── calcular_burn_rate ────────────────────────────────────────────────────────

def calcular_burn_rate(
    txs:          Sequence[Transaction],
    year:         int,
    month:        int,
    today:        Date | None = None,
) -> BurnRate:
    """Separates spending into fixed (recurring) and variable for the month."""
    today = today or Date.today()
    days_in_month = calendar.monthrange(year, month)[1]
    days_elapsed  = max(today.day, 1) if today.month == month and today.year == year else days_in_month

    gastos = [t for t in txs if t.type == TransactionType.GASTO]
    fixed   = sum((t.amount for t in gastos if getattr(t, "is_recurring", False) or t.installment_id), Decimal(0))
    variable = sum((t.amount for t in gastos if not getattr(t, "is_recurring", False) and not t.installment_id), Decimal(0))

    daily = variable / Decimal(days_elapsed) if days_elapsed > 0 else Decimal(0)

    return BurnRate(
        fixed_total=fixed,
        variable_total=variable,
        variable_daily=daily.quantize(Decimal("0.01")),
        days_elapsed=days_elapsed,
        days_in_month=days_in_month,
    )


# ── gerar_alertas ─────────────────────────────────────────────────────────────

ALERT_THRESHOLD = 0.80  # 80% consumed
ALERT_DAYS_AHEAD = 15   # only alert if > 15 days remaining


def gerar_alertas(
    budgets:    Sequence[Budget],
    spent_map:  dict[str, Decimal],
    today:      Date | None = None,
) -> list[BudgetAlert]:
    """Returns alerts for categories that are over budget or approaching the limit early."""
    today = today or Date.today()
    days_in_month  = calendar.monthrange(today.year, today.month)[1]
    days_remaining = days_in_month - today.day

    alerts: list[BudgetAlert] = []
    for b in budgets:
        spent = spent_map.get(b.category, Decimal(0))
        if b.monthly_limit <= 0:
            continue
        pct = float(spent / b.monthly_limit)
        overbudget = spent > b.monthly_limit

        if overbudget or (pct >= ALERT_THRESHOLD and days_remaining > ALERT_DAYS_AHEAD):
            alerts.append(BudgetAlert(
                category=b.category,
                pct_used=round(pct, 4),
                amount_spent=spent,
                monthly_limit=b.monthly_limit,
                overbudget=overbudget,
                days_remaining=days_remaining,
            ))

    return sorted(alerts, key=lambda a: (-float(a.pct_used), a.category))


# ── budget_status ─────────────────────────────────────────────────────────────

def calcular_budget_status(
    budgets:  Sequence[Budget],
    txs:      Sequence[Transaction],
    year:     int,
    month:    int,
    today:    Date | None = None,
) -> list[BudgetStatus]:
    """Returns status for each budget including projected close."""
    today = today or Date.today()
    burn  = calcular_burn_rate(txs, year, month, today)

    spent_map: dict[str, Decimal] = {}
    for t in txs:
        if t.type == TransactionType.GASTO:
            spent_map[t.category] = spent_map.get(t.category, Decimal(0)) + t.amount

    statuses: list[BudgetStatus] = []
    for b in budgets:
        spent = spent_map.get(b.category, Decimal(0))
        pct   = float(spent / b.monthly_limit) if b.monthly_limit > 0 else 0.0
        # Projected close: spent + remaining days * daily variable rate for this category
        projected = spent + burn.variable_daily * Decimal(burn.days_in_month - burn.days_elapsed)
        statuses.append(BudgetStatus(
            category=b.category,
            monthly_limit=b.monthly_limit,
            spent=spent,
            pct_used=round(pct, 4),
            projected_close=projected.quantize(Decimal("0.01")),
        ))

    return statuses
