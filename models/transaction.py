from __future__ import annotations

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


class PaymentMethod(str, Enum):
    PIX = "PIX"
    CARTAO_CREDITO = "CARTAO_CREDITO"
    CARTAO_DEBITO = "CARTAO_DEBITO"
    DINHEIRO = "DINHEIRO"
    TED = "TED"
    BOLETO = "BOLETO"
    TRANSFERENCIA = "TRANSFERENCIA"


class TransactionStatus(str, Enum):
    PAGO = "PAGO"
    PENDENTE = "PENDENTE"
    AGENDADO = "AGENDADO"


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: Date
    amount: float
    type: TransactionType
    category: Category
    notes: str = ""
    payment_method: PaymentMethod = PaymentMethod.PIX
    account_id: str | None = None
    card_id: str | None = None
    installment_id: str | None = None
    status: TransactionStatus = TransactionStatus.PAGO

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Valor deve ser positivo, recebido: {v}")
        return round(v, 2)
