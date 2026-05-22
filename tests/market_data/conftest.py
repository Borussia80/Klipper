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
def svc(cache) -> MarketDataService:
    s = MarketDataService(cache=cache, batch_size=50, max_workers=4)
    s._cb_yf.reset()
    s._cb_tesouro.reset()
    s._cb_bcb.reset()
    return s
