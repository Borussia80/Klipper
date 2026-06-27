"""api/routers/engines.py — Engines M1/M2/M3 via core/."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException


from api.auth import CurrentUser
from api.logging_config import get_logger

logger = get_logger(__name__)
from core.repositories import InvestmentRepository
from models.investment import InvestmentType

router = APIRouter(prefix="/engines", tags=["engines"])


def _fragility_level(score: float) -> str:
    return "low" if score < 0.3 else "medium" if score < 0.6 else "high"


@router.get("/m1/{ticker}")
async def m1_score(ticker: str, _user: CurrentUser) -> dict[str, Any]:
    """Score M1 (Quant Engine) para um ticker do portfólio."""
    try:
        from core.m1_quant import calcular_score_m1
        repo = InvestmentRepository()
        inv  = repo.get_by_ticker(ticker)
        if inv is None:
            raise HTTPException(status_code=404, detail=f"Ativo {ticker.upper()} não encontrado")

        score = calcular_score_m1(
            dy=float(inv.dy_12m),
            pvp=float(inv.pvp),
            liquidez=float(inv.liquidity_daily),
            volatilidade=float(inv.volatility),
            spread_cdi=float(inv.spread_vs_cdi),
        )
        return {
            "ticker": inv.ticker,
            "score":  score,
            "inputs": {
                "dy_12m":          float(inv.dy_12m),
                "pvp":             float(inv.pvp),
                "liquidity_daily": float(inv.liquidity_daily),
                "volatility":      float(inv.volatility),
                "spread_vs_cdi":   float(inv.spread_vs_cdi),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Engine error: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Motor indisponível. Tente novamente.") from exc


@router.get("/governance")
async def m2_governance(_user: CurrentUser) -> dict[str, Any]:
    """Verifica hard limits M2 para o portfólio atual via Supabase.

    O caixa (ativos do tipo CAIXA) é separado dos ativos de risco e passado
    como ``caixa_disponivel`` — `verificar_limites` soma os dois para compor o
    total e checar o piso de caixa de 20%.
    """
    try:
        from core.m2_governance import hard_fail, verificar_limites
        repo      = InvestmentRepository()
        portfolio = repo.get_portfolio()

        caixa_disponivel = float(
            sum((inv.current_value for inv in portfolio if inv.type == InvestmentType.CAIXA), Decimal(0))
        )
        ativos_risco = [inv for inv in portfolio if inv.type != InvestmentType.CAIXA]

        alertas   = verificar_limites(ativos_risco, caixa_disponivel)
        fail, msg = hard_fail(alertas)
        return {
            "ok":               not fail,
            "caixa_disponivel": round(caixa_disponivel, 2),
            "violations":       [asdict(a) for a in alertas],
            "message":          msg,
        }
    except Exception as exc:
        logger.error("Engine error: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Motor indisponível. Tente novamente.") from exc


@router.get("/fragility")
async def m3_fragility(_user: CurrentUser) -> dict[str, Any]:
    """Score de fragilidade do portfólio.

    `calcular_fragility_score` recebe **um** Investment + seu peso no portfólio e
    devolve um `FragilityBreakdown`. Calculamos por ticker e agregamos o overall
    como média ponderada pelo valor de mercado.
    """
    try:
        from core.fragility import calcular_fragility_score
        repo      = InvestmentRepository()
        portfolio = repo.get_portfolio()

        total = float(sum((inv.current_value for inv in portfolio), Decimal(0)))

        results: list[dict[str, Any]] = []
        weighted_sum = 0.0
        for inv in portfolio:
            peso_pct  = (float(inv.current_value) / total * 100) if total else 0.0
            breakdown = calcular_fragility_score(inv, peso_portfolio_pct=peso_pct)
            results.append({
                "ticker":    inv.ticker,
                "score":     breakdown.total,
                "breakdown": asdict(breakdown),
            })
            weighted_sum += breakdown.total * (float(inv.current_value) / total if total else 0.0)

        overall = round(weighted_sum, 4)
        return {
            "overall_score": overall,
            "level":         _fragility_level(overall),
            "by_ticker":     results,
        }
    except Exception as exc:
        logger.error("Engine error: %s", exc, exc_info=True)
        raise HTTPException(status_code=502, detail="Motor indisponível. Tente novamente.") from exc
