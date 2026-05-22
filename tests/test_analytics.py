from __future__ import annotations

from datetime import date

from core.analytics import calcular_saldo_mensal, calcular_top_categorias
from models.transaction import Category, Transaction, TransactionType


_FIXED_DATE = date(2026, 5, 15)


def _make_tx(
    amount: float,
    tipo: TransactionType,
    cat: Category,
    tx_date: date | None = None,
) -> Transaction:
    return Transaction(date=tx_date or _FIXED_DATE, amount=amount, type=tipo, category=cat)


class TestCalcularSaldoMensal:
    def test_saldo_positivo(self):
        txs = [
            _make_tx(5000, TransactionType.GANHO, Category.RENDA),
            _make_tx(2000, TransactionType.GASTO, Category.MORADIA),
        ]
        saldo = calcular_saldo_mensal(txs, 2026, 5)
        assert saldo.total_ganhos == 5000
        assert saldo.total_gastos == 2000
        assert saldo.saldo == 3000

    def test_taxa_poupanca(self):
        txs = [
            _make_tx(10000, TransactionType.GANHO, Category.RENDA),
            _make_tx(7000, TransactionType.GASTO, Category.OUTROS),
        ]
        saldo = calcular_saldo_mensal(txs, 2026, 5)
        assert saldo.taxa_poupanca == 30.0

    def test_sem_transacoes(self):
        saldo = calcular_saldo_mensal([], 2026, 5)
        assert saldo.saldo == 0
        assert saldo.taxa_poupanca == 0

    def test_filtra_transacoes_por_competencia(self):
        txs = [
            _make_tx(5000, TransactionType.GANHO, Category.RENDA, date(2026, 5, 10)),
            _make_tx(1500, TransactionType.GASTO, Category.MORADIA, date(2026, 5, 11)),
            _make_tx(9999, TransactionType.GANHO, Category.RENDA, date(2026, 4, 30)),
            _make_tx(9999, TransactionType.GASTO, Category.LAZER, date(2025, 5, 10)),
        ]
        saldo = calcular_saldo_mensal(txs, 2026, 5)
        assert saldo.total_ganhos == 5000
        assert saldo.total_gastos == 1500
        assert saldo.saldo == 3500


class TestCalcularTopCategorias:
    def test_ordena_por_maior_gasto(self):
        txs = [
            _make_tx(3000, TransactionType.GASTO, Category.MORADIA),
            _make_tx(1000, TransactionType.GASTO, Category.ALIMENTACAO),
            _make_tx(500, TransactionType.GASTO, Category.TRANSPORTE),
        ]
        top = calcular_top_categorias(txs, n=3)
        assert top[0].category == Category.MORADIA.value
        assert top[-1].category == Category.TRANSPORTE.value

    def test_ignora_ganhos(self):
        txs = [
            _make_tx(5000, TransactionType.GANHO, Category.RENDA),
            _make_tx(2000, TransactionType.GASTO, Category.MORADIA),
        ]
        top = calcular_top_categorias(txs)
        assert all(c.category != Category.RENDA.value for c in top)

    def test_retorna_n_maximo(self):
        txs = [_make_tx(100, TransactionType.GASTO, cat) for cat in list(Category)[:6]]
        top = calcular_top_categorias(txs, n=3)
        assert len(top) <= 3
