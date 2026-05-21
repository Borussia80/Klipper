from __future__ import annotations

import logging
import os
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

log = logging.getLogger(__name__)


def _carregar_config() -> tuple[str, str]:
    """Valida e retorna credenciais Supabase no boot."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    ausentes = [k for k, v in {"SUPABASE_URL": url, "SUPABASE_KEY": key}.items() if not v]
    if ausentes:
        raise EnvironmentError(
            f"Variáveis de ambiente obrigatórias ausentes: {', '.join(ausentes)}\n"
            "Consulte .env.example para configuração."
        )
    return url, key


@lru_cache(maxsize=1)
def get_client() -> Client:
    """Retorna singleton do cliente Supabase."""
    url, key = _carregar_config()
    log.info("Conectando ao Supabase: %s", url)
    return create_client(url, key)
