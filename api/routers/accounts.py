"""api/routers/accounts.py — Consultas financeiras de contas e parcelamentos.

CRUD de contas/cartões vai direto pelo supabase-js no front.
Esta API provê apenas as consultas que requerem lógica de negócio Python:
- GET /accounts/invoice  → fatura vigente de um cartão
- GET /accounts/commitment → dicionário mensal de comprometimento de parcelamentos
"""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, Query


from api.auth import CurrentUser
from api.logging_config import get_logger

logger = get_logger(__name__)
from core.database import get_client
from core.credit_card_billing import invoice_by_due_month
from core.installment_engine import calcular_comprometimento_mensal
from core.repositories import CreditCardRepository, InstallmentRepository, TransactionRepository

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/invoice")
async def get_invoice(
    card_id: str,
    user_id: CurrentUser,
    year:  int = Query(default=0),
    month: int = Query(default=0),
) -> dict[str, Any]:
    """Retorna os totais da fatura vigente (ou do mês especificado) para um cartão."""
    today = date.today()
    yr  = year  or today.year
    mon = month or today.month

    card = CreditCardRepository().get_by_id(card_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Cartão {card_id} não encontrado")

    repo = TransactionRepository()
    txs  = repo.list_by_card(card_id, yr, mon)

    invoice = invoice_by_due_month(card, txs, yr, mon)

    return {
        "card_id":      card_id,
        "year":         yr,
        "month":        mon,
        "total":        float(invoice.total),
        "count":        invoice.count,
        "closing_date": invoice.closing_date.isoformat(),
        "due_date":     invoice.due_date.isoformat(),
    }


@router.get("/commitment")
async def get_commitment(user_id: CurrentUser) -> dict[str, float]:
    """Retorna dicionário YYYY-MM → total de comprometimento de parcelamentos ativos."""
    installments = InstallmentRepository().list_active()
    raw = calcular_comprometimento_mensal(installments)
    return {k: float(v) for k, v in raw.items()}
