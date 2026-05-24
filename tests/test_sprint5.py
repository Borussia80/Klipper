"""TDD Sprint 5 — charts de Transações: gastos diários + comparativo por categoria."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest


# ── helpers ───────────────────────────────────────────────────────────────────

def _tx(amount: float, day: int, month: int = 4, year: int = 2030,
        tipo: str = "GASTO", cat: str = "Alimentação") -> object:
    from models.transaction import Transaction, TransactionType, Category, PaymentMethod, TransactionStatus
    return Transaction(
        description=f"tx-{day}",
        amount=Decimal(str(amount)),
        date=date(year, month, day),
        type=TransactionType(tipo),
        category=Category(cat),
        payment_method=PaymentMethod.PIX,
        status=TransactionStatus.PAGO,
    )


# ── preparar_gastos_diarios ───────────────────────────────────────────────────

class TestPrepararGastosDiarios:

    def test_returns_list(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(50.0, 1)]
        result = preparar_gastos_diarios(txs, 2030, 4)
        assert isinstance(result, list)

    def test_empty_transactions_returns_empty(self):
        from core.analytics import preparar_gastos_diarios
        result = preparar_gastos_diarios([], 2030, 4)
        assert result == []

    def test_row_has_required_keys(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(50.0, 5)]
        result = preparar_gastos_diarios(txs, 2030, 4)
        assert len(result) > 0
        row = result[0]
        assert "dia" in row
        assert "date" in row
        assert "Gastos" in row

    def test_gastos_aggregated_per_day(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(30.0, 10), _tx(20.0, 10), _tx(50.0, 15)]
        result = preparar_gastos_diarios(txs, 2030, 4)
        day10 = next((r for r in result if r["dia"] == 10), None)
        assert day10 is not None
        assert abs(day10["Gastos"] - 50.0) < 0.01

    def test_excludes_ganhos(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(1000.0, 1, tipo="GANHO"), _tx(50.0, 1, tipo="GASTO")]
        result = preparar_gastos_diarios(txs, 2030, 4)
        day1 = next((r for r in result if r["dia"] == 1), None)
        assert day1 is not None
        assert abs(day1["Gastos"] - 50.0) < 0.01

    def test_filters_by_month_and_year(self):
        from core.analytics import preparar_gastos_diarios
        txs = [
            _tx(100.0, 1, month=4, year=2030),
            _tx(200.0, 1, month=5, year=2030),  # outro mês
            _tx(300.0, 1, month=4, year=2029),  # outro ano
        ]
        result = preparar_gastos_diarios(txs, 2030, 4)
        assert len(result) == 1
        assert abs(result[0]["Gastos"] - 100.0) < 0.01

    def test_ordered_by_day(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(10.0, 20), _tx(10.0, 5), _tx(10.0, 12)]
        result = preparar_gastos_diarios(txs, 2030, 4)
        dias = [r["dia"] for r in result]
        assert dias == sorted(dias)

    def test_date_is_string(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(50.0, 7)]
        result = preparar_gastos_diarios(txs, 2030, 4)
        assert isinstance(result[0]["date"], str)

    def test_gastos_is_float(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(99.99, 3)]
        result = preparar_gastos_diarios(txs, 2030, 4)
        assert isinstance(result[0]["Gastos"], float)

    def test_cumulative_optional(self):
        from core.analytics import preparar_gastos_diarios
        txs = [_tx(10.0, 1), _tx(20.0, 2), _tx(30.0, 3)]
        result = preparar_gastos_diarios(txs, 2030, 4, cumulative=True)
        gastos = [r["Gastos"] for r in result]
        # cumulativo: dia 3 deve ser >= dia 2 >= dia 1
        assert gastos[0] <= gastos[1] <= gastos[2]


# ── preparar_comparativo_categorias ──────────────────────────────────────────

class TestPrepararComparativoCategorias:

    def test_returns_list(self):
        from core.analytics import preparar_comparativo_categorias
        txs = [_tx(100.0, 1, cat="Alimentação")]
        result = preparar_comparativo_categorias(txs, [])
        assert isinstance(result, list)

    def test_empty_both_returns_empty(self):
        from core.analytics import preparar_comparativo_categorias
        result = preparar_comparativo_categorias([], [])
        assert result == []

    def test_row_has_required_keys(self):
        from core.analytics import preparar_comparativo_categorias
        txs = [_tx(100.0, 1, cat="Alimentação")]
        result = preparar_comparativo_categorias(txs, [])
        row = result[0]
        assert "categoria" in row
        assert "Este mês" in row
        assert "Mês anterior" in row

    def test_current_month_aggregated(self):
        from core.analytics import preparar_comparativo_categorias
        txs = [_tx(60.0, 1, cat="Alimentação"), _tx(40.0, 5, cat="Alimentação")]
        result = preparar_comparativo_categorias(txs, [])
        row = next(r for r in result if r["categoria"] == "Alimentação")
        assert abs(row["Este mês"] - 100.0) < 0.01

    def test_previous_month_aggregated(self):
        from core.analytics import preparar_comparativo_categorias
        current = [_tx(50.0, 1, cat="Transporte")]
        previous = [_tx(80.0, 1, cat="Transporte")]
        result = preparar_comparativo_categorias(current, previous)
        row = next(r for r in result if r["categoria"] == "Transporte")
        assert abs(row["Mês anterior"] - 80.0) < 0.01

    def test_missing_category_in_previous_is_zero(self):
        from core.analytics import preparar_comparativo_categorias
        txs = [_tx(100.0, 1, cat="Saúde")]
        result = preparar_comparativo_categorias(txs, [])
        row = next(r for r in result if r["categoria"] == "Saúde")
        assert row["Mês anterior"] == 0.0

    def test_missing_category_in_current_included_when_in_previous(self):
        from core.analytics import preparar_comparativo_categorias
        previous = [_tx(200.0, 1, cat="Educação")]
        result = preparar_comparativo_categorias([], previous)
        cats = [r["categoria"] for r in result]
        assert "Educação" in cats

    def test_excludes_ganhos(self):
        from core.analytics import preparar_comparativo_categorias
        txs = [_tx(5000.0, 1, tipo="GANHO", cat="Renda"), _tx(100.0, 1, cat="Alimentação")]
        result = preparar_comparativo_categorias(txs, [])
        cats = [r["categoria"] for r in result]
        assert "Renda" not in cats
        assert "Alimentação" in cats

    def test_top_n_limits_results(self):
        from core.analytics import preparar_comparativo_categorias
        cats = ["Alimentação", "Transporte", "Saúde", "Lazer", "Educação"]
        txs = [_tx(100.0 * (i + 1), 1, cat=c) for i, c in enumerate(cats)]
        result = preparar_comparativo_categorias(txs, [], top_n=3)
        assert len(result) <= 3

    def test_sorted_by_current_month_desc(self):
        from core.analytics import preparar_comparativo_categorias
        txs = [
            _tx(50.0, 1, cat="Alimentação"),
            _tx(200.0, 1, cat="Transporte"),
            _tx(100.0, 1, cat="Saúde"),
        ]
        result = preparar_comparativo_categorias(txs, [])
        valores = [r["Este mês"] for r in result]
        assert valores == sorted(valores, reverse=True)

    def test_values_are_floats(self):
        from core.analytics import preparar_comparativo_categorias
        txs = [_tx(77.50, 1, cat="Lazer")]
        result = preparar_comparativo_categorias(txs, [])
        row = result[0]
        assert isinstance(row["Este mês"], float)
        assert isinstance(row["Mês anterior"], float)
