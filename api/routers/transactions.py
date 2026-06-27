"""api/routers/transactions.py — Gateway de escrita de transações.

Esteira atômica (spec fase-0.5 §2.2):
  1. Validar  →  HTTP 422 se inválido
  2. Categorizar  →  sempre consulta o motor fuzzy (retornado na resposta para contexto)
  3. Persistir  →  simples | parcelado | rateado | parcelado+rateado
  4. Ajustar saldo  →  apenas débito/PIX; cartão de crédito não toca no saldo imediatamente
  5. Gravar memória  →  somente quando confirmed=True

Todas as escritas com regra de negócio passam por aqui.
CRUD simples (conta, cartão, config) usa supabase-js direto.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator


from api.auth import CurrentUser
from api.logging_config import get_logger

logger = get_logger(__name__)
from core.database import get_client
from core.installment_engine import gerar_parcelas
from core.repositories import CategoryMemoryRepository, categorize_with_memory
from core.split_utils import distribuir_splits_proporcional
from models.installment import Installment
from models.transaction import Category

router = APIRouter(prefix="/transactions", tags=["transactions"])

_DEBIT_METHODS = {"PIX", "CARTAO_DEBITO", "DINHEIRO", "TED", "BOLETO", "TRANSFERENCIA"}


# ── Request / Response schemas ────────────────────────────────────────────────

class SplitInput(BaseModel):
    category: str
    amount: float = Field(gt=0)


class TxCreateRequest(BaseModel):
    date: str
    amount: float = Field(gt=0)
    type: str
    notes: str = ""
    payment_method: str
    account_id: str | None = None
    card_id: str | None = None
    category: str | None = None
    confirmed: bool = False
    is_recurring: bool = False
    n_installments: int = Field(default=1, ge=1)
    splits: list[SplitInput] | None = None

    @model_validator(mode="after")
    def validate_business_rules(self) -> "TxCreateRequest":
        try:
            tx_date = date.fromisoformat(self.date)
        except ValueError as exc:
            raise ValueError("date inválida — use formato ISO (YYYY-MM-DD)") from exc

        if tx_date > date.today() + timedelta(days=90):
            raise ValueError("date não pode ser mais de 90 dias no futuro")

        if not self.account_id and not self.card_id:
            raise ValueError("account_id ou card_id é obrigatório")

        if self.card_id and self.payment_method != "CARTAO_CREDITO":
            raise ValueError("card_id requer payment_method CARTAO_CREDITO")

        if self.n_installments > 1 and not self.card_id:
            raise ValueError("n_installments > 1 requer card_id")

        if self.splits:
            total_splits = round(sum(s.amount for s in self.splits), 2)
            if abs(total_splits - round(self.amount, 2)) > 0.001:
                raise ValueError(
                    f"splits somam {total_splits:.2f} mas amount é {self.amount:.2f}"
                )

        return self


# ── helpers internos ──────────────────────────────────────────────────────────

def _tx_row(body: TxCreateRequest, category: str, user_id: str, inst_id: str | None = None, notes: str | None = None, tx_date: str | None = None, amount: str | None = None, status: str = "PAGO") -> dict[str, Any]:
    return {
        "date":             tx_date or body.date,
        "amount":           amount or str(body.amount),
        "type":             body.type,
        "category":         category,
        "notes":            notes if notes is not None else body.notes,
        "payment_method":   body.payment_method,
        "account_id":       body.account_id,
        "card_id":          body.card_id,
        "installment_id":   inst_id,
        "is_recurring":     body.is_recurring,
        "status":           status,
        "user_id":          user_id,
    }


def _persist_simple(db: Any, body: TxCreateRequest, category: str, user_id: str) -> tuple[dict, list, list]:
    row = _tx_row(body, category, user_id)
    result = db.table("transactions").insert(row).execute()
    rows = result.data if isinstance(result.data, list) else [result.data]
    return rows[0], [], []


def _persist_simple_with_splits(db: Any, body: TxCreateRequest, user_id: str) -> tuple[dict, list, list]:
    row = _tx_row(body, "Rateado", user_id)
    result = db.table("transactions").insert(row).execute()
    rows = result.data if isinstance(result.data, list) else [result.data]
    tx_id = rows[0]["id"]

    split_rows = [
        {"transaction_id": tx_id, "category": s.category, "amount": str(s.amount), "user_id": user_id}
        for s in (body.splits or [])
    ]
    db.table("transaction_splits").insert(split_rows).execute()

    splits_out = [{"category": s.category, "amount": s.amount} for s in (body.splits or [])]
    return rows[0], [], splits_out


def _persist_installments(db: Any, body: TxCreateRequest, category: str, user_id: str) -> tuple[dict, list, list]:
    inst_row = {
        "description":        body.notes or body.category or "Compra parcelada",
        "total_amount":       str(body.amount),
        "n_total":            body.n_installments,
        "n_paid":             0,
        "installment_amount": str(round(body.amount / body.n_installments, 2)),
        "start_date":         body.date,
        "card_id":            body.card_id,
        "account_id":         body.account_id,
        "category":           category,
        "user_id":            user_id,
    }
    inst_result = db.table("installments").insert(inst_row).execute()
    inst_id = inst_result.data[0]["id"]

    inst = Installment(
        id=inst_id,
        description=inst_row["description"],
        total_amount=Decimal(str(body.amount)),
        n_total=body.n_installments,
        start_date=date.fromisoformat(body.date),
        card_id=body.card_id,
        account_id=body.account_id,
        category=category,
    )
    parcelas = gerar_parcelas(inst)

    tx_rows = [
        _tx_row(body, category, user_id,
                inst_id=inst_id,
                notes=p.notes,
                tx_date=str(p.date),
                amount=str(p.amount),
                status=p.status.value)
        for p in parcelas
    ]
    result = db.table("transactions").insert(tx_rows).execute()
    rows = result.data if isinstance(result.data, list) else [result.data]
    return rows[0], rows[1:], []


def _persist_installments_with_splits(db: Any, body: TxCreateRequest, user_id: str) -> tuple[dict, list, list]:
    description = body.notes or "Compra parcelada"
    inst_row = {
        "description":        description,
        "total_amount":       str(body.amount),
        "n_total":            body.n_installments,
        "n_paid":             0,
        "installment_amount": str(round(body.amount / body.n_installments, 2)),
        "start_date":         body.date,
        "card_id":            body.card_id,
        "account_id":         body.account_id,
        "category":           "Rateado",
        "user_id":            user_id,
    }
    inst_result = db.table("installments").insert(inst_row).execute()
    inst_id = inst_result.data[0]["id"]

    inst = Installment(
        id=inst_id,
        description=description,
        total_amount=Decimal(str(body.amount)),
        n_total=body.n_installments,
        start_date=date.fromisoformat(body.date),
        card_id=body.card_id,
        account_id=body.account_id,
        category="Outros",
    )
    parcelas = gerar_parcelas(inst)

    tx_rows = [
        _tx_row(body, "Rateado", user_id,
                inst_id=inst_id,
                notes=p.notes,
                tx_date=str(p.date),
                amount=str(p.amount),
                status=p.status.value)
        for p in parcelas
    ]
    result = db.table("transactions").insert(tx_rows).execute()
    rows = result.data if isinstance(result.data, list) else [result.data]

    total = Decimal(str(body.amount))
    splits_input = [{"category": s.category, "amount": Decimal(str(s.amount))} for s in (body.splits or [])]

    all_split_rows: list[dict] = []
    splits_per_tx: dict[str, list] = {}

    for p, row in zip(parcelas, rows):
        tx_id = row["id"]
        proportional = distribuir_splits_proporcional(splits_input, p.amount, total)
        tx_splits = []
        for split_def, amt in zip(body.splits or [], proportional):
            all_split_rows.append({
                "transaction_id": tx_id,
                "category":       split_def.category,
                "amount":         str(amt),
                "user_id":        user_id,
            })
            tx_splits.append({"category": split_def.category, "amount": float(amt)})
        splits_per_tx[tx_id] = tx_splits

    if all_split_rows:
        db.table("transaction_splits").insert(all_split_rows).execute()

    def _enrich(row: dict) -> dict:
        return {**row, "splits": splits_per_tx.get(row["id"], [])}

    main = _enrich(rows[0])
    children = [_enrich(r) for r in rows[1:]]
    return main, children, splits_per_tx.get(rows[0]["id"], [])


# ── endpoint ──────────────────────────────────────────────────────────────────

@router.post("", status_code=201)
async def create_transaction(body: TxCreateRequest, user_id: CurrentUser) -> dict:
    db = get_client()

    # 2. Categorizar — sempre chama o motor para retornar a sugestão contextual
    suggestion = categorize_with_memory(body.notes, user_id)
    final_category = body.category or suggestion.category.value

    # 3. Persistir
    has_splits = bool(body.splits)
    is_installment = body.n_installments > 1

    if not is_installment and not has_splits:
        main_tx, children, splits_out = _persist_simple(db, body, final_category, user_id)
    elif is_installment and not has_splits:
        main_tx, children, splits_out = _persist_installments(db, body, final_category, user_id)
    elif has_splits and not is_installment:
        main_tx, children, splits_out = _persist_simple_with_splits(db, body, user_id)
    else:
        main_tx, children, splits_out = _persist_installments_with_splits(db, body, user_id)

    # 4. Ajustar saldo (somente débito com conta vinculada)
    account_balance: float | None = None
    if body.account_id and body.payment_method in _DEBIT_METHODS:
        ba = (
            db.table("bank_accounts")
            .select("balance")
            .eq("id", body.account_id)
            .single()
            .execute()
        )
        current = Decimal(str(ba.data["balance"]))
        new_balance = current - Decimal(str(body.amount))
        db.table("bank_accounts").update({"balance": str(new_balance)}).eq("id", body.account_id).execute()
        account_balance = float(new_balance)

    # 5. Gravar memória
    if body.confirmed and body.notes and final_category != "Rateado":
        try:
            CategoryMemoryRepository().remember(body.notes, Category(final_category), user_id)
        except ValueError:
            logger.warning("category memory skipped — invalid category: %s", final_category)

    return {
        "transaction":          main_tx,
        "installment_children": children,
        "splits":               splits_out,
        "category_suggestion": {
            "category":   suggestion.category.value,
            "confidence": round(suggestion.score, 3),
            "source":     suggestion.source,
        },
        "account_balance": account_balance,
    }
