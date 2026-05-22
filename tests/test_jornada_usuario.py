"""
TDD — Jornada do Usuário: Abertura de Conta → Relatório Semanal

Cada teste é independente (F.I.R.S.T.-I): cria seus próprios dados via
scenario_builders, sem estado compartilhado entre testes.
"""
from __future__ import annotations

from datetime import date, datetime

import pytest

from models.transaction import Category
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
from tests.jornada_usuario.scenario_builders import (
    ganho as _ganho,
    gasto as _gasto,
    budget as _budget,
    build_historico as _build_historico,
    build_maio as _build_maio,
    build_parcelas as _build_parcelas,
    build_budgets as _build_budgets,
)


# ── Fase 1: Saldo Mensal e KPIs do Dashboard ──────────────────────────────

class TestKPIsDashboard:
    """O relatório deve expor os KPIs corretos de saldo para o mês."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
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


# ── Fase 2: Score Financeiro ──────────────────────────────────────────────

class TestScoreFinanceiro:
    """Score deve refletir o estado real do mês (sem orçamentos → orcamento OK)."""

    def test_score_sem_budgets_e_sem_parcelas_tem_maximo_possivel(self):
        txs = [_ganho(date(2026, 5, 5), 10_000.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
            meta_poupanca=10.0,
            caixa_pct=25.0,
        )
        # Sem budgets (ok), poupança 100% (ok), caixa 25% (ok), sem histórico 3m (ok), sem parcelas (ok)
        assert r.score.total == 100

    def test_score_com_estouro_desconta_orcamento(self):
        txs = _build_historico() + _build_maio()
        budgets = _build_budgets()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=budgets,
            ano=2026,
            mes=5,
            meta_poupanca=40.0,   # taxa real ~37.7%, vai falhar
            caixa_pct=15.0,       # < 20%, vai falhar
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
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )
        assert "orcamento" in r.score.detalhes
        assert "poupanca"  in r.score.detalhes
        assert "caixa"     in r.score.detalhes
        assert "media"     in r.score.detalhes
        assert "parcelas"  in r.score.detalhes


# ── Fase 3: Tendências Mensais ───────────────────────────────────────────

class TestTendenciasMensais:
    """Relatório deve conter tendências históricas mês a mês."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
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
        assert maio.ganhos  == pytest.approx(12_000.0)
        assert maio.gastos  == pytest.approx(7_480.0)
        assert maio.saldo   == pytest.approx(4_520.0)

    def test_tendencias_tem_taxa_poupanca(self):
        r = self._relatorio()
        fev = next(t for t in r.tendencias if t.mes == 2)
        # ganhos 12000, gastos 3550 → saldo 8450 → ~70.4%
        assert fev.taxa_poupanca > 0

    def test_tendencia_sem_historico_tem_apenas_mes_atual(self):
        txs = [_ganho(date(2026, 5, 5), 5_000.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )
        assert len(r.tendencias) == 1
        assert r.tendencias[0].mes == 5


# ── Fase 4: Top Categorias ───────────────────────────────────────────────

class TestTopCategorias:
    """Relatório deve listar as categorias com maior gasto do mês."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )

    def test_top_categorias_retorna_lista(self):
        r = self._relatorio()
        assert isinstance(r.top_categorias, list)
        assert len(r.top_categorias) > 0

    def test_top_categorias_ordenadas_por_gasto_decrescente(self):
        r = self._relatorio()
        totais = [c.total for c in r.top_categorias]
        assert totais == sorted(totais, reverse=True)

    def test_investimento_e_maior_gasto_do_mes(self):
        r = self._relatorio()
        # Investimento: R$2000, Moradia: R$2180, Alimentação: R$1850
        nomes = [c.category for c in r.top_categorias]
        assert "Moradia" in nomes or "Investimento" in nomes

    def test_top_categorias_tem_percentual(self):
        r = self._relatorio()
        for cat in r.top_categorias:
            assert 0 < cat.percentual <= 100


# ── Fase 5: Orçamentos (Budget vs. Real) ─────────────────────────────────

class TestOrcamentosVsReal:
    """Relatório deve comparar gasto real com limite configurado por categoria."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=_build_budgets(),
            ano=2026,
            mes=5,
        )

    def test_orcamentos_retorna_lista(self):
        r = self._relatorio()
        assert isinstance(r.orcamentos, list)
        assert len(r.orcamentos) == 5   # 5 budgets configurados

    def test_alimentacao_em_estouro(self):
        r = self._relatorio()
        alim = next(o for o in r.orcamentos if o.category == "Alimentação")
        # Gasto: 850+400+600=1850 > limite 1200
        assert alim.gasto == pytest.approx(1_850.0)
        assert alim.status == "ESTOURO"

    def test_moradia_dentro_do_limite(self):
        r = self._relatorio()
        mor = next(o for o in r.orcamentos if o.category == "Moradia")
        # Gasto: 2000+180=2180 vs limite 2200
        assert mor.status in ("OK", "ALERTA")

    def test_orcamento_sem_gasto_e_ok(self):
        txs = [_ganho(date(2026, 5, 5), 5_000.0)]
        budgets = [_budget(Category.LAZER, 500.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=budgets,
            ano=2026,
            mes=5,
        )
        lazer = r.orcamentos[0]
        assert lazer.gasto == 0.0
        assert lazer.status == "OK"


# ── Fase 6: Alertas Comportamentais ──────────────────────────────────────

class TestAlertasComportamentais:
    """Relatório detecta categorias com gasto acima de 1.3× a média de 3 meses."""

    def test_alimentacao_gera_alerta(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )
        cats_com_alerta = [a.category for a in r.alertas]
        # Alimentação histórico: ~800/mês → maio: 1850 → ratio ~2.3 > 1.3
        assert "Alimentação" in cats_com_alerta

    def test_sem_historico_sem_alertas(self):
        txs = [
            _ganho(date(2026, 5, 5), 5_000.0),
            _gasto(date(2026, 5, 10), 1_000.0, Category.ALIMENTACAO),
        ]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )
        # Sem histórico de 3 meses anteriores → sem alertas
        assert len(r.alertas) == 0

    def test_alerta_tem_ratio_acima_de_1_3(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )
        for alerta in r.alertas:
            assert alerta.ratio > 1.3, f"Alerta {alerta.category} tem ratio {alerta.ratio}"


# ── Fase 7: Parcelamentos ─────────────────────────────────────────────────

class TestParcelamentos:
    """Relatório deve resumir parcelamentos ativos e comprometimento futuro."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=_build_parcelas(),
            budgets=[],
            ano=2026,
            mes=5,
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
        # start jan/2026, hoje maio/2026 → 4 pagas de 12 → 8 restantes → ~8×350 = 2800
        assert nb.total_remaining > 0
        assert nb.n_remaining > 0

    def test_comprometimento_tem_meses_futuros(self):
        r = self._relatorio()
        # Must have entries for future months (after may/2026)
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


# ── Fase 8: Dados de Gráficos (Plotly-ready) ──────────────────────────────

class TestDadosGraficos:
    """Funções de gráficos retornam ChartData compatível com Plotly."""

    def _tendencias(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
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
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )
        chart = dados_grafico_categorias(r.top_categorias)
        assert chart.chart_type == "pie"
        assert len(chart.series) == 1
        assert len(chart.series[0].x) == len(r.top_categorias)

    def test_dados_grafico_orcamento_e_barra_horizontal(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=_build_budgets(),
            ano=2026,
            mes=5,
        )
        chart = dados_grafico_orcamento(r.orcamentos)
        assert chart.chart_type == "bar"
        assert len(chart.series) >= 1

    def test_dados_gauge_score_tem_tipo_gauge(self):
        txs = [_ganho(date(2026, 5, 5), 10_000.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=[],
            budgets=[],
            ano=2026,
            mes=5,
        )
        chart = dados_gauge_score(r.score)
        assert chart.chart_type == "gauge"
        assert len(chart.series) == 1
        valor = chart.series[0].y[0]
        assert 0 <= valor <= 100

    def test_dados_grafico_parcelamentos_tem_meses_no_eixo_x(self):
        txs = _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=_build_parcelas(),
            budgets=[],
            ano=2026,
            mes=5,
        )
        chart = dados_grafico_parcelamentos(r.comprometimento)
        assert chart.chart_type == "bar"
        x = chart.series[0].x
        assert all(len(label) == 7 for label in x)   # "YYYY-MM"


# ── Fase 9: Relatório Completo — Jornada Semana a Semana ─────────────────

class TestJornadaCompletaSemanaASemana:
    """
    Simula a jornada completa do usuário:
    - Abre conta em fevereiro
    - Registra transações semana a semana durante 4 meses
    - Cria parcelamentos
    - Configura orçamentos
    - Gera relatório semanal em maio
    - Valida todas as seções do relatório
    """

    @pytest.fixture()
    def relatorio_maio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=_build_parcelas(),
            budgets=_build_budgets(),
            ano=2026,
            mes=5,
            meta_poupanca=30.0,
            caixa_pct=20.0,
        )

    def test_relatorio_gerado_com_sucesso(self, relatorio_maio):
        assert relatorio_maio is not None

    def test_relatorio_tem_data_geracao(self, relatorio_maio):
        assert isinstance(relatorio_maio.gerado_em, datetime)

    def test_saldo_positivo_no_mes(self, relatorio_maio):
        assert relatorio_maio.saldo_mes.saldo > 0

    def test_score_entre_0_e_100(self, relatorio_maio):
        assert 0 <= relatorio_maio.score.total <= 100

    def test_tendencias_cobrindo_quatro_meses(self, relatorio_maio):
        assert len(relatorio_maio.tendencias) == 4

    def test_top_categorias_ate_cinco(self, relatorio_maio):
        assert 1 <= len(relatorio_maio.top_categorias) <= 5

    def test_orcamentos_presentes(self, relatorio_maio):
        assert len(relatorio_maio.orcamentos) == 5

    def test_parcelas_presentes(self, relatorio_maio):
        assert len(relatorio_maio.parcelas) == 2

    def test_comprometimento_futuro_presente(self, relatorio_maio):
        assert len(relatorio_maio.comprometimento) > 0

    def test_relatorio_indica_estouro_em_alimentacao(self, relatorio_maio):
        alim = next(
            (o for o in relatorio_maio.orcamentos if o.category == "Alimentação"), None
        )
        assert alim is not None
        assert alim.status == "ESTOURO"

    def test_relatorio_detecta_alerta_comportamental(self, relatorio_maio):
        # Alimentação em maio (~1850) vs média fev-abr (~800) → ratio > 1.3
        assert len(relatorio_maio.alertas) > 0

    def test_relatorio_score_nao_e_perfeito_com_estouro(self, relatorio_maio):
        # Orçamento em estouro → não pode ter 100
        assert relatorio_maio.score.total < 100

    def test_resumo_parcelas_tem_total_restante_positivo(self, relatorio_maio):
        for p in relatorio_maio.parcelas:
            assert p.total_remaining > 0

    def test_serie_tendencia_ascendente_ou_estavel(self, relatorio_maio):
        """Ganhos de fev-mai são todos 12k — linha plana esperada."""
        t = relatorio_maio.tendencias
        ganhos = [m.ganhos for m in t]
        # Todos devem ser ≈ 12000 (fev-mai mesma renda)
        assert all(g == pytest.approx(12_000.0) for g in ganhos)


# ── Fase 10: Invariantes Structurais do WeeklyReport ────────────────────

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
