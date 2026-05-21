import uuid
from datetime import date as Date

from pydantic import BaseModel, Field, field_validator, model_validator


class Installment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    total_amount: float
    n_total: int
    n_paid: int = 0
    installment_amount: float = 0.0
    start_date: Date
    card_id: str | None = None
    account_id: str | None = None
    category: str = "Outros"
    notes: str = ""
    is_active: bool = True

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

    @field_validator("total_amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Valor total deve ser positivo")
        return round(v, 2)

    @model_validator(mode="after")
    def set_installment_amount(self) -> "Installment":
        if self.installment_amount == 0.0 and self.n_total > 0:
            self.installment_amount = round(self.total_amount / self.n_total, 2)
        return self

    @property
    def n_remaining(self) -> int:
        return max(0, self.n_total - self.n_paid)

    @property
    def total_remaining(self) -> float:
        return round(self.n_remaining * self.installment_amount, 2)

    @property
    def next_due_date(self) -> Date | None:
        if self.n_remaining == 0:
            return None
        from dateutil.relativedelta import relativedelta
        return self.start_date + relativedelta(months=self.n_paid)
