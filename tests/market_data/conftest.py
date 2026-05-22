"""Fixtures de infraestrutura compartilhadas — apenas o essencial."""
from __future__ import annotations

import fakeredis
import pytest

from core.market_cache import MarketCache
from core.market_data import MarketDataService


@pytest.fixture()
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture()
def cache(fake_redis) -> MarketCache:
    return MarketCache(redis_client=fake_redis)


@pytest.fixture()
def svc(cache, monkeypatch) -> MarketDataService:
    # Isolate each test with a fresh circuit-breaker registry so shared state
    # from the global get_breaker() singleton never leaks between tests.
    from core import circuit_breaker as _cb_mod
    monkeypatch.setattr(_cb_mod, "_registry", {})
    return MarketDataService(cache=cache, batch_size=50, max_workers=4)
