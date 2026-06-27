"""api/routers/quotes.py — Cotações e benchmarks via core/market_data.py."""

from __future__ import annotations


from fastapi import APIRouter, HTTPException

# Adiciona raiz do repo ao path para importar core/

from api.auth import CurrentUser  # noqa: E402
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("/benchmarks")
async def list_benchmarks(_user: CurrentUser) -> dict:
    """Retorna benchmarks: CDI, SELIC, câmbio via MarketDataService."""
    try:
        from core.market_data import get_market_service  # type: ignore
        svc = get_market_service()
        return svc.get_benchmarks()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Benchmarks unavailable: {exc}") from exc


@router.get("/{ticker}")
async def get_quote(ticker: str, _user: CurrentUser) -> dict:
    """Retorna cotação atual de um ticker (ação ou FII)."""
    try:
        from core.market_data import get_market_service, is_fii  # type: ignore
        svc = get_market_service()
        t = ticker.upper()
        quote = svc.get_fii(t) if is_fii(t) else svc.get_stock(t)
        if quote is None:
            raise HTTPException(status_code=404, detail=f"Ticker {t} não encontrado.")
        price = getattr(quote, "current_price", None) or getattr(quote, "price", None)
        return {"ticker": t, "price": price}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Market data unavailable: {exc}") from exc
