"""api/routers/kira.py — Chat Kira com streaming SSE via core/financial_ai.py."""

from __future__ import annotations

from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


from api.auth import CurrentUser  # noqa: E402
from api.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/kira", tags=["kira"])


class ChatRequest(BaseModel):
    message: str
    context: dict | None = None


async def _stream_kira(message: str, context: dict | None) -> AsyncIterator[str]:
    """Gera eventos SSE do chat Kira usando core/financial_ai.py::ask()."""
    import asyncio
    try:
        from core.financial_ai import ask  # type: ignore
        # ask() é síncrono — executa em thread para não bloquear o event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, ask, message)
        # Entrega em chunks simulados para manter interface SSE
        for chunk in (response[i:i+100] for i in range(0, len(response), 100)):
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(0)
    except Exception as exc:
        yield f"data: [ERROR] {exc}\n\n"
    finally:
        yield "data: [DONE]\n\n"


@router.post("/chat")
async def kira_chat(body: ChatRequest, _user: CurrentUser) -> StreamingResponse:
    """Chat com Kira via streaming SSE."""
    if not body.message.strip():
        raise HTTPException(status_code=422, detail="Mensagem não pode estar vazia.")

    return StreamingResponse(
        _stream_kira(body.message, body.context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
