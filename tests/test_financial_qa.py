from __future__ import annotations

from datetime import date
from time import perf_counter

import pytest

from core.analytics import calcular_saldo_mensal, calcular_top_categorias
from core.behavioral import calcular_uso_orcamento
from core.installment_engine import gerar_parcelas
from models.budget import Budget
from models.credit_card import CreditCard
from models.installment import Installment
from models.transaction import Category, PaymentMethod, Transaction, TransactionType


def _tx(
    amount: float,
    tipo: TransactionType,
    category: Category,
    tx_date: date,
    card_id: str | None = None,
) -> Transaction:
    return Transaction(
        date=tx_date,
        amount=amount,
        type=tipo,
        category=category,
        card_id=card_id,
        payment_method=PaymentMethod.CARTAO_CREDITO if card_id else PaymentMethod.PIX,
    )


def test_sinergia_parcelamento_cartao_orcamento_e_saldo_mensal():
    card = CreditCard(id="card-br-001", name="Cartao Principal", limit_total=1000)
    inst = Installment(
        description="Compra parcelada",
        total_amount=100.0,
        n_total=3,
        start_date=date(2026, 5, 10),
        card_id=card.id,
        category=Category.ALIMENTACAO.value,
    )

    parcelas = gerar_parcelas(inst)
    maio = [p for p in parcelas if p.date.year == 2026 and p.date.month == 5]
    budgets = [Budget(category=Category.ALIMENTACAO.value, monthly_limit=50, year=2026, month=5)]

    saldo = calcular_saldo_mensal(
        [_tx(5000, TransactionType.GANHO, Category.RENDA, date(2026, 5, 1)), *parcelas],
        2026,
        5,
    )
    uso_orcamento = calcular_uso_orcamento(maio, budgets)[0]

    assert sum(p.amount for p in parcelas) == pytest.approx(inst.total_amount)
    assert all(p.payment_method == PaymentMethod.CARTAO_CREDITO for p in parcelas)
    assert card.fatura_atual(maio) == pytest.approx(33.33)
    assert uso_orcamento.gasto == pytest.approx(33.33)
    assert saldo.total_gastos == pytest.approx(33.33)
    assert saldo.saldo == pytest.approx(4966.67)


def test_analytics_performance_com_volume_de_transacoes():
    txs = [
        _tx(
            amount=float((i % 250) + 1),
            tipo=TransactionType.GANHO if i % 5 == 0 else TransactionType.GASTO,
            category=list(Category)[i % len(Category)],
            tx_date=date(2026, 5 if i % 2 == 0 else 4, (i % 28) + 1),
        )
        for i in range(25_000)
    ]

    start = perf_counter()
    saldo = calcular_saldo_mensal(txs, 2026, 5)
    top = calcular_top_categorias(txs, n=5)
    elapsed = perf_counter() - start

    assert saldo.total_ganhos > 0
    assert len(top) == 5
    assert elapsed < 0.35


def test_installment_engine_performance_com_carteira_grande():
    installments = [
        Installment(
            description=f"Contrato {i}",
            total_amount=1000 + i,
            n_total=12,
            start_date=date(2026, 1, 10),
            card_id=f"card-{i % 10}",
        )
        for i in range(1_000)
    ]

    start = perf_counter()
    parcelas = [p for inst in installments for p in gerar_parcelas(inst)]
    elapsed = perf_counter() - start

    assert len(parcelas) == 12_000
    assert elapsed < 1.25
