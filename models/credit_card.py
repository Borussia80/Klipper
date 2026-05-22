import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from models.transaction import Transaction


class CreditCard(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    bank: str = ""
    limit_total: Decimal = Decimal("0")
    closing_day: int = 1
    due_day: int = 10
    color: str = "#EF4444"
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome do cartão não pode ser vazio")
        return v.strip()

    @field_validator("closing_day", "due_day")
    @classmethod
    def day_valid(cls, v: int) -> int:
        if not 1 <= v <= 31:
            raise ValueError(f"Dia inválido: {v}. Esperado 1–31.")
        return v

    @field_validator("limit_total")
    @classmethod
    def limit_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Limite não pode ser negativo")
        return round(v, 2)

    def limit_used(self, transactions: list["Transaction"]) -> Decimal:
        from models.transaction import TransactionType
        return sum(
            (t.amount for t in transactions
             if t.card_id == self.id and t.type == TransactionType.GASTO),
            Decimal(0),
        )

    def limit_available(self, transactions: list["Transaction"]) -> Decimal:
        return self.limit_total - self.limit_used(transactions)

    def fatura_atual(self, transactions: list["Transaction"]) -> Decimal:
        return self.limit_used(transactions)

    def fatura_por_vencimento(
        self,
        transactions: list["Transaction"],
        year: int,
        month: int,
    ) -> float:
        from core.credit_card_billing import invoice_by_due_month
        return invoice_by_due_month(self, transactions, year, month).total
