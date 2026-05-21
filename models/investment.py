from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InvestmentType(str, Enum):
    FII = "FII"
    ACAO = "Ação"
    RF = "Renda Fixa"
    CAIXA = "Caixa"


class Investment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticker: str
    type: InvestmentType
    quantity: float
    avg_price: float
    current_price: float
    dy_12m: float = 0.0        # Dividend Yield 12 meses (%)
    pvp: float = 0.0           # Preço / Valor Patrimonial
    liquidity_daily: float = 0.0  # Liquidez média diária (R$)
    volatility: float = 0.0    # Volatilidade anualizada (%)
    spread_vs_cdi: float = 0.0 # Spread vs CDI (p.p.)
    sector: str = ""
    fragility_score: float = 0.0  # 0.0–1.0 (M4 Fragility)
    notes: str = ""

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper().strip()

    @field_validator("quantity", "avg_price", "current_price")
    @classmethod
    def must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(f"Valor deve ser positivo, recebido: {v}")
        return v

    @field_validator("fragility_score")
    @classmethod
    def fragility_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Fragility score deve estar entre 0 e 1, recebido: {v}")
        return round(v, 4)

    @property
    def current_value(self) -> float:
        return round(self.quantity * self.current_price, 2)

    @property
    def gain_loss(self) -> float:
        return round((self.current_price - self.avg_price) * self.quantity, 2)

    @property
    def gain_loss_pct(self) -> float:
        if self.avg_price == 0:
            return 0.0
        return round((self.current_price / self.avg_price - 1) * 100, 2)
