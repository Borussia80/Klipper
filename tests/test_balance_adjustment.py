"""TDD Red — débito/crédito automático de conta ao criar/editar transações."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from models.transaction import TransactionType


class TestTxBalanceDelta:
    """tx_balance_delta(amount, tx_type) → signed float."""

    def test_gasto_returns_negative(self):
        from core.repositories import tx_balance_delta
        assert tx_balance_delta(200.0, TransactionType.GASTO) == pytest.approx(-200.0)

    def test_ganho_returns_positive(self):
        from core.repositories import tx_balance_delta
        assert tx_balance_delta(200.0, TransactionType.GANHO) == pytest.approx(200.0)

    def test_zero_amount(self):
        from core.repositories import tx_balance_delta
        assert tx_balance_delta(0.0, TransactionType.GASTO) == pytest.approx(0.0)

    def test_decimal_amount_gasto(self):
        from core.repositories import tx_balance_delta
        assert tx_balance_delta(99.99, TransactionType.GASTO) == pytest.approx(-99.99)


class TestBankAccountAdjustBalance:
    """BankAccountRepository.adjust_balance(account_id, delta) aplica delta ao saldo."""

    def _make_account(self, balance: float = 1000.0):
        from models.bank_account import BankAccount, AccountType
        return BankAccount(
            id="test-id",
            name="Conta Teste",
            bank="Banco",
            type=AccountType.CORRENTE,
            balance=Decimal(str(balance)),
        )

    def test_debit_reduces_balance(self):
        from core.repositories import BankAccountRepository
        repo = BankAccountRepository()
        account = self._make_account(1000.0)
        with patch.object(repo, "get_by_id", return_value=account):
            with patch.object(repo, "update_balance") as mock_update:
                repo.adjust_balance("test-id", -200.0)
                mock_update.assert_called_once_with("test-id", pytest.approx(800.0))

    def test_credit_increases_balance(self):
        from core.repositories import BankAccountRepository
        repo = BankAccountRepository()
        account = self._make_account(1000.0)
        with patch.object(repo, "get_by_id", return_value=account):
            with patch.object(repo, "update_balance") as mock_update:
                repo.adjust_balance("test-id", 500.0)
                mock_update.assert_called_once_with("test-id", pytest.approx(1500.0))

    def test_zero_delta_keeps_balance(self):
        from core.repositories import BankAccountRepository
        repo = BankAccountRepository()
        account = self._make_account(750.0)
        with patch.object(repo, "get_by_id", return_value=account):
            with patch.object(repo, "update_balance") as mock_update:
                repo.adjust_balance("test-id", 0.0)
                mock_update.assert_called_once_with("test-id", pytest.approx(750.0))

    def test_unknown_account_raises(self):
        from core.repositories import BankAccountRepository
        repo = BankAccountRepository()
        with patch.object(repo, "get_by_id", return_value=None):
            with pytest.raises(ValueError, match="não encontrada"):
                repo.adjust_balance("ghost-id", -100.0)
