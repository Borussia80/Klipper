"""api/routers/engines.py — Engines M1/M2/M3 via core/."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.auth import CurrentUser  # noqa: E402

router = APIRouter(prefix="/engines", tags=["engines"])


@router.get("/m1/{ticker}")
async def m1_score(ticker: str, _user: CurrentUser) -> dict[str, Any]:
    """Score M1 (Quant Engine) para um ticker."""
    try:
        from core.m1_quant import calcular_score_m1  # type: ignore
        result = calcular_score_m1(ticker.upper())
        return {"ticker": ticker.upper(), **result}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/governance")
async def m2_governance(_user: CurrentUser) -> dict[str, Any]:
    """Verifica hard limits M2 para o portfólio atual via Supabase."""
    try:
        from core.database import get_client  # type: ignore
        from core.m2_governance import hard_fail, verificar_limites  # type: ignore
        from core.repositories import InvestmentRepository  # type: ignore
        repo = InvestmentRepository(get_client())
        portfolio = repo.listar()
        alertas = verificar_limites(portfolio)
        fail, msg = hard_fail(alertas)
        return {
            "ok": not fail,
            "violations": [a.model_dump() if hasattr(a, "model_dump") else str(a) for a in alertas],
            "message": msg,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/fragility")
async def m3_fragility(_user: CurrentUser) -> dict[str, Any]:
    """Score de fragilidade M3 do portfólio."""
    try:
        from core.database import get_client  # type: ignore
        from core.fragility import calcular_fragility_score  # type: ignore
        from core.repositories import InvestmentRepository  # type: ignore
        repo = InvestmentRepository(get_client())
        portfolio = repo.listar()
        score = calcular_fragility_score(portfolio)
        return {"score": float(score), "level": "low" if score < 0.3 else "medium" if score < 0.6 else "high"}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
