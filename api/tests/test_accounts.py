"""Tests for api/routers/accounts.py — GET /accounts/invoice and /accounts/commitment."""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


FAKE_USER_ID = "user-1"


@pytest.fixture()
def client() -> TestClient:
    from api.main import app
    from api.auth import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FAKE_USER_ID
    yield TestClient(app)
    app.dependency_overrides.clear()


def _auth() -> dict:
    return {"Authorization": "Bearer fake-token"}


def _card() -> MagicMock:
    card = MagicMock()
    card.id          = "card-1"
    card.closing_day = 5
    card.due_day     = 15
    return card


def _invoice(total: float = 350.0) -> MagicMock:
    inv = MagicMock()
    inv.total        = total
    inv.count        = 3
    inv.closing_date = date(2026, 6, 5)
    inv.due_date     = date(2026, 6, 15)
    return inv


# ── GET /accounts/invoice ─────────────────────────────────────────────────────

class TestGetInvoice:
    def test_returns_invoice_totals(self, client: TestClient) -> None:
        with (
            patch("api.routers.accounts.CreditCardRepository") as MockRepo,
            patch("api.routers.accounts.TransactionRepository") as MockTxRepo,
            patch("api.routers.accounts.invoice_by_due_month", return_value=_invoice(350.0)),
        ):
            MockRepo.return_value.get_by_id.return_value = _card()
            MockTxRepo.return_value.list_by_card.return_value = []

            r = client.get("/accounts/invoice?card_id=card-1")

        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 350.0
        assert body["count"] == 3
        assert body["card_id"] == "card-1"

    def test_404_when_card_not_found(self, client: TestClient) -> None:
        with patch("api.routers.accounts.CreditCardRepository") as MockRepo:
            MockRepo.return_value.get_by_id.return_value = None
            r = client.get("/accounts/invoice?card_id=nonexistent")

        assert r.status_code == 404

    def test_uses_current_month_when_no_year_month(self, client: TestClient) -> None:
        today = date.today()
        with (
            patch("api.routers.accounts.CreditCardRepository") as MockRepo,
            patch("api.routers.accounts.TransactionRepository") as MockTxRepo,
            patch("api.routers.accounts.invoice_by_due_month", return_value=_invoice()) as mock_inv,
        ):
            MockRepo.return_value.get_by_id.return_value = _card()
            MockTxRepo.return_value.list_by_card.return_value = []
            r = client.get("/accounts/invoice?card_id=card-1")

        assert r.status_code == 200
        args = mock_inv.call_args[0]
        assert args[2] == today.year
        assert args[3] == today.month


# ── GET /accounts/commitment ──────────────────────────────────────────────────

class TestGetCommitment:
    def test_returns_monthly_dict(self, client: TestClient) -> None:
        commitment_data = {"2026-07": Decimal("500.00"), "2026-08": Decimal("500.00")}

        with (
            patch("api.routers.accounts.InstallmentRepository") as MockInst,
            patch("api.routers.accounts.calcular_comprometimento_mensal", return_value=commitment_data),
        ):
            MockInst.return_value.list_active.return_value = []
            r = client.get("/accounts/commitment")

        assert r.status_code == 200
        body = r.json()
        assert body["2026-07"] == 500.0
        assert body["2026-08"] == 500.0

    def test_empty_when_no_installments(self, client: TestClient) -> None:
        with (
            patch("api.routers.accounts.InstallmentRepository") as MockInst,
            patch("api.routers.accounts.calcular_comprometimento_mensal", return_value={}),
        ):
            MockInst.return_value.list_active.return_value = []
            r = client.get("/accounts/commitment")

        assert r.status_code == 200
        assert r.json() == {}
