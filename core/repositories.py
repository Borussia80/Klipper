from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Any

from models.transaction import Category, Transaction, TransactionType, PaymentMethod, TransactionStatus
from models.investment import Investment
from models.decision import DecisionRecord
from models.bank_account import BankAccount, AccountType
from models.credit_card import CreditCard
from models.installment import Installment
from models.budget import Budget

from .categorizer import categorize, normalize, CategoryGuess
from .database import get_client

log = logging.getLogger(__name__)


def tx_balance_delta(amount: float, tx_type: TransactionType) -> float:
    """Signed balance change a transaction causes: GASTO → negative, GANHO → positive."""
    return -amount if tx_type == TransactionType.GASTO else amount


def _to_db(data: dict) -> dict:
    """Converte Decimal → str para serialização JSON do cliente Supabase."""
    return {k: str(v) if isinstance(v, Decimal) else v for k, v in data.items()}


class TransactionRepository:
    TABLE = "transactions"

    def create(self, tx: Transaction) -> Transaction:
        data = _to_db(tx.model_dump())
        data["date"] = data["date"].isoformat()
        data["type"] = data["type"].value
        data["category"] = data["category"].value
        data["payment_method"] = data["payment_method"].value
        data["status"] = data["status"].value
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar transação %s: %s", tx.id, e)
            raise
        return tx

    def list_by_month(self, year: int, month: int) -> list[Transaction]:
        start = date(year, month, 1).isoformat()
        end = date(year + 1, 1, 1).isoformat() if month == 12 else date(year, month + 1, 1).isoformat()
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .gte("date", start)
                .lt("date", end)
                .order("date", desc=True)
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar transações %d/%d: %s", month, year, e)
            raise
        return [self._from_row(r) for r in res.data]

    def list_by_category(self, category: Category, year: int, month: int) -> list[Transaction]:
        return [t for t in self.list_by_month(year, month) if t.category == category]

    def list_by_card(self, card_id: str, year: int, month: int) -> list[Transaction]:
        return [t for t in self.list_by_month(year, month) if t.card_id == card_id]

    def list_by_account(self, account_id: str, year: int, month: int) -> list[Transaction]:
        return [t for t in self.list_by_month(year, month) if t.account_id == account_id]

    def list_pending_by_installment(self, installment_id: str) -> list[Transaction]:
        """Returns PENDENTE/AGENDADO transactions for a given installment, ordered by date."""
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("installment_id", installment_id)
                .in_("status", ["PENDENTE", "AGENDADO"])
                .order("date")
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar pendentes do parcelamento %s: %s", installment_id, e)
            raise
        return [self._from_row(r) for r in res.data]

    def list_pending(self) -> list[Transaction]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .in_("status", ["PENDENTE", "AGENDADO"])
                .order("date")
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar pendentes: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def update(self, tx: Transaction) -> Transaction:
        data = _to_db(tx.model_dump())
        data["date"] = data["date"].isoformat()
        data["type"] = data["type"].value
        data["category"] = data["category"].value
        data["payment_method"] = data["payment_method"].value
        data["status"] = data["status"].value
        try:
            get_client().table(self.TABLE).update(data).eq("id", tx.id).execute()
        except Exception as e:
            log.error("Erro ao atualizar transação %s: %s", tx.id, e)
            raise
        return tx

    def delete(self, transaction_id: str) -> None:
        try:
            get_client().table(self.TABLE).delete().eq("id", transaction_id).execute()
        except Exception as e:
            log.error("Erro ao deletar transação %s: %s", transaction_id, e)
            raise

    @staticmethod
    def _from_row(row: dict[str, Any]) -> Transaction:
        return Transaction(
            **{
                **row,
                "type": TransactionType(row["type"]),
                "category": Category(row["category"]),
                "payment_method": PaymentMethod(row.get("payment_method", "PIX")),
                "status": TransactionStatus(row.get("status", "PAGO")),
            }
        )


class InvestmentRepository:
    TABLE = "investments"

    def upsert(self, inv: Investment) -> Investment:
        data = _to_db(inv.model_dump())
        data["type"] = data["type"].value
        try:
            get_client().table(self.TABLE).upsert(data, on_conflict="ticker").execute()
        except Exception as e:
            log.error("Erro ao upsert investimento %s: %s", inv.ticker, e)
            raise
        return inv

    def get_portfolio(self) -> list[Investment]:
        try:
            res = get_client().table(self.TABLE).select("*").order("ticker").execute()
        except Exception as e:
            log.error("Erro ao carregar portfólio: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def get_by_ticker(self, ticker: str) -> Investment | None:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("ticker", ticker.upper())
                .execute()
            )
        except Exception as e:
            log.error("Erro ao buscar ativo %s: %s", ticker, e)
            raise
        return self._from_row(res.data[0]) if res.data else None

    def delete(self, ticker: str) -> None:
        try:
            get_client().table(self.TABLE).delete().eq("ticker", ticker.upper()).execute()
        except Exception as e:
            log.error("Erro ao deletar ativo %s: %s", ticker, e)
            raise

    @staticmethod
    def _from_row(row: dict[str, Any]) -> Investment:
        from models.investment import InvestmentType
        return Investment(**{**row, "type": InvestmentType(row["type"])})


class DecisionRepository:
    TABLE = "decisions"

    def create(self, rec: DecisionRecord) -> DecisionRecord:
        data = _to_db(rec.model_dump())
        data["date"] = data["date"].isoformat()
        if data["outcome"]:
            data["outcome"] = data["outcome"].value
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar decision record %s: %s", rec.id, e)
            raise
        return rec

    def update(self, rec: DecisionRecord) -> DecisionRecord:
        data = _to_db(rec.model_dump())
        data["date"] = data["date"].isoformat()
        if data["outcome"]:
            data["outcome"] = data["outcome"].value
        try:
            get_client().table(self.TABLE).update(data).eq("id", rec.id).execute()
        except Exception as e:
            log.error("Erro ao atualizar decision record %s: %s", rec.id, e)
            raise
        return rec

    def list_by_ticker(self, ticker: str) -> list[DecisionRecord]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("ticker", ticker.upper())
                .order("date", desc=True)
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar decisions para %s: %s", ticker, e)
            raise
        return [self._from_row(r) for r in res.data]

    def list_all(self) -> list[DecisionRecord]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .order("date", desc=True)
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar todos os decisions: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    @staticmethod
    def _from_row(row: dict[str, Any]) -> DecisionRecord:
        from models.decision import DecisionOutcome
        outcome = DecisionOutcome(row["outcome"]) if row.get("outcome") else None
        return DecisionRecord(**{**row, "outcome": outcome})


class BankAccountRepository:
    TABLE = "bank_accounts"

    def create(self, account: BankAccount) -> BankAccount:
        data = _to_db(account.model_dump())
        data["type"] = data["type"].value
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar conta %s: %s", account.id, e)
            raise
        return account

    def list_active(self) -> list[BankAccount]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("is_active", True)
                .order("name")
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar contas: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def get_by_id(self, account_id: str) -> BankAccount | None:
        try:
            res = get_client().table(self.TABLE).select("*").eq("id", account_id).execute()
        except Exception as e:
            log.error("Erro ao buscar conta %s: %s", account_id, e)
            raise
        return self._from_row(res.data[0]) if res.data else None

    def update_balance(self, account_id: str, balance: float) -> None:
        try:
            get_client().table(self.TABLE).update({"balance": round(balance, 2)}).eq("id", account_id).execute()
        except Exception as e:
            log.error("Erro ao atualizar saldo %s: %s", account_id, e)
            raise

    def adjust_balance(self, account_id: str, delta: float) -> None:
        """Applies a signed delta to the account balance (negative = debit, positive = credit)."""
        account = self.get_by_id(account_id)
        if account is None:
            raise ValueError(f"Conta {account_id} não encontrada.")
        self.update_balance(account_id, float(account.balance) + delta)

    def delete(self, account_id: str) -> None:
        try:
            get_client().table(self.TABLE).update({"is_active": False}).eq("id", account_id).execute()
        except Exception as e:
            log.error("Erro ao desativar conta %s: %s", account_id, e)
            raise

    @staticmethod
    def _from_row(row: dict[str, Any]) -> BankAccount:
        data = {k: v for k, v in row.items() if k != "created_at"}
        return BankAccount(**{**data, "type": AccountType(data["type"])})


class CreditCardRepository:
    TABLE = "credit_cards"

    def create(self, card: CreditCard) -> CreditCard:
        data = _to_db(card.model_dump())
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar cartão %s: %s", card.id, e)
            raise
        return card

    def list_active(self) -> list[CreditCard]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("is_active", True)
                .order("name")
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar cartões: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def get_by_id(self, card_id: str) -> CreditCard | None:
        try:
            res = get_client().table(self.TABLE).select("*").eq("id", card_id).execute()
        except Exception as e:
            log.error("Erro ao buscar cartão %s: %s", card_id, e)
            raise
        return self._from_row(res.data[0]) if res.data else None

    def delete(self, card_id: str) -> None:
        try:
            get_client().table(self.TABLE).update({"is_active": False}).eq("id", card_id).execute()
        except Exception as e:
            log.error("Erro ao desativar cartão %s: %s", card_id, e)
            raise

    @staticmethod
    def _from_row(row: dict[str, Any]) -> CreditCard:
        return CreditCard(**{k: v for k, v in row.items() if k != "created_at"})


class InstallmentRepository:
    TABLE = "installments"

    def create(self, inst: Installment) -> Installment:
        data = _to_db(inst.model_dump())
        data["start_date"] = data["start_date"].isoformat()
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar parcelamento %s: %s", inst.id, e)
            raise
        return inst

    def list_active(self) -> list[Installment]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("is_active", True)
                .order("start_date", desc=True)
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar parcelamentos: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def mark_paid(self, installment_id: str) -> None:
        try:
            res = get_client().table(self.TABLE).select("n_paid,n_total").eq("id", installment_id).execute()
            if not res.data:
                return
            row = res.data[0]
            new_paid = min(row["n_paid"] + 1, row["n_total"])
            is_done = new_paid >= row["n_total"]
            get_client().table(self.TABLE).update({
                "n_paid": new_paid,
                "is_active": not is_done,
            }).eq("id", installment_id).execute()
        except Exception as e:
            log.error("Erro ao marcar parcela paga %s: %s", installment_id, e)
            raise

    @staticmethod
    def _from_row(row: dict[str, Any]) -> Installment:
        from datetime import date as Date
        data = {k: v for k, v in row.items() if k != "created_at"}
        if isinstance(data.get("start_date"), str):
            data["start_date"] = Date.fromisoformat(data["start_date"])
        return Installment(**data)


class BudgetRepository:
    TABLE = "budgets"

    def upsert(self, budget: Budget) -> Budget:
        data = _to_db(budget.model_dump())
        try:
            get_client().table(self.TABLE).upsert(
                data, on_conflict="category,year,month"
            ).execute()
        except Exception as e:
            log.error("Erro ao upsert budget %s: %s", budget.category, e)
            raise
        return budget

    def list_by_month(self, year: int, month: int) -> list[Budget]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("year", year)
                .eq("month", month)
                .order("category")
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar budgets %d/%d: %s", month, year, e)
            raise
        return [self._from_row(r) for r in res.data]

    def get_by_category_month(self, category: str, year: int, month: int) -> Budget | None:
        budgets = self.list_by_month(year, month)
        return next((b for b in budgets if b.category == category), None)

    def delete(self, budget_id: str) -> None:
        try:
            get_client().table(self.TABLE).delete().eq("id", budget_id).execute()
        except Exception as e:
            log.error("Erro ao deletar budget %s: %s", budget_id, e)
            raise

    @staticmethod
    def _from_row(row: dict[str, Any]) -> Budget:
        return Budget(**{k: v for k, v in row.items() if k != "created_at"})


class CategoryMemoryRepository:
    """Persiste e recupera a memória de categorização do usuário.

    É a camada 1 do core.categorizer: rótulos que o usuário confirmou, com
    precedência sobre as regras genéricas. Dedup por `pattern` (estabelecimento
    normalizado) — uma linha por estabelecimento, não por transação.
    """

    TABLE = "category_memory"

    def remember(self, description: str, category: Category, user_id: str) -> None:
        """Grava (ou reforça) que `description` pertence a `category`, para `user_id`.

        Chamar quando o usuário CONFIRMA/CORRIGE uma categoria — nunca para
        palpites automáticos, ou o sistema reforçaria os próprios erros.

        `user_id` é OBRIGATÓRIO: o cliente roda com service_role (RLS bypassada,
        `auth.uid()`=NULL), então toda query é escopada explicitamente por usuário
        e o INSERT grava `user_id` (sem ele, violaria `NOT NULL`). Ver
        docs/security/multi_tenant_audit.md §4.1.
        """
        if not user_id:
            raise ValueError("user_id é obrigatório em CategoryMemoryRepository.remember")
        pattern = normalize(description)
        if not pattern:
            return
        # Read-modify-write (não atômico) em vez de upsert: precisamos INCREMENTAR
        # `hits`, o que o upsert do PostgREST não faz. Escopo por (user_id, pattern)
        # — a corrida concorrente por usuário é desprezível. Se virar escrita intensa,
        # trocar por uma função RPC com `hits = hits + 1` atômico.
        try:
            client = get_client()
            existing = (
                client.table(self.TABLE)
                .select("id, hits")
                .eq("user_id", user_id)
                .eq("pattern", pattern)
                .limit(1)
                .execute()
            )
            if existing.data:
                row = existing.data[0]
                client.table(self.TABLE).update(
                    {"category": category.value, "hits": row["hits"] + 1}
                ).eq("id", row["id"]).eq("user_id", user_id).execute()
            else:
                client.table(self.TABLE).insert(
                    {"pattern": pattern, "category": category.value, "user_id": user_id}
                ).execute()
        except Exception as e:
            # Memória é best-effort: nunca derruba o fluxo de salvar a transação.
            log.error("Erro ao gravar memória de categoria '%s': %s", pattern, e)

    def load_history(self, user_id: str) -> list[tuple[str, Category]]:
        """Pares (pattern, category) do `user_id`, para alimentar o categorizador.

        Ordenado por `hits` desc — estabelecimentos mais confirmados primeiro.
        `user_id` obrigatório (service_role bypassa RLS; filtro explícito evita
        vazar memória entre usuários).
        """
        if not user_id:
            raise ValueError("user_id é obrigatório em CategoryMemoryRepository.load_history")
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("pattern, category")
                .eq("user_id", user_id)
                .order("hits", desc=True)
                .execute()
            )
            return [(r["pattern"], Category(r["category"])) for r in res.data]
        except Exception as e:
            log.error("Erro ao carregar memória de categoria: %s", e)
            return []


def categorize_with_memory(description: str, user_id: str) -> CategoryGuess:
    """Categoriza consultando a memória do `user_id` + regras + fuzzy.

    Atalho para uso pontual (ex.: entrada rápida). Em importação de lote, carregue
    a memória UMA vez com CategoryMemoryRepository().load_history(user_id) e passe
    para core.categorizer.categorize(desc, history=...) por linha — evita N round-trips.
    """
    history = CategoryMemoryRepository().load_history(user_id)
    return categorize(description, history)


def confirm_transaction(tx: Transaction, user_id: str, learn: bool = True) -> Transaction:
    """Persiste uma transação CONFIRMADA pelo usuário e ensina a memória do `user_id`.

    Seam de caso-de-uso: `TransactionRepository.create` continua só persistindo
    (SOLID-S); o aprendizado é composto aqui. Use nas telas de entrada manual e
    de correção de categoria — `learn=False` no import automático, para não
    reforçar palpites do próprio algoritmo.
    """
    saved = TransactionRepository().create(tx)
    if learn and tx.notes:
        CategoryMemoryRepository().remember(tx.notes, tx.category, user_id)
    return saved
