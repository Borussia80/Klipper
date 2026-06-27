"""Tests for api/routers/budget.py — POST /budget/suggest, GET /budget/status, GET /budget/alerts."""

from __future__ import annotations

import sys
from pathlib import Path
from decimal import Decimal
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


class TestBudgetSuggest:
    def test_returns_50_30_20_distribution(self, client: TestClient) -> None:
        r = client.post("/budget/suggest", json={
            "monthly_income": 10000,
            "categories": ["Moradia", "Lazer", "Investimento"],
        })
        assert r.status_code == 200
        body = r.json()
        assert body["Moradia"]     == pytest.approx(5000.0)
        assert body["Lazer"]       == pytest.approx(3000.0)
        assert body["Investimento"] == pytest.approx(2000.0)

    def test_422_when_income_zero(self, client: TestClient) -> None:
        r = client.post("/budget/suggest", json={
            "monthly_income": 0,
            "categories": ["Moradia"],
        })
        assert r.status_code == 422

    def test_empty_for_unknown_categories(self, client: TestClient) -> None:
        r = client.post("/budget/suggest", json={
            "monthly_income": 5000,
            "categories": ["CategoriaDesconhecida"],
        })
        assert r.status_code == 200
        assert r.json() == {}


class TestBudgetStatus:
    def test_returns_list(self, client: TestClient) -> None:
        from core.budget_engine import BudgetStatus
        from decimal import Decimal

        mock_status = [
            BudgetStatus(
                category="Alimentação",
                monthly_limit=Decimal("1000"),
                spent=Decimal("600"),
                pct_used=0.6,
                projected_close=Decimal("900"),
            )
        ]

        with (
            patch("api.routers.budget.BudgetRepository") as MockBudget,
            patch("api.routers.budget.TransactionRepository") as MockTx,
            patch("api.routers.budget.calcular_budget_status", return_value=mock_status),
        ):
            MockBudget.return_value.list_by_month.return_value = []
            MockTx.return_value.list_by_month.return_value     = []

            r = client.get("/budget/status")

        assert r.status_code == 200
        body = r.json()
        assert len(body) == 1
        assert body[0]["category"]  == "Alimentação"
        assert body[0]["spent"]     == pytest.approx(600.0)
        assert body[0]["pct_used"]  == pytest.approx(0.6)


class TestBudgetAlerts:
    def test_returns_empty_when_no_alerts(self, client: TestClient) -> None:
        with (
            patch("api.routers.budget.BudgetRepository") as MockBudget,
            patch("api.routers.budget.TransactionRepository") as MockTx,
            patch("api.routers.budget.gerar_alertas", return_value=[]),
        ):
            MockBudget.return_value.list_by_month.return_value = []
            MockTx.return_value.list_by_month.return_value     = []

            r = client.get("/budget/alerts")

        assert r.status_code == 200
        assert r.json() == []

    def test_includes_message_field(self, client: TestClient) -> None:
        from core.budget_engine import BudgetAlert

        mock_alert = BudgetAlert(
            category="Alimentação",
            pct_used=1.1,
            amount_spent=Decimal("1100"),
            monthly_limit=Decimal("1000"),
            overbudget=True,
            days_remaining=10,
        )

        with (
            patch("api.routers.budget.BudgetRepository") as MockBudget,
            patch("api.routers.budget.TransactionRepository") as MockTx,
            patch("api.routers.budget.gerar_alertas", return_value=[mock_alert]),
        ):
            MockBudget.return_value.list_by_month.return_value = []
            MockTx.return_value.list_by_month.return_value     = []

            r = client.get("/budget/alerts")

        assert r.status_code == 200
        body = r.json()
        assert len(body) == 1
        assert "message" in body[0]
        assert body[0]["overbudget"] is True
