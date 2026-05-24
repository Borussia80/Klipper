from __future__ import annotations

import uuid
from datetime import date as Date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from models.transaction import Category as _Category


class Installment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    total_amount: Decimal
    n_total: int
    n_paid: int = 0
    installment_amount: Decimal = Decimal("0")
    start_date: Date
    card_id: str | None = None
    account_id: str | None = None
    category: str = "Outros"
    notes: str = ""
    is_active: bool = True

    @field_validator("category")
    @classmethod
    def category_valid(cls, v: str) -> str:
        valid = {c.value for c in _Category}
        if v not in valid:
            return _Category.OUTROS.value
        return v

    @field_validator("description")
    @classmethod
    def desc_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Descrição não pode ser vazia")
        return v.strip()

    @field_validator("n_total")
    @classmethod
    def n_total_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("n_total deve ser ≥ 1")
        return v

    @field_validator("n_paid")
    @classmethod
    def n_paid_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("n_paid não pode ser negativo")
        return v

    @field_validator("total_amount")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Valor total deve ser positivo")
        return round(v, 2)

    @model_validator(mode="after")
    def set_installment_amount(self) -> "Installment":
        if self.n_paid > self.n_total:
            raise ValueError("n_paid não pode ser maior que n_total")
        if self.installment_amount == Decimal("0") and self.n_total > 0:
            self.installment_amount = self.amount_for_installment(0)
        return self

    def installment_amounts(self) -> list[Decimal]:
        """Return currency-safe installment amounts whose sum equals total_amount."""
        total_cents = int(self.total_amount * 100)
        base_cents = total_cents // self.n_total
        remainder = total_cents - (base_cents * self.n_total)
        amounts = [base_cents] * self.n_total
        amounts[-1] += remainder
        return [Decimal(cents) / 100 for cents in amounts]

    def amount_for_installment(self, index: int) -> Decimal:
        return self.installment_amounts()[index]

    @property
    def n_remaining(self) -> int:
        return max(0, self.n_total - self.n_paid)

    @property
    def total_remaining(self) -> Decimal:
        return sum(self.installment_amounts()[self.n_paid:], Decimal(0))

    @property
    def next_due_date(self) -> Date | None:
        if self.n_remaining == 0:
            return None
        from dateutil.relativedelta import relativedelta
        return self.start_date + relativedelta(months=self.n_paid)
