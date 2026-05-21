import uuid
from datetime import date as Date
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    GASTO = "GASTO"
    GANHO = "GANHO"


class Category(str, Enum):
    MORADIA = "Moradia"
    ALIMENTACAO = "Alimentação"
    TRANSPORTE = "Transporte"
    SAUDE = "Saúde"
    EDUCACAO = "Educação"
    LAZER = "Lazer"
    INVESTIMENTO = "Investimento"
    RENDA = "Renda"
    FREELANCE = "Freelance"
    OUTROS = "Outros"


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: Date
    amount: float
    type: TransactionType
    category: Category
    notes: str = ""

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Valor deve ser positivo, recebido: {v}")
        return round(v, 2)

    @field_validator("date")
    @classmethod
    def date_not_in_future(cls, v: Date) -> Date:
        if v > Date.today():
            raise ValueError("Data não pode ser futura")
        return v
