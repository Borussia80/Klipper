"""api/routers/category.py — Categorização fuzzy + memória de aprendizado.

Seam do loop de aprendizado para o PWA (que fala supabase-js direto e não passa
pelo core/ Python, exceto aqui):
  • POST /category/suggest  → sugere categoria para uma descrição (memória + fuzzy)
  • POST /category/memory   → grava o rótulo confirmado pelo usuário (aprende)
"""
from __future__ import annotations


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


from api.auth import CurrentUser  # noqa: E402
from api.logging_config import get_logger

logger = get_logger(__name__)
from core.repositories import CategoryMemoryRepository, categorize_with_memory  # noqa: E402
from models.transaction import Category  # noqa: E402

router = APIRouter(prefix="/category", tags=["category"])


class SuggestRequest(BaseModel):
    description: str = Field(min_length=1, max_length=500)


class MemoryRequest(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    category: str = Field(min_length=1)


def _parse_category(value: str) -> Category:
    try:
        return Category(value)
    except ValueError as exc:
        validas = ", ".join(c.value for c in Category)
        raise HTTPException(
            status_code=422,
            detail=f"Categoria inválida: '{value}'. Válidas: {validas}.",
        ) from exc


@router.post("/suggest")
async def suggest_category(body: SuggestRequest, user_id: CurrentUser) -> dict:
    """Sugere a categoria de uma descrição. Inclui score e se é confiável,
    para o PWA decidir entre aplicar direto ou pedir validação ao usuário."""
    guess = categorize_with_memory(body.description, user_id)
    return {
        "category": guess.category.value,
        "score": round(guess.score, 3),
        "source": guess.source,
        "confident": guess.confident,
        "matched": guess.matched,
    }


@router.post("/memory")
async def remember_category(body: MemoryRequest, user_id: CurrentUser) -> dict:
    """Registra um rótulo confirmado pelo usuário (descrição → categoria).
    Chamar quando o usuário confirma/corrige a categoria — nunca em palpite automático."""
    category = _parse_category(body.category)
    CategoryMemoryRepository().remember(body.description, category, user_id)
    return {"ok": True}
