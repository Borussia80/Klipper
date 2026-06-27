"""api/routers/budget.py — Motor de orçamento: sugestão 50/30/20, status e alertas."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field


from api.auth import CurrentUser
from api.logging_config import get_logger

logger = get_logger(__name__)
from core.budget_engine import (
    BudgetAlert,
    BudgetStatus,
    calcular_budget_status,
    gerar_alertas,
    suggest_50_30_20,
)
from core.repositories import BudgetRepository, TransactionRepository

router = APIRouter(prefix="/budget", tags=["budget"])


class SuggestRequest(BaseModel):
    monthly_income: float = Field(gt=0)
    categories:     list[str]


@router.post("/suggest")
async def budget_suggest(body: SuggestRequest, _user: CurrentUser) -> dict[str, float]:
    """Retorna sugestão 50/30/20 por categoria."""
    result = suggest_50_30_20(
        Decimal(str(body.monthly_income)),
        body.categories,
    )
    return {k: float(v) for k, v in result.items()}


def _status_to_dict(s: BudgetStatus) -> dict[str, Any]:
    return {
        "category":       s.category,
        "monthly_limit":  float(s.monthly_limit),
        "spent":          float(s.spent),
        "pct_used":       s.pct_used,
        "projected_close": float(s.projected_close),
    }


def _alert_to_dict(a: BudgetAlert) -> dict[str, Any]:
    return {
        "category":      a.category,
        "pct_used":      a.pct_used,
        "amount_spent":  float(a.amount_spent),
        "monthly_limit": float(a.monthly_limit),
        "overbudget":    a.overbudget,
        "days_remaining": a.days_remaining,
        "message": (
            f"Orçamento estourado em {a.category}!"
            if a.overbudget
            else f"{a.category}: {round(a.pct_used * 100)}% usado com {a.days_remaining} dias restantes."
        ),
    }


@router.get("/status")
async def budget_status(_user: CurrentUser) -> list[dict[str, Any]]:
    """Retorna status de gastos vs. limite para o mês corrente."""
    today = date.today()
    budgets = BudgetRepository().list_by_month(today.year, today.month)
    txs     = TransactionRepository().list_by_month(today.year, today.month)
    statuses = calcular_budget_status(budgets, txs, today.year, today.month, today)
    return [_status_to_dict(s) for s in statuses]


@router.get("/alerts")
async def budget_alerts(_user: CurrentUser) -> list[dict[str, Any]]:
    """Retorna alertas de categorias acima de 80% ou estouradas."""
    today = date.today()
    budgets = BudgetRepository().list_by_month(today.year, today.month)
    txs     = TransactionRepository().list_by_month(today.year, today.month)

    spent_map: dict[str, Decimal] = {}
    for t in txs:
        from models.transaction import TransactionType
        if t.type == TransactionType.GASTO:
            spent_map[t.category] = spent_map.get(t.category, Decimal(0)) + t.amount

    alerts = gerar_alertas(budgets, spent_map, today)
    return [_alert_to_dict(a) for a in alerts]
