"""
MarketCache — TTL, fallback store e invalidação.

test_valor_expira_apos_ttl usa time.sleep(1s) real porque o comportamento
de expiração de chave do Redis depende de tempo real — marcado @slow.
O ciclo local roda sem ele; CI executa a suite completa.
"""
from __future__ import annotations

import time
from time import perf_counter

import pytest

from core.market_cache import FII_TTL, STOCK_TTL, MarketCache


class TestMarketCacheOperacoes:

    def test_get_retorna_none_para_chave_inexistente(self, cache):
        assert cache.get("inexistente:XX") is None

    def test_set_e_get_roundtrip(self, cache):
        cache.set("stock:PETR4", {"price": 35.5}, STOCK_TTL)
        assert cache.get("stock:PETR4") == {"price": 35.5}

    def test_ttl_e_aplicado(self, cache):
        cache.set("test:ttl_check", {"x": 1}, ttl=5)
        remaining = cache.ttl("test:ttl_check")
        assert 0 < remaining <= 5

    @pytest.mark.slow
    def test_valor_expira_apos_ttl(self, cache):
        """Expira chave real — dependência de tempo real, excluído do ciclo local."""
        cache.set("test:expire", {"v": 99}, ttl=1)
        assert cache.get("test:expire") == {"v": 99}
        time.sleep(1.05)
        assert cache.get("test:expire") is None

    def test_fallback_sobrevive_expiracao(self, cache):
        """invalidate() simula expiração; fallback_store deve sobreviver."""
        cache.set("stock:VALE3", {"price": 67.0}, ttl=STOCK_TTL)
        cache.invalidate("stock:VALE3")
        assert cache.get("stock:VALE3") is None
        assert cache.get_fallback("stock:VALE3") == {"price": 67.0}

    def test_invalidate_remove_chave_do_redis(self, cache):
        cache.set("stock:ITUB4", {"price": 28.0}, STOCK_TTL)
        cache.invalidate("stock:ITUB4")
        assert cache.get("stock:ITUB4") is None

    def test_invalidate_nao_apaga_fallback(self, cache):
        cache.set("stock:BBDC4", {"price": 15.0}, STOCK_TTL)
        cache.invalidate("stock:BBDC4")
        assert cache.get_fallback("stock:BBDC4") == {"price": 15.0}

    def test_invalidate_pattern_remove_multiplas_chaves(self, cache):
        for t in ["PETR4", "VALE3", "MGLU3"]:
            cache.set(f"stock:{t}", {"price": 10.0}, STOCK_TTL)
        cache.set("fii:MXRF11", {"price": 10.0}, FII_TTL)
        cache.invalidate_pattern("stock:*")
        assert cache.get("stock:PETR4") is None
        assert cache.get("stock:VALE3") is None
        assert cache.get("fii:MXRF11") is not None  # intocado

    def test_flush_limpa_tudo_incluindo_fallback(self, cache):
        cache.set("stock:WEGE3", {"price": 45.0}, STOCK_TTL)
        cache.flush()
        assert cache.get("stock:WEGE3") is None
        assert cache.get_fallback("stock:WEGE3") is None


class TestMarketCachePerformance:

    def test_1000_get_set_em_menos_de_500ms(self, cache):
        start = perf_counter()
        for i in range(1000):
            cache.set(f"stock:TICKER{i:04d}", {"price": float(i)}, STOCK_TTL)
        for i in range(1000):
            assert cache.get(f"stock:TICKER{i:04d}") is not None
        elapsed = perf_counter() - start
        assert elapsed < 0.5, f"1000 get+set demorou {elapsed:.2f}s"
