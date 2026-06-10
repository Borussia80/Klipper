"""Testes dos routers FastAPI — mock do core/ e do JWT."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

FAKE_USER_ID = "d82db08b-d2d1-4d28-adf8-2cd4bacf7165"


@pytest.fixture
def client():
    from api.auth import get_current_user
    from api.main import app

    app.dependency_overrides[get_current_user] = lambda: FAKE_USER_ID
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── Health ────────────────────────────────────────────────────────────────────

def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# ── Auth: rota protegida sem override deve retornar 401 ──────────────────────

def test_no_auth_returns_401() -> None:
    from api.main import app
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/quotes/MXRF11")
    assert resp.status_code == 401


# ── Quotes ────────────────────────────────────────────────────────────────────

def test_get_quote_success(client: TestClient) -> None:
    mock_svc = MagicMock()
    mock_quote = MagicMock()
    mock_quote.current_price = 145.50
    mock_svc.get_fii.return_value = mock_quote

    with patch("core.market_data.get_market_service", return_value=mock_svc), \
         patch("core.market_data.is_fii", return_value=True):
        resp = client.get("/quotes/MXRF11")

    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "MXRF11"
    assert data["price"] == 145.50


def test_get_quote_uppercase(client: TestClient) -> None:
    mock_svc = MagicMock()
    mock_quote = MagicMock()
    mock_quote.current_price = 10.0
    mock_svc.get_fii.return_value = mock_quote

    with patch("core.market_data.get_market_service", return_value=mock_svc), \
         patch("core.market_data.is_fii", return_value=True):
        resp = client.get("/quotes/mxrf11")

    assert resp.json()["ticker"] == "MXRF11"


def test_get_quote_not_found(client: TestClient) -> None:
    mock_svc = MagicMock()
    mock_svc.get_stock.return_value = None

    with patch("core.market_data.get_market_service", return_value=mock_svc), \
         patch("core.market_data.is_fii", return_value=False):
        resp = client.get("/quotes/XXXX99")

    assert resp.status_code == 404


def test_get_quote_market_error(client: TestClient) -> None:
    with patch("core.market_data.get_market_service", side_effect=Exception("timeout")):
        resp = client.get("/quotes/FAIL11")
    assert resp.status_code == 502


# ── Engines M1 ────────────────────────────────────────────────────────────────

def test_m1_score(client: TestClient) -> None:
    from core.m1_quant import calcular_score_m1
    mock_result = {"score": 0.72, "decisao": "COMPRAR"}

    with patch("core.m1_quant.calcular_score_m1", return_value=mock_result):
        resp = client.get("/engines/m1/MXRF11")

    assert resp.status_code == 200
    assert resp.json()["ticker"] == "MXRF11"
    assert resp.json()["score"] == 0.72


# ── Statement Import ──────────────────────────────────────────────────────────

def test_import_statement_pdf(client: TestClient) -> None:
    mock_result = MagicMock()
    mock_tx = MagicMock()
    mock_tx.__dict__ = {"date": "2026-06-01", "amount": 150.0, "category": "Alimentação"}
    mock_result.transactions = [mock_tx]

    with patch("core.statement_reader.read_statement", return_value=mock_result):
        resp = client.post(
            "/import/statement",
            files={"file": ("extrato.pdf", b"%PDF-1.4 fake", "application/pdf")},
        )

    assert resp.status_code == 200
    assert resp.json()["count"] == 1


def test_import_statement_unsupported_format(client: TestClient) -> None:
    resp = client.post(
        "/import/statement",
        files={"file": ("doc.docx", b"fake", "application/vnd.openxmlformats")},
    )
    assert resp.status_code == 415


def test_import_statement_too_large(client: TestClient) -> None:
    large_content = b"X" * (11 * 1024 * 1024)
    resp = client.post(
        "/import/statement",
        files={"file": ("big.pdf", large_content, "application/pdf")},
    )
    assert resp.status_code == 413


# ── Kira ─────────────────────────────────────────────────────────────────────

def test_kira_chat_empty_message(client: TestClient) -> None:
    resp = client.post("/kira/chat", json={"message": "  "})
    assert resp.status_code == 422


def test_kira_chat_returns_stream(client: TestClient) -> None:
    with patch("core.financial_ai.ask", return_value="Análise do MXRF11: bom DY."):
        resp = client.post("/kira/chat", json={"message": "Analise MXRF11"})
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
