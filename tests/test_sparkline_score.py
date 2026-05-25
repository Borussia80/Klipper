"""TDD — preparar_sparkline_score_historico em core/analytics.py."""
from __future__ import annotations

import pytest
from decimal import Decimal


def _reg(ano, mes, ganhos, gastos):
    return (ano, mes, Decimal(str(ganhos)), Decimal(str(gastos)))


class TestPrepararSparklineScoreHistorico:
    """preparar_sparkline_score_historico(registros) → lista de dicts ordenada."""

    def _fn(self, registros):
        from core.analytics import preparar_sparkline_score_historico
        return preparar_sparkline_score_historico(registros)

    # ── estrutura de retorno ───────────────────────────────────────────────

    def test_returns_list(self):
        result = self._fn([_reg(2026, 1, 5000, 4000)])
        assert isinstance(result, list)

    def test_empty_input_returns_empty(self):
        assert self._fn([]) == []

    def test_each_item_has_mes_and_score(self):
        result = self._fn([_reg(2026, 1, 5000, 3000)])
        assert "mes" in result[0]
        assert "score" in result[0]

    def test_score_is_int(self):
        result = self._fn([_reg(2026, 1, 5000, 4000)])
        assert isinstance(result[0]["score"], int)

    def test_length_matches_input(self):
        regs = [_reg(2026, i, 5000, 3000) for i in range(1, 5)]
        assert len(self._fn(regs)) == 4

    # ── ordenação ─────────────────────────────────────────────────────────

    def test_ordered_chronologically(self):
        regs = [_reg(2026, 3, 5000, 3000), _reg(2026, 1, 5000, 3000), _reg(2026, 2, 5000, 3000)]
        result = self._fn(regs)
        meses = [r["mes"] for r in result]
        assert meses == ["Jan/26", "Fev/26", "Mar/26"]

    def test_crosses_year_boundary(self):
        regs = [_reg(2026, 1, 5000, 3000), _reg(2025, 12, 5000, 3000)]
        result = self._fn(regs)
        assert result[0]["mes"].endswith("25")  # Dez/25 vem antes
        assert result[1]["mes"].endswith("26")

    # ── rótulo ────────────────────────────────────────────────────────────

    def test_label_jan_format(self):
        result = self._fn([_reg(2026, 1, 5000, 3000)])
        assert result[0]["mes"] == "Jan/26"

    def test_label_dez_format(self):
        result = self._fn([_reg(2025, 12, 5000, 3000)])
        assert result[0]["mes"] == "Dez/25"

    def test_label_mai_format(self):
        result = self._fn([_reg(2026, 5, 5000, 3000)])
        assert result[0]["mes"] == "Mai/26"

    # ── cálculo do score proxy ────────────────────────────────────────────

    def test_meta_20pct_gives_score_100(self):
        # taxa = (5000 - 4000) / 5000 * 100 = 20%  → score = min(100, round(20 * 5)) = 100
        result = self._fn([_reg(2026, 1, 5000, 4000)])
        assert result[0]["score"] == 100

    def test_savings_above_meta_capped_at_100(self):
        # taxa = 40%  → round(40 * 5) = 200  → capped 100
        result = self._fn([_reg(2026, 1, 5000, 3000)])
        assert result[0]["score"] == 100

    def test_zero_savings_gives_score_0(self):
        # ganhos == gastos → taxa = 0  → score = 0
        result = self._fn([_reg(2026, 1, 5000, 5000)])
        assert result[0]["score"] == 0

    def test_deficit_gives_score_0(self):
        # gastos > ganhos → taxa < 0  → clamped to 0
        result = self._fn([_reg(2026, 1, 3000, 5000)])
        assert result[0]["score"] == 0

    def test_zero_income_gives_score_0(self):
        result = self._fn([_reg(2026, 1, 0, 0)])
        assert result[0]["score"] == 0

    def test_10pct_savings_gives_score_50(self):
        # taxa = (5000 - 4500) / 5000 * 100 = 10%  → round(10 * 5) = 50
        result = self._fn([_reg(2026, 1, 5000, 4500)])
        assert result[0]["score"] == 50

    def test_score_between_0_and_100(self):
        regs = [_reg(2026, i, 5000, 4000 + i * 100) for i in range(1, 7)]
        for r in self._fn(regs):
            assert 0 <= r["score"] <= 100
