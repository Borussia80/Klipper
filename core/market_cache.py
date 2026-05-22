"""
Cache de cotações com Redis (TTL configurável) e fallback in-memory.

Hierarquia de cache:
  1. Redis (se REDIS_URL configurado) — compartilhado entre workers
  2. fakeredis em memória          — single-process, sem infra
  3. Fallback store                — sem TTL, último valor conhecido

TTLs padrão (segundos):
  STOCK_TTL   =    300   # 5 min — ações e ETFs
  FII_TTL     =  86400   # 1 dia — dados fundamentais de FII
  TESOURO_TTL =   3600   # 1 h   — taxas do Tesouro
  PTAX_TTL    =  86400   # 1 dia — PTAX fecha uma vez por dia
  FX_TTL      =     60   # 1 min — câmbio em tempo real
"""

from __future__ import annotations

import json
import logging
import os
import threading
from typing import Any

log = logging.getLogger(__name__)

# ── TTLs ──────────────────────────────────────────────────────────────────────

STOCK_TTL   =    300
FII_TTL     =  86400
TESOURO_TTL =   3600
PTAX_TTL    =  86400
FX_TTL      =     60


# ── Backend selection ─────────────────────────────────────────────────────────

def _build_redis_client():
    """Retorna cliente Redis ou fakeredis como fallback."""
    url = os.environ.get("REDIS_URL", "")
    if url:
        try:
            import redis as redis_lib
            client = redis_lib.from_url(url, decode_responses=True, socket_connect_timeout=2)
            client.ping()
            log.info("MarketCache: usando Redis em %s", url)
            return client
        except Exception as e:
            log.warning("MarketCache: falha ao conectar ao Redis (%s) — usando fakeredis", e)

    import fakeredis
    log.info("MarketCache: usando fakeredis (in-memory)")
    return fakeredis.FakeRedis(decode_responses=True)


# ── MarketCache ───────────────────────────────────────────────────────────────

class MarketCache:
    """
    Cache de cotações com TTL por tipo de ativo.

    Mantém também um _fallback_store (sem TTL) com o último valor
    bem-sucedido de cada chave — servido quando a API falha e o
    cache expirou.
    """

    def __init__(self, redis_client=None) -> None:
        self._r = redis_client or _build_redis_client()
        self._fallback: dict[str, str] = {}     # chave → JSON serializado
        self._lock = threading.Lock()

    # ── public API ────────────────────────────────────────────────────────────

    def get(self, key: str) -> Any | None:
        """Retorna valor do cache Redis ou None se expirado/ausente."""
        try:
            raw = self._r.get(key)
            if raw is not None:
                return json.loads(raw)
        except Exception as e:
            log.debug("MarketCache.get(%s) erro: %s", key, e)
        return None

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Grava valor no Redis com TTL e atualiza o fallback store."""
        raw = json.dumps(value, default=str)
        try:
            self._r.setex(key, ttl, raw)
        except Exception as e:
            log.debug("MarketCache.set(%s) erro: %s", key, e)
        with self._lock:
            self._fallback[key] = raw

    def get_fallback(self, key: str) -> Any | None:
        """Último valor conhecido, sem considerar TTL."""
        with self._lock:
            raw = self._fallback.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def invalidate(self, key: str) -> None:
        """Remove uma chave do cache Redis (não apaga o fallback)."""
        try:
            self._r.delete(key)
        except Exception as e:
            log.debug("MarketCache.invalidate(%s) erro: %s", key, e)

    def invalidate_pattern(self, pattern: str) -> None:
        """Remove todas as chaves que combinam com o padrão glob."""
        try:
            keys = self._r.keys(pattern)
            if keys:
                self._r.delete(*keys)
                log.debug("MarketCache.invalidate_pattern(%s): %d chaves removidas", pattern, len(keys))
        except Exception as e:
            log.debug("MarketCache.invalidate_pattern(%s) erro: %s", pattern, e)

    def ttl(self, key: str) -> int:
        """Retorna o TTL restante em segundos (-2 se não existe, -1 se sem TTL)."""
        try:
            return self._r.ttl(key)
        except Exception:
            return -2

    def flush(self) -> None:
        """Apaga TODO o cache Redis (usar apenas em testes)."""
        try:
            self._r.flushdb()
        except Exception:
            pass
        with self._lock:
            self._fallback.clear()


# Singleton por processo
_cache_instance: MarketCache | None = None
_cache_lock = threading.Lock()


def get_cache() -> MarketCache:
    global _cache_instance
    with _cache_lock:
        if _cache_instance is None:
            _cache_instance = MarketCache()
    return _cache_instance


def reset_cache(client=None) -> MarketCache:
    """Substitui o singleton — usado em testes para injetar fakeredis dedicado."""
    global _cache_instance
    with _cache_lock:
        _cache_instance = MarketCache(redis_client=client)
    return _cache_instance
