from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Specialty(str, Enum):
    FONOAUDIOLOGIA    = "FONOAUDIOLOGIA"
    TERAPIA_OCUPACIONAL = "TERAPIA_OCUPACIONAL"
    PSICOLOGIA        = "PSICOLOGIA"
    PSIQUIATRIA       = "PSIQUIATRIA"
    NEUROLOGIA        = "NEUROLOGIA"
    FISIOTERAPIA      = "FISIOTERAPIA"
    OUTRO             = "OUTRO"


SPECIALTY_LABELS: dict[str, str] = {
    "FONOAUDIOLOGIA":     "Fonoaudiologia",
    "TERAPIA_OCUPACIONAL":"Terapia Ocupacional",
    "PSICOLOGIA":         "Psicologia",
    "PSIQUIATRIA":        "Psiquiatria",
    "NEUROLOGIA":         "Neurologia",
    "FISIOTERAPIA":       "Fisioterapia",
    "OUTRO":              "Outro",
}


class ReimbursementStatus(str, Enum):
    PENDENTE     = "PENDENTE"
    REEMBOLSADO  = "REEMBOLSADO"
    PARCIAL      = "PARCIAL"
    NEGADO       = "NEGADO"


STATUS_LABELS: dict[str, str] = {
    "PENDENTE":    "Pendente",
    "REEMBOLSADO": "Reembolsado",
    "PARCIAL":     "Parcial",
    "NEGADO":      "Negado",
}

STATUS_COLORS: dict[str, str] = {
    "PENDENTE":    "#F59E0B",
    "REEMBOLSADO": "#10B981",
    "PARCIAL":     "#6366F1",
    "NEGADO":      "#EF4444",
}


class HealthProfessional(BaseModel):
    id:             str       = Field(default_factory=lambda: str(uuid.uuid4()))
    name:           str
    specialty:      Specialty
    council_number: str | None = None
    is_active:      bool      = True


class HealthSession(BaseModel):
    id:                        str       = Field(default_factory=lambda: str(uuid.uuid4()))
    professional_id:           str
    session_date:              date
    amount_paid:               Decimal
    nf_number:                 str | None = None
    notes:                     str | None = None
    reimbursement_request_id:  str | None = None

    @field_validator("amount_paid")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount_paid deve ser positivo")
        return v

    @property
    def is_pending(self) -> bool:
        """Sessão ainda não incluída em nenhuma solicitação de reembolso."""
        return self.reimbursement_request_id is None


class ReimbursementRequest(BaseModel):
    id:               str       = Field(default_factory=lambda: str(uuid.uuid4()))
    professional_id:  str
    request_date:     date
    protocol_number:  str | None = None
    amount_requested: Decimal
    amount_received:  Decimal | None = None
    status:           ReimbursementStatus = ReimbursementStatus.PENDENTE
    notes:            str | None = None

    @field_validator("amount_requested")
    @classmethod
    def requested_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount_requested deve ser positivo")
        return v

    @property
    def gap(self) -> Decimal:
        """Valor ainda não recebido: requested - received (0 se totalmente reembolsado)."""
        if self.status == ReimbursementStatus.REEMBOLSADO:
            return Decimal("0")
        if self.amount_received is None:
            return self.amount_requested
        return self.amount_requested - self.amount_received
