"""api/routers/statement.py — Importação de extratos PDF/PNG via core/statement_reader.py."""

from __future__ import annotations


from fastapi import APIRouter, HTTPException, UploadFile


from api.auth import CurrentUser  # noqa: E402
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/import", tags=["import"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _apply_memory(transactions: list, user_id: str) -> None:
    """Sobrepõe a categoria do parser pela memória do `user_id`, quando ela decide.

    Só altera quando o match veio da camada de histórico (source == "history") —
    senão manteria o palpite rule/fuzzy que o parser já produziu. Altera in-place.
    """
    from core.categorizer import categorize  # type: ignore
    from core.repositories import CategoryMemoryRepository  # type: ignore

    history = CategoryMemoryRepository().load_history(user_id)
    if not history:
        return
    for tx in transactions:
        guess = categorize(tx.description, history)
        if guess.source == "history":
            tx.category = guess.category


@router.post("/statement")
async def import_statement(file: UploadFile, user_id: CurrentUser) -> dict:
    """
    Recebe upload de extrato PDF ou PNG.
    Retorna lista de transações parseadas para revisão antes de salvar.
    O salvamento final é feito pelo PWA diretamente no Supabase (supabase-js).
    """
    if file.content_type not in ("application/pdf", "image/png", "image/jpeg"):
        raise HTTPException(status_code=415, detail="Formato não suportado. Use PDF ou PNG/JPG.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Arquivo muito grande (máx 10 MB).")

    try:
        from core.statement_reader import read_statement  # type: ignore
        result = read_statement(content)
        if hasattr(result, "transactions"):
            _apply_memory(result.transactions, user_id)
            transactions = [t.__dict__ for t in result.transactions]
        else:
            transactions = result
        return {
            "count": len(transactions),
            "transactions": [t.model_dump() if hasattr(t, "model_dump") else t for t in transactions],
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Falha no parse do extrato: {exc}") from exc
