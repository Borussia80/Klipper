import uuid
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class Budget(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    monthly_limit: Decimal
    year: int
    month: int

    @field_validator("monthly_limit")
    @classmethod
    def limit_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Limite mensal deve ser positivo")
        return round(v, 2)

    @field_validator("month")
    @classmethod
    def month_valid(cls, v: int) -> int:
        if not 1 <= v <= 12:
            raise ValueError(f"Mês inválido: {v}")
        return v
