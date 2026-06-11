"""api/main.py — FastAPI thin layer sobre core/ Klipper.

Autenticação: verifica JWT Supabase via Authorization: Bearer header.
Deploy: Vercel (vercel.json na raiz) + Railway (railway.toml).
CORS: restrito ao domínio Vercel em produção.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Garante que o root do repo está no path (necessário no Vercel onde o
# working dir é a raiz do projeto, não o diretório api/)
_repo_root = str(Path(__file__).parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

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
    "http://localhost:3000",           # dev local
    "https://klipper-app.vercel.app",  # PWA prod
    "https://klipper-api.vercel.app",  # self (health checks)
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
