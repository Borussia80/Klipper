"""TDD Sprint 8 — Gauge Plotly de uso do limite por cartão."""
from __future__ import annotations

from decimal import Decimal

import pytest


# ── preparar_dados_gauge_limite ───────────────────────────────────────────────

class TestPrepararDadosGaugeLimite:

    def test_returns_dict(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("500"), Decimal("2000"))
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("500"), Decimal("2000"))
        for key in ("usado", "limite", "disponivel", "pct_uso", "status"):
            assert key in result, f"chave '{key}' ausente"

    def test_usado_is_float(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("500"), Decimal("2000"))
        assert isinstance(result["usado"], float)

    def test_limite_is_float(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("500"), Decimal("2000"))
        assert isinstance(result["limite"], float)

    def test_disponivel_correct(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("500"), Decimal("2000"))
        assert abs(result["disponivel"] - 1500.0) < 0.01

    def test_pct_uso_correct(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("500"), Decimal("2000"))
        assert abs(result["pct_uso"] - 25.0) < 0.01

    def test_status_ok_below_50pct(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("400"), Decimal("2000"))
        assert result["status"] == "ok"

    def test_status_alerta_between_50_and_80(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("1200"), Decimal("2000"))
        assert result["status"] == "alerta"

    def test_status_estouro_above_80pct(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("1800"), Decimal("2000"))
        assert result["status"] == "estouro"

    def test_status_estouro_at_100pct(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("2000"), Decimal("2000"))
        assert result["status"] == "estouro"

    def test_pct_zero_when_no_usage(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("0"), Decimal("2000"))
        assert result["pct_uso"] == 0.0
        assert result["status"] == "ok"

    def test_limite_zero_returns_safe_defaults(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("500"), Decimal("0"))
        assert result["pct_uso"] == 0.0
        assert result["disponivel"] == 0.0

    def test_disponivel_never_negative(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("3000"), Decimal("2000"))
        assert result["disponivel"] >= 0.0

    def test_pct_capped_at_100(self):
        from core.analytics import preparar_dados_gauge_limite
        result = preparar_dados_gauge_limite(Decimal("3000"), Decimal("2000"))
        assert result["pct_uso"] <= 100.0
