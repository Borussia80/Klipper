from __future__ import annotations

import pytest
from datetime import date

from models.transaction import Transaction, TransactionType, Category
from models.budget import Budget
from models.installment import Installment
from core.behavioral import (
    calcular_score_financeiro, detectar_alertas_padrao,
    calcular_uso_orcamento, OrcamentoStatus,
)

_FIXED_DATE = date(2026, 5, 15)
_FUTURE_START = date(2030, 1, 1)   # start_date de parcelas: sempre no futuro


def _gasto(categoria: str, valor: float) -> Transaction:
    return Transaction(
        date=_FIXED_DATE,
        amount=valor,
        type=TransactionType.GASTO,
        category=Category(categoria),
    )


def _ganho(valor: float) -> Transaction:
    return Transaction(
        date=_FIXED_DATE, amount=valor,
        type=TransactionType.GANHO, category=Category.RENDA,
    )


def _budget(categoria: str, limite: float) -> Budget:
    return Budget(category=categoria, monthly_limit=limite, year=2026, month=5)


def _installment(n_total: int = 12, n_paid: int = 0) -> Installment:
    return Installment(
        description="Test", total_amount=1200.0,
        n_total=n_total, n_paid=n_paid, start_date=_FUTURE_START,
    )


class TestCalcularScoreFinanceiro:
    def test_score_100_todos_criterios_ok(self):
        txs = [_ganho(5000), _gasto("Alimentação", 500)]
        budgets = [_budget("Alimentação", 1000)]
        inst = _installment(n_total=12, n_paid=0)
        score = calcular_score_financeiro(
            transacoes=txs, budgets=budgets, installments=[inst],
            taxa_poupanca_atual=25.0, meta_poupanca=20.0, caixa_pct=25.0,
        )
        assert score.total == 100
        assert score.cumpriu_orcamento
        assert score.atingiu_meta_poupanca
        assert score.caixa_m2_ok
        assert score.sem_gasto_acima_media
        assert score.sem_parcela_atrasada

    def test_score_parcial_sem_poupanca(self):
        txs = [_ganho(1000), _gasto("Alimentação", 900)]
        budgets = [_budget("Alimentação", 1000)]
        score = calcular_score_financeiro(
            transacoes=txs, budgets=budgets, installments=[],
            taxa_poupanca_atual=5.0, meta_poupanca=20.0, caixa_pct=25.0,
        )
        assert not score.atingiu_meta_poupanca
        assert score.detalhes["poupanca"] == 0
        assert score.total < 100

    def test_score_com_criterios_negativos(self):
        """Parcela atrasada, estouro de orçamento e caixa insuficiente."""
        txs = [_ganho(1000), _gasto("Alimentação", 1500)]  # estouro
        budgets = [_budget("Alimentação", 500)]
        inst_atrasado = Installment(
            description="Atrasado", total_amount=600.0, n_total=6, n_paid=0,
            start_date=date(2025, 1, 1),  # vencida em 2025, hoje 2026
        )
        score = calcular_score_financeiro(
            transacoes=txs, budgets=budgets,
            installments=[inst_atrasado],
            taxa_poupanca_atual=0.0, meta_poupanca=20.0, caixa_pct=5.0,
        )
        assert not score.cumpriu_orcamento
        assert not score.atingiu_meta_poupanca
        assert not score.caixa_m2_ok
        assert not score.sem_parcela_atrasada

    def test_score_sem_budgets_orcamento_ok(self):
        score = calcular_score_financeiro(
            transacoes=[], budgets=[], installments=[],
            taxa_poupanca_atual=30.0, meta_poupanca=20.0, caixa_pct=30.0,
        )
        assert score.cumpriu_orcamento  # sem budgets = sem estouro
        assert score.detalhes["orcamento"] == 30


class TestDetectarAlertasPadrao:
    def test_gasto_acima_media_detectado(self):
        mes_atual = [_gasto("Alimentação", 1300)]
        historico = [_gasto("Alimentação", 300), _gasto("Alimentação", 400), _gasto("Alimentação", 350)]
        alertas = detectar_alertas_padrao(mes_atual, historico, threshold=1.3)
        assert len(alertas) == 1
        assert alertas[0].category == "Alimentação"
        assert alertas[0].ratio > 1.3

    def test_gasto_dentro_da_media_sem_alerta(self):
        mes_atual = [_gasto("Alimentação", 500)]
        historico = [_gasto("Alimentação", 400), _gasto("Alimentação", 450), _gasto("Alimentação", 500)]
        alertas = detectar_alertas_padrao(mes_atual, historico)
        assert alertas == []

    def test_sem_historico_sem_alerta(self):
        mes_atual = [_gasto("Transporte", 200)]
        alertas = detectar_alertas_padrao(mes_atual, [])
        assert alertas == []

    def test_multiplas_categorias_alerta(self):
        mes_atual = [_gasto("Lazer", 2000), _gasto("Saúde", 800)]
        historico = [_gasto("Lazer", 300), _gasto("Saúde", 200)] * 3
        alertas = detectar_alertas_padrao(mes_atual, historico)
        codigos = {a.category for a in alertas}
        assert "Lazer" in codigos
        assert "Saúde" in codigos


class TestCalcularUsoOrcamento:
    def test_status_ok(self):
        txs = [_gasto("Alimentação", 500)]
        budgets = [_budget("Alimentação", 1000)]
        status = calcular_uso_orcamento(txs, budgets)
        assert len(status) == 1
        assert status[0].status == "OK"
        assert status[0].pct == 50.0

    def test_status_alerta(self):
        txs = [_gasto("Alimentação", 850)]
        budgets = [_budget("Alimentação", 1000)]
        status = calcular_uso_orcamento(txs, budgets)
        assert status[0].status == "ALERTA"

    def test_status_estouro(self):
        txs = [_gasto("Alimentação", 1200)]
        budgets = [_budget("Alimentação", 1000)]
        status = calcular_uso_orcamento(txs, budgets)
        assert status[0].status == "ESTOURO"
        assert status[0].pct == pytest.approx(120.0)

    def test_sem_gastos_na_categoria(self):
        budgets = [_budget("Lazer", 500)]
        status = calcular_uso_orcamento([], budgets)
        assert status[0].gasto == 0.0
        assert status[0].pct == 0.0

    def test_ganhos_ignorados_no_orcamento(self):
        txs = [_ganho(1000), _gasto("Outros", 200)]
        budgets = [_budget("Outros", 500)]
        status = calcular_uso_orcamento(txs, budgets)
        assert status[0].gasto == 200.0
