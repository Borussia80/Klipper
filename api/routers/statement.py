"""api/routers/statement.py — Importação de extratos PDF/PNG via core/statement_reader.py."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.auth import CurrentUser  # noqa: E402

router = APIRouter(prefix="/import", tags=["import"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/statement")
async def import_statement(file: UploadFile, _user: CurrentUser) -> dict:
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
        transactions = [t.__dict__ for t in result.transactions] if hasattr(result, "transactions") else result
        return {
            "count": len(transactions),
            "transactions": [t.model_dump() if hasattr(t, "model_dump") else t for t in transactions],
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Falha no parse do extrato: {exc}") from exc
