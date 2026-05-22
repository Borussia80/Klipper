"""
TDD Red→Green: _to_db() deve converter Decimal para str e garantir que
model_dump() produz um dict serializável em JSON antes de ir ao Supabase.
"""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

import pytest

from models.bank_account import BankAccount, AccountType
from models.budget import Budget
from models.credit_card import CreditCard
from models.installment import Installment
from models.transaction import Category, PaymentMethod, Transaction, TransactionType


def _serialize_for_supabase(data: dict) -> str:
    """Proxy que simula o que o cliente Supabase faz internamente."""
    return json.dumps(data)


def _build_tx() -> dict:
    tx = Transaction(
        date=date(2026, 5, 22),
        amount=Decimal("45.90"),
        type=TransactionType.GASTO,
        category=Category.ALIMENTACAO,
    )
    from core.repositories import _to_db
    data = _to_db(tx.model_dump())
    data["date"] = data["date"].isoformat()
    data["type"] = data["type"].value
    data["category"] = data["category"].value
    data["payment_method"] = data["payment_method"].value
    data["status"] = data["status"].value
    return data


class TestToDb:
    def test_decimal_convertido_para_string(self):
        from core.repositories import _to_db
        result = _to_db({"amount": Decimal("45.90")})
        assert result["amount"] == "45.90"
        assert isinstance(result["amount"], str)

    def test_valores_nao_decimal_preservados(self):
        from core.repositories import _to_db
        result = _to_db({"name": "test", "n": 42, "flag": True, "nul": None})
        assert result == {"name": "test", "n": 42, "flag": True, "nul": None}

    def test_decimal_zero_vira_string(self):
        from core.repositories import _to_db
        result = _to_db({"balance": Decimal("0")})
        assert result["balance"] == "0"

    def test_decimal_grande_preserva_precisao(self):
        from core.repositories import _to_db
        result = _to_db({"amount": Decimal("1500.00")})
        assert result["amount"] == "1500.00"


class TestTransactionSerializacao:
    def test_transaction_serializa_sem_erro(self):
        data = _build_tx()
        assert _serialize_for_supabase(data) is not None

    def test_amount_e_string_no_payload(self):
        data = _build_tx()
        assert isinstance(data["amount"], str)
        assert data["amount"] == "45.90"

    def test_centavos_preservados(self):
        from core.repositories import _to_db
        tx = Transaction(
            date=date(2026, 5, 22),
            amount=Decimal("33.33"),
            type=TransactionType.GASTO,
            category=Category.ALIMENTACAO,
        )
        data = _to_db(tx.model_dump())
        assert data["amount"] == "33.33"


class TestOutrosModelos:
    def test_bank_account_serializa(self):
        from core.repositories import _to_db
        acc = BankAccount(name="Nubank", bank="Nu", type=AccountType.CORRENTE, balance=Decimal("1500.50"))
        data = _to_db(acc.model_dump())
        assert isinstance(data["balance"], str)
        assert json.dumps({**data, "type": data["type"].value}) is not None

    def test_credit_card_serializa(self):
        from core.repositories import _to_db
        card = CreditCard(name="Inter", limit_total=Decimal("5000.00"))
        data = _to_db(card.model_dump())
        assert isinstance(data["limit_total"], str)
        assert json.dumps(data) is not None

    def test_budget_serializa(self):
        from core.repositories import _to_db
        budget = Budget(category="Alimentação", monthly_limit=Decimal("800.00"), year=2026, month=5)
        data = _to_db(budget.model_dump())
        assert isinstance(data["monthly_limit"], str)
        assert json.dumps(data) is not None
