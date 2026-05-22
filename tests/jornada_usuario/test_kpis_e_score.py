"""
KPIs do Dashboard, Score Financeiro e Tendências Mensais.
"""
from __future__ import annotations

from datetime import date

import pytest

from models.transaction import Category
from core.weekly_report import gerar_relatorio_semanal, MonthlyTrend
from .scenario_builders import (
    ganho as _ganho,
    build_historico as _build_historico,
    build_maio as _build_maio,
    build_budgets as _build_budgets,
)


class TestKPIsDashboard:
    """O relatório deve expor os KPIs corretos de saldo para o mês."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )

    def test_saldo_ganhos_corretos(self):
        r = self._relatorio()
        assert r.saldo_mes.total_ganhos == pytest.approx(12_000.0)

    def test_saldo_gastos_corretos(self):
        r = self._relatorio()
        # 2000+850+200+400+350+150+600+500+180+250+2000 = 7480
        assert r.saldo_mes.total_gastos == pytest.approx(7_480.0)

    def test_saldo_liquido_correto(self):
        r = self._relatorio()
        assert r.saldo_mes.saldo == pytest.approx(4_520.0)

    def test_taxa_poupanca_calculada(self):
        r = self._relatorio()
        # 4520 / 12000 ≈ 37.67%
        assert r.saldo_mes.taxa_poupanca == pytest.approx(37.7, abs=0.5)

    def test_relatorio_identifica_mes_e_ano(self):
        r = self._relatorio()
        assert r.ano == 2026
        assert r.mes == 5


class TestScoreFinanceiro:
    """Score deve refletir o estado real do mês (sem orçamentos → orcamento OK)."""

    def test_score_sem_budgets_e_sem_parcelas_tem_maximo_possivel(self):
        txs = [_ganho(date(2026, 5, 5), 10_000.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[],
            ano=2026, mes=5, meta_poupanca=10.0, caixa_pct=25.0,
        )
        # Sem budgets (ok), poupança 100% (ok), caixa 25% (ok), sem histórico 3m (ok), sem parcelas (ok)
        assert r.score.total == 100

    def test_score_com_estouro_desconta_orcamento(self):
        txs = _build_historico() + _build_maio()
        budgets = _build_budgets()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=budgets,
            ano=2026, mes=5, meta_poupanca=40.0, caixa_pct=15.0,
        )
        # Orçamento: ESTOURO em Alimentação → -30
        # Poupança: 37.7 < 40 → -25
        # Caixa: 15 < 20 → -20
        # Máximo possível: 15 (sem gasto acima da média 3m) + 10 (sem parcela) = 25
        assert r.score.total <= 25
        assert not r.score.cumpriu_orcamento
        assert not r.score.atingiu_meta_poupanca
        assert not r.score.caixa_m2_ok

    def test_score_tem_detalhes_por_criterio(self):
        txs = [_ganho(date(2026, 5, 5), 10_000.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        assert "orcamento" in r.score.detalhes
        assert "poupanca"  in r.score.detalhes
        assert "caixa"     in r.score.detalhes
        assert "media"     in r.score.detalhes
        assert "parcelas"  in r.score.detalhes


class TestTendenciasMensais:
    """Relatório deve conter tendências históricas mês a mês."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )

    def test_tendencias_contem_meses_do_historico(self):
        r = self._relatorio()
        meses = [(t.ano, t.mes) for t in r.tendencias]
        assert (2026, 2) in meses
        assert (2026, 3) in meses
        assert (2026, 4) in meses
        assert (2026, 5) in meses

    def test_tendencias_ordenadas_cronologicamente(self):
        r = self._relatorio()
        pares = [(t.ano, t.mes) for t in r.tendencias]
        assert pares == sorted(pares)

    def test_tendencias_tem_ganhos_gastos_saldo(self):
        r = self._relatorio()
        maio = next(t for t in r.tendencias if t.mes == 5)
        assert maio.ganhos == pytest.approx(12_000.0)
        assert maio.gastos == pytest.approx(7_480.0)
        assert maio.saldo  == pytest.approx(4_520.0)

    def test_tendencias_tem_taxa_poupanca(self):
        r = self._relatorio()
        fev = next(t for t in r.tendencias if t.mes == 2)
        # ganhos 12000, gastos 3550 → saldo 8450 → ~70.4%
        assert fev.taxa_poupanca > 0

    def test_tendencia_sem_historico_tem_apenas_mes_atual(self):
        txs = [_ganho(date(2026, 5, 5), 5_000.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        assert len(r.tendencias) == 1
        assert r.tendencias[0].mes == 5
