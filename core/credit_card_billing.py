from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date as Date

from dateutil.relativedelta import relativedelta

from models.credit_card import CreditCard
from models.transaction import PaymentMethod, Transaction, TransactionType


@dataclass(frozen=True)
class Invoice:
    card_id: str
    closing_date: Date
    due_date: Date
    period_start: Date
    period_end: Date
    total: float
    transactions: list[Transaction]

    @property
    def count(self) -> int:
        return len(self.transactions)


def safe_date(year: int, month: int, day: int) -> Date:
    last_day = calendar.monthrange(year, month)[1]
    return Date(year, month, min(day, last_day))


def closing_date_for_purchase(card: CreditCard, purchase_date: Date) -> Date:
    current_closing = safe_date(purchase_date.year, purchase_date.month, card.closing_day)
    if purchase_date <= current_closing:
        return current_closing
    next_month = purchase_date + relativedelta(months=1)
    return safe_date(next_month.year, next_month.month, card.closing_day)


def due_date_for_closing(card: CreditCard, closing_date: Date) -> Date:
    due_month = closing_date
    if card.due_day <= card.closing_day:
        due_month = closing_date + relativedelta(months=1)
    return safe_date(due_month.year, due_month.month, card.due_day)


def due_date_for_purchase(card: CreditCard, purchase_date: Date) -> Date:
    return due_date_for_closing(card, closing_date_for_purchase(card, purchase_date))


def invoice_for_closing(
    card: CreditCard,
    transactions: list[Transaction],
    year: int,
    month: int,
) -> Invoice:
    closing = safe_date(year, month, card.closing_day)
    previous_month = closing + relativedelta(months=-1)
    previous_closing = safe_date(previous_month.year, previous_month.month, card.closing_day)
    start = previous_closing + relativedelta(days=1)
    end = closing
    card_transactions = [
        tx for tx in transactions
        if tx.card_id == card.id
        and tx.type == TransactionType.GASTO
        and tx.payment_method == PaymentMethod.CARTAO_CREDITO
        and start <= tx.date <= end
    ]
    return Invoice(
        card_id=card.id,
        closing_date=closing,
        due_date=due_date_for_closing(card, closing),
        period_start=start,
        period_end=end,
        total=round(sum(tx.amount for tx in card_transactions), 2),
        transactions=card_transactions,
    )


def invoice_by_due_month(
    card: CreditCard,
    transactions: list[Transaction],
    year: int,
    month: int,
) -> Invoice:
    closing_month = Date(year, month, 1)
    if card.due_day <= card.closing_day:
        closing_month = closing_month + relativedelta(months=-1)
    return invoice_for_closing(card, transactions, closing_month.year, closing_month.month)
