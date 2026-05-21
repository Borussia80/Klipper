from __future__ import annotations

from datetime import date as Date

from dateutil.relativedelta import relativedelta

from models.installment import Installment
from models.transaction import Transaction, TransactionType, Category, PaymentMethod, TransactionStatus


def gerar_parcelas(inst: Installment) -> list[Transaction]:
    """Generates n_total Transactions from an installment, one per month."""
    hoje = Date.today()
    txs: list[Transaction] = []
    for i in range(inst.n_total):
        due = inst.start_date + relativedelta(months=i)
        status = TransactionStatus.PAGO if due <= hoje else TransactionStatus.PENDENTE
        payment = PaymentMethod.CARTAO_CREDITO if inst.card_id else PaymentMethod.PIX
        category = _resolve_category(inst.category)
        tx = Transaction(
            date=due,
            amount=inst.installment_amount,
            type=TransactionType.GASTO,
            category=category,
            notes=f"{inst.description} ({i + 1}/{inst.n_total})",
            payment_method=payment,
            account_id=inst.account_id,
            card_id=inst.card_id,
            installment_id=inst.id,
            status=status,
        )
        txs.append(tx)
    return txs


def calcular_comprometimento_mensal(installments: list[Installment]) -> dict[str, float]:
    """Returns monthly total commitment for active installments (key: YYYY-MM)."""
    hoje = Date.today()
    comprometimento: dict[str, float] = {}
    for inst in installments:
        if not inst.is_active:
            continue
        for i in range(inst.n_total):
            due = inst.start_date + relativedelta(months=i)
            if due >= hoje:
                key = due.strftime("%Y-%m")
                comprometimento[key] = round(
                    comprometimento.get(key, 0.0) + inst.installment_amount, 2
                )
    return dict(sorted(comprometimento.items()))


def _resolve_category(category_str: str) -> Category:
    mapping = {c.value: c for c in Category}
    return mapping.get(category_str, Category.OUTROS)
