from __future__ import annotations

import logging
from datetime import date
from typing import Any

from models.transaction import Category, Transaction, TransactionType
from models.investment import Investment
from models.decision import DecisionRecord

from .database import get_client

log = logging.getLogger(__name__)


class TransactionRepository:
    TABLE = "transactions"

    def create(self, tx: Transaction) -> Transaction:
        data = tx.model_dump()
        data["date"] = data["date"].isoformat()
        data["type"] = data["type"].value
        data["category"] = data["category"].value
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar transação %s: %s", tx.id, e)
            raise
        return tx

    def list_by_month(self, year: int, month: int) -> list[Transaction]:
        start = date(year, month, 1).isoformat()
        # Last day of month
        if month == 12:
            end = date(year + 1, 1, 1).isoformat()
        else:
            end = date(year, month + 1, 1).isoformat()
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
        txs = self.list_by_month(year, month)
        return [t for t in txs if t.category == category]

    def delete(self, transaction_id: str) -> None:
        try:
            get_client().table(self.TABLE).delete().eq("id", transaction_id).execute()
        except Exception as e:
            log.error("Erro ao deletar transação %s: %s", transaction_id, e)
            raise

    @staticmethod
    def _from_row(row: dict[str, Any]) -> Transaction:
        row["type"] = TransactionType(row["type"])
        row["category"] = Category(row["category"])
        return Transaction(**row)


class InvestmentRepository:
    TABLE = "investments"

    def upsert(self, inv: Investment) -> Investment:
        data = inv.model_dump()
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
        row["type"] = InvestmentType(row["type"])
        return Investment(**row)


class DecisionRepository:
    TABLE = "decisions"

    def create(self, rec: DecisionRecord) -> DecisionRecord:
        data = rec.model_dump()
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
        data = rec.model_dump()
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
        if row.get("outcome"):
            row["outcome"] = DecisionOutcome(row["outcome"])
        return DecisionRecord(**row)
