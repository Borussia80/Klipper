from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

from models.transaction import Category, Transaction, TransactionType, PaymentMethod, TransactionStatus
from models.investment import Investment, InvestmentType
from models.bank_account import BankAccount, AccountType
from models.credit_card import CreditCard
from models.installment import Installment
from models.budget import Budget

_FIXED_DATE = date(2026, 5, 15)
_FUTURE_DATE = date(2030, 6, 1)    # para transações pendentes / parcelas futuras
_PAST_START  = date(2026, 1, 1)    # start_date de parcelamentos já iniciados


class TestTransaction:
    def test_cria_transacao_valida(self):
        tx = Transaction(
            date=_FIXED_DATE,
            amount=100.0,
            type=TransactionType.GASTO,
            category=Category.ALIMENTACAO,
        )
        assert tx.amount == 100.0

    def test_valor_zero_invalido(self):
        with pytest.raises(ValueError, match="positivo"):
            Transaction(
                date=_FIXED_DATE, amount=0, type=TransactionType.GANHO, category=Category.RENDA
            )

    def test_valor_negativo_invalido(self):
        with pytest.raises(ValueError):
            Transaction(
                date=_FIXED_DATE, amount=-50, type=TransactionType.GASTO, category=Category.OUTROS
            )

    def test_data_futura_permitida_status_pendente(self):
        """Future dates are valid with status PENDENTE (installments need this)."""
        tx = Transaction(
            date=_FUTURE_DATE,
            amount=100,
            type=TransactionType.GASTO,
            category=Category.OUTROS,
            status=TransactionStatus.PENDENTE,
        )
        assert tx.status == TransactionStatus.PENDENTE

    def test_arredondamento_automatico(self):
        tx = Transaction(
            date=_FIXED_DATE, amount=100.999, type=TransactionType.GASTO, category=Category.OUTROS
        )
        assert tx.amount == 101.0

    def test_payment_method_default_pix(self):
        tx = Transaction(
            date=_FIXED_DATE, amount=50.0, type=TransactionType.GASTO, category=Category.LAZER
        )
        assert tx.payment_method == PaymentMethod.PIX

    def test_status_default_pago(self):
        tx = Transaction(
            date=_FIXED_DATE, amount=50.0, type=TransactionType.GASTO, category=Category.LAZER
        )
        assert tx.status == TransactionStatus.PAGO

    def test_cartao_credito_aceita_card_id(self):
        tx = Transaction(
            date=_FIXED_DATE, amount=200.0,
            type=TransactionType.GASTO, category=Category.LAZER,
            payment_method=PaymentMethod.CARTAO_CREDITO,
            card_id="some-uuid",
        )
        assert tx.card_id == "some-uuid"


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


class TestBankAccount:
    def test_cria_conta_valida(self):
        acc = BankAccount(name="Nubank", bank="Nu Pagamentos", type=AccountType.CORRENTE, balance=1000.0)
        assert acc.name == "Nubank"
        assert acc.balance == 1000.0

    def test_nome_vazio_invalido(self):
        with pytest.raises(ValueError, match="vazio"):
            BankAccount(name="  ", bank="X")

    def test_saldo_arredondado(self):
        acc = BankAccount(name="Conta", balance=100.555)
        assert acc.balance == Decimal("100.56")

    def test_tipo_default_corrente(self):
        acc = BankAccount(name="Conta")
        assert acc.type == AccountType.CORRENTE


class TestCreditCard:
    def test_cria_cartao_valido(self):
        card = CreditCard(name="Nubank", bank="Nu", limit_total=5000.0, closing_day=15, due_day=22)
        assert card.limit_total == 5000.0

    def test_nome_vazio_invalido(self):
        with pytest.raises(ValueError, match="vazio"):
            CreditCard(name="")

    def test_dia_fechamento_invalido(self):
        with pytest.raises(ValueError):
            CreditCard(name="X", closing_day=32)

    def test_limite_negativo_invalido(self):
        with pytest.raises(ValueError, match="negativo"):
            CreditCard(name="X", limit_total=-100)

    def test_limit_used_sem_transacoes(self):
        card = CreditCard(name="X", limit_total=1000.0)
        assert card.limit_used([]) == 0.0

    def test_limit_available(self):
        card = CreditCard(name="X", limit_total=1000.0)
        assert card.limit_available([]) == 1000.0


class TestInstallment:
    def _make(self, **kwargs) -> Installment:
        defaults = dict(
            description="Notebook 12x",
            total_amount=2400.0,
            n_total=12,
            start_date=_PAST_START,
        )
        defaults.update(kwargs)
        return Installment(**defaults)

    def test_cria_parcelamento_valido(self):
        inst = self._make()
        assert inst.n_total == 12
        assert inst.installment_amount == Decimal("200")

    def test_valor_negativo_invalido(self):
        with pytest.raises(ValueError, match="positivo"):
            self._make(total_amount=-100)

    def test_n_total_zero_invalido(self):
        with pytest.raises(ValueError):
            self._make(n_total=0)

    def test_descricao_vazia_invalida(self):
        with pytest.raises(ValueError, match="vazia"):
            self._make(description="   ")

    def test_n_remaining(self):
        inst = self._make(n_paid=3)
        assert inst.n_remaining == 9

    def test_total_remaining(self):
        inst = self._make(total_amount=1200.0, n_total=12, n_paid=4)
        assert inst.total_remaining == Decimal("800")

    def test_total_remaining_preserva_centavos(self):
        inst = self._make(total_amount=100.0, n_total=3, n_paid=2)
        assert inst.total_remaining == Decimal("33.34")

    def test_n_paid_nao_pode_exceder_n_total(self):
        with pytest.raises(ValueError):
            self._make(total_amount=100.0, n_total=3, n_paid=4)

    def test_installment_amount_calculado(self):
        inst = self._make(total_amount=1200.0, n_total=4)
        assert inst.installment_amount == Decimal("300")


class TestBudget:
    def test_cria_budget_valido(self):
        b = Budget(category="Alimentação", monthly_limit=1000.0, year=2026, month=5)
        assert b.monthly_limit == 1000.0

    def test_limite_negativo_invalido(self):
        with pytest.raises(ValueError, match="positivo"):
            Budget(category="X", monthly_limit=-100, year=2026, month=5)

    def test_mes_invalido(self):
        with pytest.raises(ValueError, match="Mês"):
            Budget(category="X", monthly_limit=100, year=2026, month=13)
