"""api/auth.py — Verificação do JWT Supabase para endpoints FastAPI.

O PWA envia `Authorization: Bearer <access_token>` em cada request.
Esse token é o JWT gerado pelo Supabase Auth após login do usuário.
Verificamos a assinatura e o `sub` (user_id) sem round-trip ao banco.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer()


@lru_cache(maxsize=1)
def _jwks() -> dict:
    """Busca as chaves públicas Supabase para verificação JWT (cacheado)."""
    url = os.environ["SUPABASE_URL"]
    resp = httpx.get(f"{url}/auth/v1/.well-known/jwks.json", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> str:
    """Retorna o user_id (sub) do JWT ou levanta 401."""
    from jose import JWTError, jwt

    token = credentials.credentials
    try:
        # Supabase usa RS256; a chave pública está no JWKS endpoint
        header = jwt.get_unverified_header(token)
        keys = _jwks().get("keys", [])
        public_key = next((k for k in keys if k.get("kid") == header.get("kid")), None)

        if not public_key:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Public key not found")

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="authenticated",
        )
        user_id: str = payload["sub"]
        return user_id

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
        ) from exc


CurrentUser = Annotated[str, Depends(get_current_user)]
