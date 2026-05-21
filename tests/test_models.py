from __future__ import annotations

import pytest
from datetime import date, timedelta

from models.transaction import Category, Transaction, TransactionType
from models.investment import Investment, InvestmentType


class TestTransaction:
    def test_cria_transacao_valida(self):
        tx = Transaction(
            date=date.today(),
            amount=100.0,
            type=TransactionType.GASTO,
            category=Category.ALIMENTACAO,
        )
        assert tx.amount == 100.0

    def test_valor_zero_invalido(self):
        with pytest.raises(ValueError, match="positivo"):
            Transaction(
                date=date.today(), amount=0, type=TransactionType.GANHO, category=Category.RENDA
            )

    def test_valor_negativo_invalido(self):
        with pytest.raises(ValueError):
            Transaction(
                date=date.today(), amount=-50, type=TransactionType.GASTO, category=Category.OUTROS
            )

    def test_data_futura_invalida(self):
        with pytest.raises(ValueError, match="futura"):
            Transaction(
                date=date.today() + timedelta(days=1),
                amount=100,
                type=TransactionType.GASTO,
                category=Category.OUTROS,
            )

    def test_arredondamento_automatico(self):
        tx = Transaction(
            date=date.today(), amount=100.999, type=TransactionType.GASTO, category=Category.OUTROS
        )
        assert tx.amount == 101.0


class TestInvestment:
    def _make(self, **kwargs) -> Investment:
        defaults = dict(
            ticker="MXRF11",
            type=InvestmentType.FII,
            quantity=100,
            avg_price=10.0,
            current_price=10.5,
        )
        defaults.update(kwargs)
        return Investment(**defaults)

    def test_cria_investimento_valido(self):
        inv = self._make()
        assert inv.ticker == "MXRF11"

    def test_ticker_uppercase(self):
        inv = self._make(ticker="mxrf11")
        assert inv.ticker == "MXRF11"

    def test_quantidade_zero_invalida(self):
        with pytest.raises(ValueError):
            self._make(quantity=0)

    def test_fragility_fora_de_range(self):
        with pytest.raises(ValueError, match="Fragility"):
            self._make(fragility_score=1.5)

    def test_current_value(self):
        inv = self._make(quantity=100, current_price=10.5)
        assert inv.current_value == 1050.0

    def test_gain_loss(self):
        inv = self._make(quantity=100, avg_price=10.0, current_price=11.0)
        assert inv.gain_loss == 100.0

    def test_gain_loss_pct(self):
        inv = self._make(quantity=100, avg_price=10.0, current_price=11.0)
        assert inv.gain_loss_pct == pytest.approx(10.0)
