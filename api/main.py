"""api/main.py — FastAPI thin layer sobre core/ Klipper.

Autenticação: verifica JWT Supabase via Authorization: Bearer header.
Deploy: Railway (railway.toml aponta para este arquivo).
CORS: restrito ao domínio Vercel em produção.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import engines, kira, quotes, statement

app = FastAPI(
    title="Klipper API",
    description="FastAPI thin layer over core/ — engines, market data, OCR, Kira",
    version="0.1.0",
    docs_url="/docs" if os.environ.get("ENV") != "production" else None,
    redoc_url=None,
)

# ── CORS ──────────────────────────────────────────────────────────────────────

_vercel_origin = os.environ.get("VERCEL_URL", "")
_allowed_origins = [
    "http://localhost:3000",          # dev local
    "https://klipper-app.vercel.app",  # Vercel prod
]
if _vercel_origin:
    _allowed_origins.append(f"https://{_vercel_origin}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(quotes.router)
app.include_router(engines.router)
app.include_router(statement.router)
app.include_router(kira.router)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": app.version}
