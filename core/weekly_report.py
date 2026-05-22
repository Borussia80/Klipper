"""
Relatório Semanal — Klipper

Agrega todas as camadas analíticas (saldo, score, tendências, orçamento,
alertas comportamentais, parcelamentos) em um único WeeklyReport pronto
para renderização no Dashboard e export.

SRP: este módulo só sabe montar e serializar o relatório. Não conhece Streamlit
nem repositórios.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from models.transaction import Transaction, TransactionType
from models.budget import Budget
from models.installment import Installment
from core.analytics import SaldoMensal, CategoriaResumo, calcular_saldo_mensal, calcular_top_categorias
from core.behavioral import (
    ScoreFinanceiro,
    OrcamentoStatus,
    BehavioralAlert,
    calcular_score_financeiro,
    calcular_uso_orcamento,
    detectar_alertas_padrao,
)
from core.installment_engine import gerar_parcelas, calcular_comprometimento_mensal


# ── Tipos de dados do relatório ───────────────────────────────────────────────

@dataclass
class MonthlyTrend:
    ano: int
    mes: int
    ganhos: float
    gastos: float

    @property
    def saldo(self) -> float:
        return round(self.ganhos - self.gastos, 2)

    @property
    def taxa_poupanca(self) -> float:
        if self.ganhos == 0:
            return 0.0
        return round(self.saldo / self.ganhos * 100, 1)


@dataclass
class InstallmentSummary:
    description: str
    n_total: int
    n_remaining: int
    amount_monthly: float
    total_remaining: float


@dataclass
class ChartSeries:
    name: str
    x: list
    y: list
    color: str = ""


@dataclass
class ChartData:
    title: str
    chart_type: str   # "line" | "bar" | "pie" | "gauge"
    series: list[ChartSeries]
    x_label: str = ""
    y_label: str = ""


@dataclass
class WeeklyReport:
    ano: int
    mes: int
    saldo_mes: SaldoMensal
    score: ScoreFinanceiro
    tendencias: list[MonthlyTrend]
    top_categorias: list[CategoriaResumo]
    orcamentos: list[OrcamentoStatus]
    alertas: list[BehavioralAlert]
    parcelas: list[InstallmentSummary]
    comprometimento: dict[str, float]
    gerado_em: datetime = field(default_factory=datetime.now)


# ── Geração do relatório ──────────────────────────────────────────────────────

def gerar_relatorio_semanal(
    transacoes_historico: list[Transaction],
    installments: list[Installment],
    budgets: list[Budget],
    ano: int,
    mes: int,
    meta_poupanca: float = 20.0,
    caixa_pct: float = 0.0,
) -> WeeklyReport:
    """
    Monta o WeeklyReport completo para o mês especificado.

    transacoes_historico deve conter transações de todos os meses relevantes
    (incluindo o mês corrente e pelo menos os 3 anteriores para alertas).
    """
    txs_mes = [t for t in transacoes_historico if t.date.year == ano and t.date.month == mes]
    txs_3m  = _transacoes_tres_meses_anteriores(transacoes_historico, ano, mes)

    saldo_mes    = calcular_saldo_mensal(txs_mes, ano, mes)
    top_cats     = calcular_top_categorias(txs_mes)
    orcamentos   = calcular_uso_orcamento(txs_mes, budgets)
    alertas      = detectar_alertas_padrao(txs_mes, txs_3m) if txs_3m else []
    tendencias   = _calcular_tendencias(transacoes_historico, ano, mes)
    score        = calcular_score_financeiro(
        transacoes=txs_mes,
        budgets=budgets,
        installments=installments,
        taxa_poupanca_atual=saldo_mes.taxa_poupanca,
        meta_poupanca=meta_poupanca,
        caixa_pct=caixa_pct,
        transacoes_3_meses=txs_3m,
    )
    parcelas_sum = _resumir_parcelas(installments)
    comprometimento = calcular_comprometimento_mensal(installments)

    return WeeklyReport(
        ano=ano,
        mes=mes,
        saldo_mes=saldo_mes,
        score=score,
        tendencias=tendencias,
        top_categorias=top_cats,
        orcamentos=orcamentos,
        alertas=alertas,
        parcelas=parcelas_sum,
        comprometimento=comprometimento,
    )


# ── Helpers internos ──────────────────────────────────────────────────────────

def _transacoes_tres_meses_anteriores(
    transacoes: list[Transaction], ano: int, mes: int
) -> list[Transaction]:
    """Retorna transações dos 3 meses imediatamente anteriores ao mês de referência."""
    meses_anteriores: list[tuple[int, int]] = []
    m, a = mes - 1, ano
    for _ in range(3):
        if m == 0:
            m = 12
            a -= 1
        meses_anteriores.append((a, m))
        m -= 1
    return [
        t for t in transacoes
        if (t.date.year, t.date.month) in meses_anteriores
    ]


def _calcular_tendencias(
    transacoes: list[Transaction], ano: int, mes: int
) -> list[MonthlyTrend]:
    """Extrai MonthlyTrend para cada mês presente no histórico, ordenado."""
    meses_unicos: set[tuple[int, int]] = {
        (t.date.year, t.date.month) for t in transacoes
    }
    tendencias: list[MonthlyTrend] = []
    for a, m in sorted(meses_unicos):
        txs_m = [t for t in transacoes if t.date.year == a and t.date.month == m]
        ganhos = sum(t.amount for t in txs_m if t.type == TransactionType.GANHO)
        gastos = sum(t.amount for t in txs_m if t.type == TransactionType.GASTO)
        tendencias.append(MonthlyTrend(ano=a, mes=m, ganhos=round(ganhos, 2), gastos=round(gastos, 2)))
    return tendencias


def _resumir_parcelas(installments: list[Installment]) -> list[InstallmentSummary]:
    """Converte Installments ativos em InstallmentSummary para o relatório."""
    hoje = date.today()
    summaries: list[InstallmentSummary] = []
    for inst in installments:
        if not inst.is_active:
            continue
        txs = gerar_parcelas(inst)
        pagas = sum(1 for tx in txs if tx.date <= hoje)
        n_paid = max(inst.n_paid, pagas)
        n_remaining = max(0, inst.n_total - n_paid)
        total_remaining = round(
            sum(inst.amount_for_installment(i) for i in range(n_paid, inst.n_total)), 2
        )
        summaries.append(InstallmentSummary(
            description=inst.description,
            n_total=inst.n_total,
            n_remaining=n_remaining,
            amount_monthly=inst.amount_for_installment(0),
            total_remaining=total_remaining,
        ))
    return summaries


# ── Funções de Chart Data (Plotly-ready) ─────────────────────────────────────

_MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}


def dados_grafico_tendencia(tendencias: list[MonthlyTrend]) -> ChartData:
    """Gráfico de linhas: Ganhos e Gastos mês a mês."""
    labels = [f"{_MESES_PT[t.mes]}/{str(t.ano)[2:]}" for t in tendencias]
    return ChartData(
        title="Fluxo Financeiro",
        chart_type="line",
        x_label="Mês",
        y_label="R$",
        series=[
            ChartSeries(name="Ganhos", x=labels, y=[t.ganhos for t in tendencias], color="#10B981"),
            ChartSeries(name="Gastos", x=labels, y=[t.gastos for t in tendencias], color="#EF4444"),
        ],
    )


def dados_grafico_categorias(top_categorias: list[CategoriaResumo]) -> ChartData:
    """Gráfico de pizza: distribuição de gastos por categoria."""
    labels = [c.category for c in top_categorias]
    values = [c.total for c in top_categorias]
    return ChartData(
        title="Gastos por Categoria",
        chart_type="pie",
        series=[ChartSeries(name="Gastos", x=labels, y=values)],
    )


def dados_grafico_orcamento(orcamentos: list[OrcamentoStatus]) -> ChartData:
    """Gráfico de barras horizontais: gasto vs limite por categoria."""
    labels = [o.category for o in orcamentos]
    return ChartData(
        title="Orçamento vs Real",
        chart_type="bar",
        x_label="R$",
        y_label="Categoria",
        series=[
            ChartSeries(name="Gasto", x=labels, y=[o.gasto for o in orcamentos], color="#6366F1"),
            ChartSeries(name="Limite", x=labels, y=[o.limite for o in orcamentos], color="#E2E8F0"),
        ],
    )


def dados_gauge_score(score: ScoreFinanceiro) -> ChartData:
    """Gauge circular: Score Financeiro 0–100."""
    return ChartData(
        title="Score Financeiro",
        chart_type="gauge",
        series=[ChartSeries(name="Score", x=["Score"], y=[score.total])],
    )


def dados_grafico_parcelamentos(comprometimento: dict[str, float]) -> ChartData:
    """Gráfico de barras: comprometimento mensal com parcelas futuras."""
    meses = sorted(comprometimento.keys())
    valores = [comprometimento[m] for m in meses]
    return ChartData(
        title="Comprometimento com Parcelas",
        chart_type="bar",
        x_label="Mês",
        y_label="R$",
        series=[ChartSeries(name="Parcelas", x=meses, y=valores, color="#F59E0B")],
    )
