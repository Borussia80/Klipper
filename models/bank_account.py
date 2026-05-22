import uuid
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class AccountType(str, Enum):
    CORRENTE = "CORRENTE"
    POUPANCA = "POUPANCA"
    INVESTIMENTO = "INVESTIMENTO"


class BankAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    bank: str = ""
    type: AccountType = AccountType.CORRENTE
    balance: Decimal = Decimal("0")
    color: str = "#6366F1"
    is_active: bool = True

    @field_validator("balance")
    @classmethod
    def balance_two_decimals(cls, v: Decimal) -> Decimal:
        return round(v, 2)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome da conta não pode ser vazio")
        return v.strip()
