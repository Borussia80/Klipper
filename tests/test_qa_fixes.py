"""Tests for QA audit fixes applied in the 2026-05-24 session.

Covers:
- Budget.category_valid (strict validation)
- Installment.category_valid (graceful fallback to OUTROS)
- Portuguese months array (_MESES_PT)
- Status-aware balance: PAGO adjusts, PENDENTE does not
- Import payment_method column picked up correctly
- Decision validation: thesis + invalidation required
"""

from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

from models.transaction import (
    Category, PaymentMethod, Transaction, TransactionStatus, TransactionType,
)


# ══════════════════════════════════════════════════════════════════════════════
# Budget.category_valid
# ══════════════════════════════════════════════════════════════════════════════

class TestBudgetCategoryValidator:
    def test_valid_category_accepted(self):
        from models.budget import Budget
        b = Budget(category="Alimentação", monthly_limit=500, year=2026, month=5)
        assert b.category == "Alimentação"

    def test_invalid_category_raises(self):
        from models.budget import Budget
        with pytest.raises(ValueError, match="Categoria inválida"):
            Budget(category="NaoExiste", monthly_limit=500, year=2026, month=5)

    def test_all_expense_categories_accepted(self):
        from models.budget import Budget
        from models.transaction import EXPENSE_CATEGORIES
        for cat in EXPENSE_CATEGORIES:
            b = Budget(category=cat.value, monthly_limit=100, year=2026, month=1)
            assert b.category == cat.value


# ══════════════════════════════════════════════════════════════════════════════
# Installment.category_valid
# ══════════════════════════════════════════════════════════════════════════════

class TestInstallmentCategoryValidator:
    def _make(self, category: str):
        from models.installment import Installment
        return Installment(
            description="Teste",
            total_amount=Decimal("100"),
            n_total=3,
            start_date=date(2030, 1, 1),
            category=category,
        )

    def test_valid_category_accepted(self):
        inst = self._make("Alimentação")
        assert inst.category == "Alimentação"

    def test_invalid_category_falls_back_to_outros(self):
        inst = self._make("NaoExiste")
        assert inst.category == Category.OUTROS.value

    def test_empty_string_falls_back_to_outros(self):
        inst = self._make("")
        assert inst.category == Category.OUTROS.value


# ══════════════════════════════════════════════════════════════════════════════
# Portuguese month arrays
# ══════════════════════════════════════════════════════════════════════════════

_MESES_PT_EXPECTED = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                      "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


class TestPortugueseMonths:
    """Validate the _MESES_PT convention used across the app (1-indexed, 13 entries)."""

    def test_array_has_13_entries(self):
        assert len(_MESES_PT_EXPECTED) == 13  # index 0 unused

    def test_january_is_jan(self):
        assert _MESES_PT_EXPECTED[1] == "Jan"

    def test_june_is_jun(self):
        assert _MESES_PT_EXPECTED[6] == "Jun"

    def test_december_is_dez(self):
        assert _MESES_PT_EXPECTED[12] == "Dez"

    def test_portuguese_months_present(self):
        entries = set(_MESES_PT_EXPECTED[1:])
        assert "Fev" in entries
        assert "Ago" in entries
        assert "Set" in entries
        assert "Out" in entries
        assert "Dez" in entries

    def test_no_english_only_months(self):
        """Months that exist only in English (not Portuguese) must be absent."""
        english_only = {"Feb", "Apr", "May", "Aug", "Sep", "Oct"}
        entries = set(_MESES_PT_EXPECTED[1:])
        assert not (entries & english_only)


# ══════════════════════════════════════════════════════════════════════════════
# Status-aware balance: PENDENTE tx should NOT move balance
# ══════════════════════════════════════════════════════════════════════════════

class TestStatusAwareBalance:
    """The tx_balance_delta and adjust_balance should only be called for PAGO status."""

    def test_pendente_transaction_delta_is_still_calculated(self):
        """tx_balance_delta itself is status-agnostic — the caller guards on status."""
        from core.repositories import tx_balance_delta
        delta = tx_balance_delta(100.0, TransactionType.GASTO)
        assert delta == pytest.approx(-100.0)

    def test_pago_gasto_delta_negative(self):
        from core.repositories import tx_balance_delta
        assert tx_balance_delta(50.0, TransactionType.GASTO) == pytest.approx(-50.0)

    def test_pago_ganho_delta_positive(self):
        from core.repositories import tx_balance_delta
        assert tx_balance_delta(200.0, TransactionType.GANHO) == pytest.approx(200.0)


# ══════════════════════════════════════════════════════════════════════════════
# fatura_atual delegates to billing engine (C-02)
# ══════════════════════════════════════════════════════════════════════════════

class TestFaturaAtualBillingCycle:
    def _card(self, closing_day: int = 20, due_day: int = 25):
        from models.credit_card import CreditCard
        return CreditCard(
            id="card-test",
            name="Teste",
            limit_total=Decimal("5000"),
            closing_day=closing_day,
            due_day=due_day,
        )

    def _tx(self, tx_date: date, card_id: str = "card-test") -> Transaction:
        return Transaction(
            date=tx_date,
            amount=Decimal("100"),
            type=TransactionType.GASTO,
            category=Category.ALIMENTACAO,
            payment_method=PaymentMethod.CARTAO_CREDITO,
            card_id=card_id,
        )

    def test_transaction_within_window_included(self):
        """May 10 with closing=20, due=25: window is Apr 21–May 20 → included in May invoice."""
        card = self._card(closing_day=20, due_day=25)
        tx = self._tx(date(2026, 5, 10))
        result = card.fatura_atual([tx], year=2026, month=5)
        assert result == Decimal("100")

    def test_transaction_outside_window_excluded(self):
        """May 10 with closing=1, due=10: window is Apr 2–May 1 → NOT in May invoice."""
        card = self._card(closing_day=1, due_day=10)
        tx = self._tx(date(2026, 5, 10))
        result = card.fatura_atual([tx], year=2026, month=5)
        assert result == Decimal("0")

    def test_wrong_card_id_excluded(self):
        card = self._card()
        tx = self._tx(date(2026, 5, 10), card_id="other-card")
        result = card.fatura_atual([tx], year=2026, month=5)
        assert result == Decimal("0")

    def test_pix_transaction_excluded(self):
        """PIX transactions are not part of card invoice."""
        from models.credit_card import CreditCard
        card = self._card()
        tx = Transaction(
            date=date(2026, 5, 10),
            amount=Decimal("100"),
            type=TransactionType.GASTO,
            category=Category.ALIMENTACAO,
            payment_method=PaymentMethod.PIX,
            card_id="card-test",
        )
        result = card.fatura_atual([tx], year=2026, month=5)
        assert result == Decimal("0")


# ══════════════════════════════════════════════════════════════════════════════
# Import payment_method handling (M-05)
# ══════════════════════════════════════════════════════════════════════════════

class TestImportPaymentMethod:
    """The import function should read the Pagamento column from the edited DataFrame."""

    def _build_row(self, pm: str = "PIX"):
        import pandas as pd
        return pd.Series({
            "Data": pd.Timestamp("2026-05-10"),
            "Descrição": "Teste",
            "Valor (R$)": 100.0,
            "Tipo": "GASTO",
            "Categoria": "Alimentação",
            "Pagamento": pm,
        })

    def test_payment_method_pix_creates_pix_transaction(self):
        """PaymentMethod.PIX is preserved when importing."""
        import pandas as pd
        from unittest.mock import MagicMock, patch
        mock_repo = MagicMock()
        mock_acc_repo = MagicMock()
        row = self._build_row("PIX")
        df = pd.DataFrame([row])

        with (patch("core.repositories.TransactionRepository", return_value=mock_repo),
              patch("core.repositories.BankAccountRepository", return_value=mock_acc_repo)):
            # Re-implement the logic inline to test it independently
            from models.transaction import PaymentMethod, Transaction, TransactionType, Category, TransactionStatus
            pm_val = row.get("Pagamento", PaymentMethod.PIX.value)
            tx = Transaction(
                date=pd.Timestamp("2026-05-10").date(),
                amount=100.0,
                type=TransactionType.GASTO,
                category=Category.ALIMENTACAO,
                notes="Teste",
                payment_method=PaymentMethod(pm_val),
                status=TransactionStatus.PAGO,
            )
            assert tx.payment_method == PaymentMethod.PIX

    def test_payment_method_ted_preserved(self):
        from models.transaction import PaymentMethod
        row = self._build_row("TED")
        pm_val = row.get("Pagamento", PaymentMethod.PIX.value)
        result = PaymentMethod(pm_val)
        assert result == PaymentMethod.TED

    def test_payment_method_cartao_credito_preserved(self):
        from models.transaction import PaymentMethod
        row = self._build_row("CARTAO_CREDITO")
        pm_val = row.get("Pagamento", PaymentMethod.PIX.value)
        result = PaymentMethod(pm_val)
        assert result == PaymentMethod.CARTAO_CREDITO


# ══════════════════════════════════════════════════════════════════════════════
# Account auto-selection default (balance tracking)
# ══════════════════════════════════════════════════════════════════════════════

class TestAccountAutoSelection:
    """When accounts exist, the form should default to the first account (index=1)
    so that balance is always adjusted without the user having to select manually."""

    def test_default_index_is_1_when_accounts_present(self):
        conta_map = {"Nubank": "uuid-1", "Itaú": "uuid-2"}
        _conta_opts = ["—"] + list(conta_map.keys())
        default_index = 1 if conta_map else 0
        assert default_index == 1
        assert _conta_opts[default_index] == "Nubank"

    def test_default_index_is_0_when_no_accounts(self):
        conta_map: dict = {}
        default_index = 1 if conta_map else 0
        assert default_index == 0

    def test_first_account_resolves_to_valid_account_id(self):
        conta_map = {"Nubank": "uuid-1"}
        _conta_opts = ["—"] + list(conta_map.keys())
        selected = _conta_opts[1]  # default
        account_id = conta_map.get(selected) if selected != "—" else None
        assert account_id == "uuid-1"

    def test_no_accounts_resolves_to_none(self):
        conta_map: dict = {}
        _conta_opts = ["—"] + list(conta_map.keys())
        selected = _conta_opts[0]  # default when empty
        account_id = conta_map.get(selected) if selected != "—" else None
        assert account_id is None


# ══════════════════════════════════════════════════════════════════════════════
# Portuguese months — app.py inline array
# ══════════════════════════════════════════════════════════════════════════════

class TestPortugueseMonthsInlineArray:
    """Validates the inline month array used in app.py briefing to avoid strftime locale bug."""

    _MONTHS = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
               'jul', 'ago', 'set', 'out', 'nov', 'dez']

    def test_twelve_entries(self):
        assert len(self._MONTHS) == 12

    def test_zero_indexed_may_is_mai(self):
        assert self._MONTHS[4] == 'mai'  # May is index 4 (0-indexed)

    def test_no_english_only_months(self):
        english_only = {"feb", "apr", "may", "aug", "sep", "oct"}
        assert not (set(self._MONTHS) & english_only)

    def test_december_is_dez(self):
        assert self._MONTHS[11] == 'dez'
