from __future__ import annotations

from datetime import date
from time import perf_counter

import pytest

from core.credit_card_billing import (
    due_date_for_purchase,
    invoice_by_due_month,
    invoice_for_closing,
)
from core.debt import DebtRisk, classify_debt_burden, estimate_cet
from core.liquidity import LiquidityBucket, calculate_emergency_reserve, classify_liquidity
from models.credit_card import CreditCard
from models.investment import Investment, InvestmentType
from models.transaction import Category, PaymentMethod, Transaction, TransactionType


def _card_tx(day: date, amount: float, card_id: str = "card-001") -> Transaction:
    return Transaction(
        date=day,
        amount=amount,
        type=TransactionType.GASTO,
        category=Category.OUTROS,
        payment_method=PaymentMethod.CARTAO_CREDITO,
        card_id=card_id,
    )


def _investment(
    value: float,
    liquidity_days: int,
    inv_type: InvestmentType = InvestmentType.RF,
) -> Investment:
    return Investment(
        ticker=f"ATIVO{value:.0f}{liquidity_days}",
        type=inv_type,
        quantity=1,
        avg_price=value,
        current_price=value,
        liquidity_days=liquidity_days,
    )


class TestCreditCardBillingBrasil:
    def test_compra_apos_fechamento_vai_para_proxima_fatura(self):
        card = CreditCard(id="card-001", name="Principal", closing_day=15, due_day=22)
        txs = [
            _card_tx(date(2026, 5, 14), 100),
            _card_tx(date(2026, 5, 16), 200),
            _card_tx(date(2026, 6, 15), 300),
        ]

        maio = invoice_for_closing(card, txs, 2026, 5)
        junho = invoice_for_closing(card, txs, 2026, 6)

        assert maio.period_start == date(2026, 4, 16)
        assert maio.period_end == date(2026, 5, 15)
        assert maio.due_date == date(2026, 5, 22)
        assert maio.total == pytest.approx(100)
        assert junho.total == pytest.approx(500)

    def test_vencimento_menor_que_fechamento_cai_no_mes_seguinte(self):
        card = CreditCard(id="card-001", name="Principal", closing_day=25, due_day=10)
        tx = _card_tx(date(2026, 5, 24), 150)

        assert due_date_for_purchase(card, tx.date) == date(2026, 6, 10)
        assert invoice_by_due_month(card, [tx], 2026, 6).total == pytest.approx(150)
        assert card.fatura_por_vencimento([tx], 2026, 6) == pytest.approx(150)

    def test_ignora_pix_e_outros_cartoes_na_fatura(self):
        card = CreditCard(id="card-001", name="Principal", closing_day=15, due_day=22)
        txs = [
            _card_tx(date(2026, 5, 10), 100, card_id="card-001"),
            _card_tx(date(2026, 5, 10), 999, card_id="card-002"),
            Transaction(
                date=date(2026, 5, 10),
                amount=888,
                type=TransactionType.GASTO,
                category=Category.OUTROS,
                payment_method=PaymentMethod.PIX,
                card_id="card-001",
            ),
        ]

        assert invoice_for_closing(card, txs, 2026, 5).total == pytest.approx(100)


class TestDebtBrasil:
    def test_estima_cet_de_parcelamento_com_juros(self):
        summary = estimate_cet(principal=1000, installment_amount=110, n_installments=10)

        assert summary.total_paid == pytest.approx(1100)
        assert summary.total_interest_and_fees == pytest.approx(100)
        assert 1.6 < summary.monthly_cet_pct < 1.9
        assert summary.annual_cet_pct > 20

    def test_classifica_comprometimento_de_renda(self):
        assert classify_debt_burden(500, 5000) == DebtRisk.BAIXO
        assert classify_debt_burden(1000, 5000) == DebtRisk.ATENCAO
        assert classify_debt_burden(1750, 5000) == DebtRisk.ALTO
        assert classify_debt_burden(2500, 5000) == DebtRisk.CRITICO


class TestLiquidityBrasil:
    def test_classifica_reserva_por_prazo_de_resgate(self):
        caixa = _investment(5000, 0, InvestmentType.CAIXA)
        cdb_d30 = _investment(3000, 30)
        previdencia = _investment(10000, 120)

        assert classify_liquidity(caixa) == LiquidityBucket.IMEDIATA
        assert classify_liquidity(cdb_d30) == LiquidityBucket.CURTA
        assert classify_liquidity(previdencia) == LiquidityBucket.TRAVADA

        reserve = calculate_emergency_reserve([caixa, cdb_d30, previdencia], monthly_expenses=2000)
        assert reserve.immediate == pytest.approx(5000)
        assert reserve.short_term == pytest.approx(3000)
        assert reserve.locked == pytest.approx(10000)
        assert reserve.coverage_months == pytest.approx(4.0)
        assert reserve.status == "ATENCAO"


class TestBrazilianFinancePerformance:
    def test_fatura_cartao_performance_stress(self):
        card = CreditCard(id="card-001", name="Principal", closing_day=15, due_day=22)
        txs = [
            _card_tx(
                date(2026, (i % 12) + 1, (i % 28) + 1),
                amount=float((i % 300) + 1),
            )
            for i in range(100_000)
        ]

        start = perf_counter()
        invoices = [invoice_for_closing(card, txs, 2026, month) for month in range(1, 13)]
        elapsed = perf_counter() - start

        assert sum(invoice.count for invoice in invoices) > 0
        assert elapsed < 1.75

    def test_cet_performance_stress(self):
        start = perf_counter()
        summaries = [
            estimate_cet(
                principal=1000 + i,
                installment_amount=(1000 + i) / 10 + 12,
                n_installments=10,
            )
            for i in range(10_000)
        ]
        elapsed = perf_counter() - start

        assert len(summaries) == 10_000
        assert summaries[-1].annual_cet_pct > 0
        assert elapsed < 2.5

    def test_reserva_liquidez_performance_stress(self):
        investments = [
            _investment(
                value=float((i % 1_000) + 100),
                liquidity_days=[0, 1, 30, 90][i % 4],
                inv_type=InvestmentType.CAIXA if i % 4 == 0 else InvestmentType.RF,
            )
            for i in range(50_000)
        ]

        start = perf_counter()
        reserve = calculate_emergency_reserve(investments, monthly_expenses=5000)
        elapsed = perf_counter() - start

        assert reserve.eligible_total > 0
        assert reserve.locked > 0
        assert elapsed < 0.35
