"""TDD Sprint 06 — Filter chips e paginação no ledger de Transações."""
from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import date


# ── Helpers para criar transações de teste ─────────────────────────────────────

def _tx(pm: str = "PIX", installment_id: str | None = None,
        category: str = "Alimentação", tx_type: str = "GASTO"):
    from models.transaction import (
        Transaction, TransactionType, Category, PaymentMethod, TransactionStatus
    )
    return Transaction(
        date=date(2026, 5, 10),
        amount=Decimal("100"),
        type=TransactionType(tx_type),
        category=Category(category),
        payment_method=PaymentMethod(pm),
        installment_id=installment_id,
        status=TransactionStatus.PAGO,
    )


# ── filter_transactions_by_chip ───────────────────────────────────────────────

class TestFilterTransactionsByChip:
    """filter_transactions_by_chip(txs, chip) retorna subconjunto filtrado."""

    def test_todos_returns_all(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx("PIX"), _tx("CARTAO_CREDITO")]
        result = filter_transactions_by_chip(txs, "Todos")
        assert len(result) == 2

    def test_pix_returns_only_pix(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx("PIX"), _tx("CARTAO_CREDITO"), _tx("PIX")]
        result = filter_transactions_by_chip(txs, "PIX")
        assert len(result) == 2
        assert all(t.payment_method.value == "PIX" for t in result)

    def test_cartao_returns_credit_and_debit(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx("PIX"), _tx("CARTAO_CREDITO"), _tx("CARTAO_DEBITO"), _tx("TED")]
        result = filter_transactions_by_chip(txs, "Cartão")
        assert len(result) == 2
        assert all(t.payment_method.value in ("CARTAO_CREDITO", "CARTAO_DEBITO") for t in result)

    def test_parcelas_returns_installment_txs(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx(installment_id="abc-123"), _tx(), _tx(installment_id="def-456")]
        result = filter_transactions_by_chip(txs, "Parcelas")
        assert len(result) == 2
        assert all(t.installment_id is not None for t in result)

    def test_parcelas_excludes_non_installment(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx(), _tx()]  # no installment_id
        result = filter_transactions_by_chip(txs, "Parcelas")
        assert result == []

    def test_unknown_chip_returns_all(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx("PIX"), _tx("TED")]
        result = filter_transactions_by_chip(txs, "Desconhecido")
        assert len(result) == 2

    def test_preserves_order(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx("PIX"), _tx("PIX"), _tx("PIX")]
        result = filter_transactions_by_chip(txs, "PIX")
        assert result == txs

    def test_empty_list_returns_empty(self):
        from core.ledger_filters import filter_transactions_by_chip
        result = filter_transactions_by_chip([], "PIX")
        assert result == []

    def test_dinheiro_chip(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx("DINHEIRO"), _tx("PIX"), _tx("BOLETO")]
        result = filter_transactions_by_chip(txs, "Dinheiro")
        assert len(result) == 1
        assert result[0].payment_method.value == "DINHEIRO"

    def test_ted_chip(self):
        from core.ledger_filters import filter_transactions_by_chip
        txs = [_tx("TED"), _tx("PIX")]
        result = filter_transactions_by_chip(txs, "TED")
        assert len(result) == 1


# ── paginate_transactions ──────────────────────────────────────────────────────

class TestPaginateTransactions:
    """paginate_transactions(txs, page, page_size) retorna slice correto."""

    def _many(self, n: int):
        return [_tx() for _ in range(n)]

    def test_page_1_returns_first_n(self):
        from core.ledger_filters import paginate_transactions
        txs = self._many(50)
        result = paginate_transactions(txs, page=1, page_size=30)
        assert len(result) == 30
        assert result == txs[:30]

    def test_page_2_returns_rest(self):
        from core.ledger_filters import paginate_transactions
        txs = self._many(50)
        result = paginate_transactions(txs, page=2, page_size=30)
        assert len(result) == 20
        assert result == txs[30:]

    def test_less_than_page_size_returns_all(self):
        from core.ledger_filters import paginate_transactions
        txs = self._many(10)
        result = paginate_transactions(txs, page=1, page_size=30)
        assert len(result) == 10

    def test_empty_returns_empty(self):
        from core.ledger_filters import paginate_transactions
        result = paginate_transactions([], page=1, page_size=30)
        assert result == []

    def test_page_beyond_end_returns_empty(self):
        from core.ledger_filters import paginate_transactions
        txs = self._many(10)
        result = paginate_transactions(txs, page=3, page_size=30)
        assert result == []

    def test_total_pages_exact_division(self):
        from core.ledger_filters import total_pages
        assert total_pages(60, page_size=30) == 2

    def test_total_pages_remainder(self):
        from core.ledger_filters import total_pages
        assert total_pages(31, page_size=30) == 2

    def test_total_pages_zero(self):
        from core.ledger_filters import total_pages
        assert total_pages(0, page_size=30) == 1

    def test_total_pages_exact_one_page(self):
        from core.ledger_filters import total_pages
        assert total_pages(30, page_size=30) == 1

    def test_custom_page_size(self):
        from core.ledger_filters import paginate_transactions
        txs = self._many(25)
        result = paginate_transactions(txs, page=1, page_size=10)
        assert len(result) == 10
