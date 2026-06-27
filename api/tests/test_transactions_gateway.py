"""Testes do gateway POST /transactions — Fase 0.5.

Estratégia de mock:
  - api.routers.transactions.get_client → MagicMock (Supabase)
  - api.routers.transactions.categorize_with_memory → retorna suggestion fake
  - api.routers.transactions.CategoryMemoryRepository → mock da classe

Todos RED até a implementação de api/routers/transactions.py.

Seções cobertas (spec fase-0.5 §4):
  §4.1 — caminho feliz (simples, parcelado, rateado, parcelado+rateado, saldo, memória)
  §4.2 — validações 422
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


FAKE_USER_ID  = "d82db08b-d2d1-4d28-adf8-2cd4bacf7165"
FAKE_ACCOUNT_ID = "bbbbbbbb-0000-0000-0000-000000000001"
FAKE_CARD_ID    = "cccccccc-0000-0000-0000-000000000001"
FAKE_TX_ID      = "aaaaaaaa-0000-0000-0000-000000000001"
FAKE_INST_ID    = "dddddddd-0000-0000-0000-000000000001"
TODAY = date.today().isoformat()


# ── helpers ───────────────────────────────────────────────────────────────────

def _fake_suggestion(category="Transporte", source="memory", score=0.92, confident=True):
    s = MagicMock()
    s.category.value = category
    s.source = source
    s.score = score
    s.confident = confident
    return s


def _make_db(n_tx_rows: int = 1, account_balance: str = "1000.00") -> tuple[MagicMock, dict]:
    """Retorna (db_mock, registry) onde registry[table_name] é o mock da tabela.
    n_tx_rows: quantas linhas o INSERT de transactions retorna (1 simples, N parcelado).
    """
    registry: dict[str, MagicMock] = {}

    def _table(name: str) -> MagicMock:
        if name not in registry:
            registry[name] = MagicMock()
        return registry[name]

    db = MagicMock()
    db.table.side_effect = _table

    # bank_accounts — SELECT balance
    ba = _table("bank_accounts")
    ba_row = MagicMock()
    ba_row.data = {"balance": account_balance}
    (ba.select.return_value
       .eq.return_value
       .single.return_value
       .execute.return_value) = ba_row

    # transactions — INSERT (batch ou simples)
    tx_tbl = _table("transactions")
    tx_rows = [
        {
            "id": f"{FAKE_TX_ID[:-1]}{i}",
            "date": TODAY,
            "amount": "150.00",
            "type": "GASTO",
            "category": "Transporte",
            "notes": "Uber",
            "payment_method": "PIX",
            "account_id": FAKE_ACCOUNT_ID,
            "card_id": None,
            "installment_id": FAKE_INST_ID if n_tx_rows > 1 else None,
            "is_recurring": False,
            "status": "PAGO",
        }
        for i in range(n_tx_rows)
    ]
    tx_tbl.insert.return_value.execute.return_value = MagicMock(data=tx_rows)

    # installments — INSERT
    inst_tbl = _table("installments")
    inst_tbl.insert.return_value.execute.return_value = MagicMock(data=[{"id": FAKE_INST_ID}])

    # transaction_splits — INSERT
    splits_tbl = _table("transaction_splits")
    splits_tbl.insert.return_value.execute.return_value = MagicMock(data=[])

    return db, registry


def _base_payload(**overrides) -> dict:
    payload = {
        "date":           TODAY,
        "amount":         150.00,
        "type":           "GASTO",
        "notes":          "Uber",
        "payment_method": "PIX",
        "account_id":     FAKE_ACCOUNT_ID,
        "card_id":        None,
        "category":       "Transporte",
        "confirmed":      False,
        "is_recurring":   False,
        "n_installments": 1,
        "splits":         None,
    }
    payload.update(overrides)
    return payload


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    from api.auth import get_current_user
    from api.main import app

    app.dependency_overrides[get_current_user] = lambda: FAKE_USER_ID
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── §4.1 caminho feliz — transação simples ────────────────────────────────────

class TestTransacaoSimples:
    def test_retorna_201(self, client: TestClient):
        db, _ = _make_db()
        suggestion = _fake_suggestion()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=suggestion), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            resp = client.post("/transactions", json=_base_payload())
        assert resp.status_code == 201

    def test_installment_children_vazio(self, client: TestClient):
        db, _ = _make_db()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=_base_payload()).json()
        assert data["installment_children"] == []

    def test_splits_vazio(self, client: TestClient):
        db, _ = _make_db()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=_base_payload()).json()
        assert data["splits"] == []

    def test_transaction_id_presente(self, client: TestClient):
        db, _ = _make_db()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=_base_payload()).json()
        assert "id" in data["transaction"]

    def test_category_suggestion_presente(self, client: TestClient):
        db, _ = _make_db()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion(source="memory")), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=_base_payload()).json()
        assert data["category_suggestion"]["source"] == "memory"
        assert "confidence" in data["category_suggestion"]


# ── §4.1 caminho feliz — parcelamento ────────────────────────────────────────

class TestTransacaoParcelada:
    def test_3_parcelas_retorna_2_children(self, client: TestClient):
        db, _ = _make_db(n_tx_rows=3)
        payload = _base_payload(
            n_installments=3,
            payment_method="CARTAO_CREDITO",
            card_id=FAKE_CARD_ID,
            account_id=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=payload).json()
        assert len(data["installment_children"]) == 2

    def test_children_tem_mesmo_installment_id(self, client: TestClient):
        db, _ = _make_db(n_tx_rows=3)
        payload = _base_payload(
            n_installments=3,
            payment_method="CARTAO_CREDITO",
            card_id=FAKE_CARD_ID,
            account_id=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=payload).json()
        ids = {c["installment_id"] for c in data["installment_children"]}
        assert len(ids) == 1

    def test_soma_children_mais_principal_igual_ao_total(self, client: TestClient):
        total = 300.00
        db, _ = _make_db(n_tx_rows=3)
        # Ajusta mock: cada parcela = 100.00
        registry_tx = db.table("transactions")
        rows = [{"id": f"tx-{i}", "amount": "100.00", "installment_id": FAKE_INST_ID,
                 "date": TODAY, "type": "GASTO", "category": "Transporte",
                 "payment_method": "CARTAO_CREDITO", "card_id": FAKE_CARD_ID,
                 "account_id": None, "is_recurring": False, "status": "PENDENTE", "notes": ""}
                for i in range(3)]
        registry_tx.insert.return_value.execute.return_value = MagicMock(data=rows)

        payload = _base_payload(
            amount=total,
            n_installments=3,
            payment_method="CARTAO_CREDITO",
            card_id=FAKE_CARD_ID,
            account_id=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=payload).json()

        principal = Decimal(str(data["transaction"]["amount"]))
        children_sum = sum(Decimal(str(c["amount"])) for c in data["installment_children"])
        assert principal + children_sum == Decimal(str(total))


# ── §4.1 caminho feliz — rateio ───────────────────────────────────────────────

class TestTransacaoRateada:
    def test_categoria_e_rateado(self, client: TestClient):
        db, _ = _make_db()
        # Sobrescreve category no mock
        db.table("transactions").insert.return_value.execute.return_value = MagicMock(
            data=[{"id": FAKE_TX_ID, "date": TODAY, "amount": "100.00",
                   "type": "GASTO", "category": "Rateado", "notes": "Hipermercado",
                   "payment_method": "PIX", "account_id": FAKE_ACCOUNT_ID,
                   "card_id": None, "installment_id": None, "is_recurring": False, "status": "PAGO"}]
        )
        payload = _base_payload(
            amount=100.00,
            notes="Hipermercado",
            splits=[
                {"category": "Alimentação", "amount": 80.00},
                {"category": "Moradia",     "amount": 20.00},
            ],
            category=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=payload).json()
        assert data["transaction"]["category"] == "Rateado"

    def test_splits_tem_2_itens(self, client: TestClient):
        db, _ = _make_db()
        db.table("transactions").insert.return_value.execute.return_value = MagicMock(
            data=[{"id": FAKE_TX_ID, "date": TODAY, "amount": "100.00",
                   "type": "GASTO", "category": "Rateado", "notes": "Hipermercado",
                   "payment_method": "PIX", "account_id": FAKE_ACCOUNT_ID,
                   "card_id": None, "installment_id": None, "is_recurring": False, "status": "PAGO"}]
        )
        payload = _base_payload(
            amount=100.00,
            splits=[
                {"category": "Alimentação", "amount": 80.00},
                {"category": "Moradia",     "amount": 20.00},
            ],
            category=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=payload).json()
        assert len(data["splits"]) == 2


# ── §4.1 caminho feliz — parcelado + rateado ─────────────────────────────────

class TestParceladoMaisRateado:
    def test_10x_com_splits_tem_10_children_mais_principal(self, client: TestClient):
        n = 10
        db, _ = _make_db(n_tx_rows=n)
        # Sobrescreve: todas as parcelas com category=Rateado
        rows = [{"id": f"tx-{i}", "amount": "300.00", "installment_id": FAKE_INST_ID,
                 "date": TODAY, "type": "GASTO", "category": "Rateado",
                 "payment_method": "CARTAO_CREDITO", "card_id": FAKE_CARD_ID,
                 "account_id": None, "is_recurring": False, "status": "PENDENTE", "notes": ""}
                for i in range(n)]
        db.table("transactions").insert.return_value.execute.return_value = MagicMock(data=rows)

        payload = _base_payload(
            amount=3000.00,
            n_installments=n,
            payment_method="CARTAO_CREDITO",
            card_id=FAKE_CARD_ID,
            account_id=None,
            splits=[
                {"category": "Alimentação", "amount": 1000.00},
                {"category": "Moradia",     "amount": 2000.00},
            ],
            category=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            resp = client.post("/transactions", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["installment_children"]) == n - 1

    def test_splits_proporcionais_somam_ao_total(self, client: TestClient):
        """Soma de todos os splits de todas as parcelas = total da compra."""
        n = 10
        total = 3000.00
        db, _ = _make_db(n_tx_rows=n)
        rows = [{"id": f"tx-{i}", "amount": "300.00", "installment_id": FAKE_INST_ID,
                 "date": TODAY, "type": "GASTO", "category": "Rateado",
                 "payment_method": "CARTAO_CREDITO", "card_id": FAKE_CARD_ID,
                 "account_id": None, "is_recurring": False, "status": "PENDENTE", "notes": ""}
                for i in range(n)]
        db.table("transactions").insert.return_value.execute.return_value = MagicMock(data=rows)

        payload = _base_payload(
            amount=total,
            n_installments=n,
            payment_method="CARTAO_CREDITO",
            card_id=FAKE_CARD_ID,
            account_id=None,
            splits=[
                {"category": "Alimentação", "amount": 1000.00},
                {"category": "Moradia",     "amount": 2000.00},
            ],
            category=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=payload).json()

        all_transactions = [data["transaction"]] + data["installment_children"]
        total_splits = Decimal("0")
        for tx in all_transactions:
            for sp in tx.get("splits", []):
                total_splits += Decimal(str(sp["amount"]))

        assert total_splits == Decimal(str(total))


# ── §4.1 caminho feliz — saldo e memória ─────────────────────────────────────

class TestSaldoEMemoria:
    def test_pix_retorna_account_balance_atualizado(self, client: TestClient):
        db, registry = _make_db(account_balance="1000.00")
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=_base_payload(amount=150.00)).json()
        assert data["account_balance"] == pytest.approx(850.00, abs=0.01)

    def test_cartao_credito_retorna_account_balance_none(self, client: TestClient):
        db, _ = _make_db()
        payload = _base_payload(
            payment_method="CARTAO_CREDITO",
            card_id=FAKE_CARD_ID,
            account_id=None,
        )
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=payload).json()
        assert data["account_balance"] is None

    def test_confirmed_true_grava_memoria(self, client: TestClient):
        db, _ = _make_db()
        mem_repo = MagicMock()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository", return_value=mem_repo):
            client.post("/transactions", json=_base_payload(confirmed=True, notes="Uber"))
        mem_repo.remember.assert_called_once()

    def test_confirmed_false_nao_grava_memoria(self, client: TestClient):
        db, _ = _make_db()
        mem_repo = MagicMock()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository", return_value=mem_repo):
            client.post("/transactions", json=_base_payload(confirmed=False))
        mem_repo.remember.assert_not_called()

    def test_segunda_transacao_usa_memoria(self, client: TestClient):
        db, _ = _make_db()
        mem_suggestion = _fake_suggestion(source="memory", score=0.99)
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=mem_suggestion), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            data = client.post("/transactions", json=_base_payload(category=None, confirmed=False)).json()
        assert data["category_suggestion"]["source"] == "memory"


# ── §4.2 validações 422 ───────────────────────────────────────────────────────

class TestValidacoes422:
    def _post(self, client: TestClient, payload: dict) -> int:
        db, _ = _make_db()
        with patch("api.routers.transactions.get_client", return_value=db), \
             patch("api.routers.transactions.categorize_with_memory", return_value=_fake_suggestion()), \
             patch("api.routers.transactions.CategoryMemoryRepository"):
            return client.post("/transactions", json=payload).status_code

    def test_amount_zero_422(self, client: TestClient):
        assert self._post(client, _base_payload(amount=0)) == 422

    def test_amount_negativo_422(self, client: TestClient):
        assert self._post(client, _base_payload(amount=-50.00)) == 422

    def test_date_mais_90_dias_futuro_422(self, client: TestClient):
        future = (date.today() + timedelta(days=91)).isoformat()
        assert self._post(client, _base_payload(date=future)) == 422

    def test_parcelas_sem_card_id_422(self, client: TestClient):
        payload = _base_payload(n_installments=3, card_id=None, account_id=FAKE_ACCOUNT_ID)
        assert self._post(client, payload) == 422

    def test_splits_soma_diferente_do_amount_422(self, client: TestClient):
        payload = _base_payload(
            amount=100.00,
            splits=[
                {"category": "Alimentação", "amount": 60.00},
                {"category": "Moradia",     "amount": 60.00},  # soma 120 ≠ 100
            ],
        )
        assert self._post(client, payload) == 422

    def test_card_id_com_metodo_nao_credito_422(self, client: TestClient):
        payload = _base_payload(
            card_id=FAKE_CARD_ID,
            payment_method="PIX",
        )
        assert self._post(client, payload) == 422

    def test_sem_account_id_e_sem_card_id_422(self, client: TestClient):
        payload = _base_payload(account_id=None, card_id=None)
        assert self._post(client, payload) == 422
