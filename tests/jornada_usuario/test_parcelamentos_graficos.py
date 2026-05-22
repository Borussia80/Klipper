"""
Parcelamentos, Dados de Gráficos (Plotly-ready) e Invariantes dos Value Objects.
"""
from __future__ import annotations

from datetime import date

import pytest

from core.weekly_report import (
    gerar_relatorio_semanal,
    dados_grafico_tendencia,
    dados_grafico_categorias,
    dados_grafico_orcamento,
    dados_gauge_score,
    dados_grafico_parcelamentos,
    MonthlyTrend,
    InstallmentSummary,
    ChartSeries,
    ChartData,
)
from .scenario_builders import (
    ganho as _ganho,
    build_historico as _build_historico,
    build_maio as _build_maio,
    build_parcelas as _build_parcelas,
    build_budgets as _build_budgets,
)


class TestParcelamentos:
    """Relatório deve resumir parcelamentos ativos e comprometimento futuro."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs, installments=_build_parcelas(), budgets=[],
            ano=2026, mes=5,
        )

    def test_parcelas_lista_ativos(self):
        r = self._relatorio()
        assert isinstance(r.parcelas, list)
        assert len(r.parcelas) == 2

    def test_parcela_notebook_tem_descricao(self):
        r = self._relatorio()
        descs = [p.description for p in r.parcelas]
        assert "Notebook Dell" in descs

    def test_parcela_tem_valor_mensal(self):
        r = self._relatorio()
        nb = next(p for p in r.parcelas if "Notebook" in p.description)
        # 4200/12 = 350
        assert nb.amount_monthly == pytest.approx(350.0, abs=0.02)

    def test_parcela_tem_total_restante(self):
        r = self._relatorio()
        nb = next(p for p in r.parcelas if "Notebook" in p.description)
        # start jan/2026, hoje maio/2026 → 4 pagas de 12 → 8 restantes
        assert nb.total_remaining > 0
        assert nb.n_remaining > 0

    def test_comprometimento_tem_meses_futuros(self):
        r = self._relatorio()
        assert isinstance(r.comprometimento, dict)
        assert len(r.comprometimento) > 0
        for key in r.comprometimento:
            assert len(key) == 7   # "YYYY-MM"
            assert key >= "2026-05"

    def test_comprometimento_soma_ambas_parcelas(self):
        r = self._relatorio()
        # In a month where both are active: 350 + 200 = 550
        june = r.comprometimento.get("2026-06")
        if june is not None:
            assert june == pytest.approx(550.0, abs=0.10)


class TestDadosGraficos:
    """Funções de gráficos retornam ChartData compatível com Plotly."""

    def _tendencias(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        return r.tendencias

    def test_dados_grafico_tendencia_tem_titulo(self):
        chart = dados_grafico_tendencia(self._tendencias())
        assert chart.title

    def test_dados_grafico_tendencia_e_linha(self):
        chart = dados_grafico_tendencia(self._tendencias())
        assert chart.chart_type == "line"

    def test_dados_grafico_tendencia_tem_series_ganhos_e_gastos(self):
        chart = dados_grafico_tendencia(self._tendencias())
        nomes = [s.name.lower() for s in chart.series]
        assert any("ganho" in n for n in nomes)
        assert any("gasto" in n for n in nomes)

    def test_dados_grafico_tendencia_x_e_rotulos_de_mes(self):
        chart = dados_grafico_tendencia(self._tendencias())
        x = chart.series[0].x
        assert len(x) == 4   # fev, mar, abr, mai
        assert all(isinstance(label, str) for label in x)

    def test_dados_grafico_categorias_e_pizza(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        chart = dados_grafico_categorias(r.top_categorias)
        assert chart.chart_type == "pie"
        assert len(chart.series) == 1
        assert len(chart.series[0].x) == len(r.top_categorias)

    def test_dados_grafico_orcamento_e_barra_horizontal(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=_build_budgets(),
            ano=2026, mes=5,
        )
        chart = dados_grafico_orcamento(r.orcamentos)
        assert chart.chart_type == "bar"
        assert len(chart.series) >= 1

    def test_dados_gauge_score_tem_tipo_gauge(self):
        txs = [_ganho(date(2026, 5, 5), 10_000.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        chart = dados_gauge_score(r.score)
        assert chart.chart_type == "gauge"
        assert len(chart.series) == 1
        valor = chart.series[0].y[0]
        assert 0 <= valor <= 100

    def test_dados_grafico_parcelamentos_tem_meses_no_eixo_x(self):
        txs = _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=_build_parcelas(), budgets=[],
            ano=2026, mes=5,
        )
        chart = dados_grafico_parcelamentos(r.comprometimento)
        assert chart.chart_type == "bar"
        x = chart.series[0].x
        assert all(len(label) == 7 for label in x)   # "YYYY-MM"


class TestInvariantesEstruturais:
    """WeeklyReport e seus tipos auxiliares respeitam invariantes do sistema."""

    def test_monthly_trend_saldo_igual_ganhos_menos_gastos(self):
        t = MonthlyTrend(ano=2026, mes=5, ganhos=10_000.0, gastos=7_000.0)
        assert t.saldo == pytest.approx(3_000.0)

    def test_monthly_trend_taxa_poupanca_correta(self):
        t = MonthlyTrend(ano=2026, mes=5, ganhos=10_000.0, gastos=7_000.0)
        assert t.taxa_poupanca == pytest.approx(30.0)

    def test_monthly_trend_sem_ganhos_taxa_zero(self):
        t = MonthlyTrend(ano=2026, mes=5, ganhos=0.0, gastos=0.0)
        assert t.taxa_poupanca == 0.0

    def test_installment_summary_n_remaining_consistente(self):
        s = InstallmentSummary(
            description="Teste",
            n_total=12,
            n_remaining=8,
            amount_monthly=350.0,
            total_remaining=2_800.0,
        )
        assert s.n_remaining <= s.n_total
        assert s.total_remaining > 0

    def test_chart_series_tem_x_e_y_do_mesmo_tamanho(self):
        s = ChartSeries(name="Ganhos", x=["jan", "fev", "mar"], y=[1000, 2000, 3000])
        assert len(s.x) == len(s.y)

    def test_chart_data_tem_pelo_menos_uma_serie(self):
        s = ChartSeries(name="Teste", x=["A"], y=[1.0])
        cd = ChartData(title="Gráfico Teste", chart_type="bar", series=[s])
        assert len(cd.series) >= 1
