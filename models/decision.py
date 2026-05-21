import uuid
from datetime import date as Date
from enum import Enum

from pydantic import BaseModel, Field


class DecisionOutcome(str, Enum):
    COMPRAR = "COMPRAR"
    MANTER = "MANTER"
    REDUZIR = "REDUZIR"
    VENDER = "VENDER"


class DecisionRecord(BaseModel):
    """Decision Template — campos do WikiAgent KB."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticker: str
    date: Date = Field(default_factory=Date.today)

    # M1 snapshot
    score_m1: float = 0.0
    dy: float = 0.0
    pvp: float = 0.0
    liquidity: float = 0.0

    # M3 snapshot
    regime: str = ""
    confidence: str = ""
    fragility: float = 0.0

    # Decisão
    outcome: DecisionOutcome | None = None
    invalidation_condition: str = ""

    # Journal — antes da compra
    thesis: str = ""
    risk: str = ""
    alternative_scenario: str = ""
    expectation: str = ""

    # Journal — depois
    result: str = ""
    error: str = ""
    learning: str = ""
    bias_identified: str = ""

    # M4 AI audit
    ai_audit: str = ""
    ai_provider: str = ""
    uncertainty_declared: bool = False
