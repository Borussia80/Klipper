"""Home — O dia em dinheiro · feed financeiro."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date
from decimal import Decimal

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.analytics import (
    calcular_saldo_mensal, calcular_top_categorias,
    preparar_dados_donut_categorias, preparar_dados_barras_mensais,
    preparar_sparkline_score_historico,
)
from core.behavioral import calcular_score_financeiro, detectar_alertas_padrao
from core.installment_engine import calcular_comprometimento_mensal
from core.m2_governance import verificar_limites, hard_fail, CAIXA_MIN_PCT
import html
import re

from core.repositories import (
    InvestmentRepository, TransactionRepository,
    InstallmentRepository, BudgetRepository,
    BankAccountRepository, CreditCardRepository,
)
from core.auth import require_auth
from core.styles import (
    inject_css, fmt_brl, fmt_pct, kicker, k_card, k_card_with_header,
    stat_card, feed_row, mood_chip, chip, bar_track, section_header,
    render_navigation, sidebar_engines, sidebar_user,
    tx_row, hero_section, CAT_COLORS, load_page_icon, sidebar_ai_qa,
    setup_sidebar, k_radar_notification_card, k_premium_empty_state,
)
from models.transaction import TransactionType

st.set_page_config(page_title="Home · Klipper", page_icon=load_page_icon(), layout="wide", initial_sidebar_state="collapsed")
inject_css()
require_auth()

hoje = date.today()
ano = hoje.year
mes = hoje.month

tx_repo   = TransactionRepository()
inv_repo  = InvestmentRepository()
inst_repo = InstallmentRepository()
bud_repo  = BudgetRepository()
acc_repo  = BankAccountRepository()
card_repo = CreditCardRepository()

with st.spinner(""):
    try:
        transacoes   = tx_repo.list_by_month(ano, mes)
        portfolio    = inv_repo.get_portfolio()
        installments = inst_repo.list_active()
        budgets      = bud_repo.list_by_month(ano, mes)
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        st.stop()

try:
    contas  = acc_repo.list_active()
    cartoes = card_repo.list_active()
except Exception:
    contas, cartoes = [], []

transacoes_3m: list = []
_historico_6m: list = []  # (ano, mes, ganhos, gastos) para bar chart
for delta in range(1, 7):
    m_prev, y_prev = mes - delta, ano
    while m_prev < 1:
        m_prev += 12; y_prev -= 1
    try:
        txs_prev = tx_repo.list_by_month(y_prev, m_prev)
        if delta <= 3:
            transacoes_3m.extend(txs_prev)
        saldo_prev = calcular_saldo_mensal(txs_prev, y_prev, m_prev)
        _historico_6m.append((y_prev, m_prev, saldo_prev.total_ganhos, saldo_prev.total_gastos))
    except Exception:
        pass

saldo           = calcular_saldo_mensal(transacoes, ano, mes)
total_portfolio = sum(inv.current_value for inv in portfolio)
total_ativos    = saldo.total_ganhos + total_portfolio
caixa_pct       = (saldo.saldo / total_ativos * 100) if total_ativos > 0 else 0.0
comp_mes        = calcular_comprometimento_mensal(installments).get(hoje.strftime("%Y-%m"), 0.0)

alertas_m2 = verificar_limites(portfolio, caixa_disponivel=saldo.saldo)
violations  = sum(1 for a in alertas_m2 if a.is_hard_fail)

score = calcular_score_financeiro(
    transacoes=transacoes, budgets=budgets, installments=installments,
    taxa_poupanca_atual=saldo.taxa_poupanca, meta_poupanca=20.0,
    caixa_pct=caixa_pct, transacoes_3_meses=transacoes_3m,
)

alertas_pad = detectar_alertas_padrao(transacoes, transacoes_3m) if transacoes_3m else []

from core.financial_ai import build_financial_context
_ai_ctx = build_financial_context(
    ano, mes,
    saldo=saldo,
    score=score,
    alertas_padrao=alertas_pad,
    top_categorias=calcular_top_categorias(transacoes),
    contas=contas,
    parcelas_ativas=[i for i in installments if i.is_active],
)

# ── Layout ────────────────────────────────────────────────────────────────────

setup_sidebar(ctx=_ai_ctx, violations=violations)

# ── Hero section ─────────────────────────────────────────────────────────────
_MESES_PT_FULL = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
mes_nome  = _MESES_PT_FULL[mes]
dia_semana = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"][hoje.weekday()]
st.markdown(
    hero_section(
        title=f"Dashboard · {mes_nome[:3].lower()} {ano}",
        saldo=fmt_brl(saldo.saldo),
        ganhos=fmt_brl(saldo.total_ganhos),
        gastos=fmt_brl(saldo.total_gastos),
        subtitle=f"score {score.total}/100 · poupança {saldo.taxa_poupanca:.1f}% · caixa {caixa_pct:.0f}%",
    ),
    unsafe_allow_html=True,
)

# ── Anti-BS narrative ──────────────────────────────────────────────────────────
impulsos = alertas_pad[:]

antiBs_text = ""
if impulsos:
    cats = ", ".join(a.category for a in impulsos[:2])
    antiBs_text = f"Gastos acima da média em {cats}. Orçamento sob tensão — revise antes do próximo aporte."
elif saldo.taxa_poupanca >= 20:
    antiBs_text = "Fluxo equilibrado. Taxa de poupança dentro da meta. Aporte pode ser mantido."
else:
    antiBs_text = "Taxa de poupança abaixo de 20%. Reforce caixa antes de novos aportes."

# ── Operating cockpit header ───────────────────────────────────────────────────
_posture = (
    "estável" if score.total >= 80 else
    "controlada" if score.total >= 60 else
    "em atenção" if score.total >= 40 else "sob tensão"
)
_posture_tone = "pos" if score.total >= 80 else "brass-c" if score.total >= 60 else "warn" if score.total >= 40 else "neg"
_brief_main = antiBs_text
_brief_budget = (
    f"{alertas_pad[0].category} está {alertas_pad[0].ratio:.1f}x acima da média recente."
    if alertas_pad else
    "Sem desvio comportamental relevante nos últimos ciclos."
)
_brief_commitment = (
    f"Compromissos futuros somam {fmt_brl(comp_mes, compact=True)} neste mês."
    if comp_mes > 0 else
    "Sem pressão relevante de parcelamentos neste mês."
)

st.markdown(f"""<div class="k-operating-hero" style="margin:4px 0 16px">
  <div class="k-operating-grid">
<div>
  <div class="k-auth-kicker">Operating position · {dia_semana}, {hoje.day} {mes_nome[:3].lower()}</div>
  <div class="k-operating-title">Sua posição financeira está <span class="{_posture_tone}">{_posture}</span>.</div>
  <p class="k-operating-copy">
    {_brief_main} O cockpit abaixo resume liquidez, disciplina e compromissos para decisões sem ruído.
  </p>
</div>
<div class="k-operating-signals">
  <div class="k-signal">
    <div class="k-signal-label">Poupança</div>
    <div class="k-signal-value {'pos' if saldo.taxa_poupanca >= 20 else 'neg'}">{fmt_pct(saldo.taxa_poupanca)}</div>
  </div>
  <div class="k-signal">
    <div class="k-signal-label">Caixa M2</div>
    <div class="k-signal-value {'pos' if caixa_pct >= CAIXA_MIN_PCT else 'warn'}">{caixa_pct:.0f}%</div>
  </div>
  <div class="k-signal">
    <div class="k-signal-label">Score</div>
    <div class="k-signal-value {_posture_tone}">{score.total}/100</div>
  </div>
</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Radar Strip ───────────────────────────────────────────────────────────────
_radar_alerts = [
    {
        "category": a.category,
        "current":  float(a.gasto_atual),
        "baseline": float(a.media_3m),
        "ratio":    a.ratio,
    }
    for a in alertas_pad
]
st.markdown(k_radar_notification_card(_radar_alerts), unsafe_allow_html=True)

# ── Spending Plan hero (Simplifi-style) ───────────────────────────────────────
_dias_no_mes    = calendar.monthrange(ano, mes)[1]
_dias_restantes = max(_dias_no_mes - hoje.day + 1, 1)
_disponivel     = max(saldo.total_ganhos - saldo.total_gastos, 0)
_por_dia        = _disponivel / _dias_restantes
_pct_mes        = min(hoje.day / _dias_no_mes * 100, 100)
_pct_gasto      = min(saldo.total_gastos / saldo.total_ganhos * 100, 100) if saldo.total_ganhos > 0 else 0
_n_bud_ok       = sum(1 for b in budgets if saldo.total_gastos <= b.monthly_limit)
_disp_color     = "var(--moss)" if _disponivel > 0 else "var(--rust)"
_fill_color     = "var(--moss)" if _pct_gasto <= _pct_mes + 5 else "var(--rust)"

_bud_note = (
    f'<div style="margin-top:8px;font-size:11px;color:var(--ink-3);font-family:var(--font-sans)">'
    f'{_n_bud_ok}/{len(budgets)} categorias dentro do orçamento</div>'
) if budgets else ""

st.markdown(f"""<div class="k-spending-hero" style="margin-bottom:16px">
  <div style="display:grid;grid-template-columns:1fr auto;gap:24px;align-items:flex-start">
<div>
  <div style="font-family:var(--font-sans);font-size:10px;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--ink-4);font-weight:600;margin-bottom:6px">
    Plano de gastos · {mes_nome[:3].lower()}
  </div>
  <div class="k-spending-amount" style="color:{_disp_color}">{fmt_brl(_disponivel)}</div>
  <div class="k-spending-rate">{fmt_brl(_por_dia)}/dia · {_dias_restantes}d restantes</div>
</div>
<div style="text-align:right;min-width:130px">
  <div style="font-size:9.5px;color:var(--ink-4);letter-spacing:0.14em;text-transform:uppercase;font-weight:600">Renda</div>
  <div class="mono pos" style="font-size:17px">{fmt_brl(saldo.total_ganhos, compact=True)}</div>
  <div style="height:1px;background:var(--rule);margin:6px 0"></div>
  <div style="font-size:9.5px;color:var(--ink-4);letter-spacing:0.14em;text-transform:uppercase;font-weight:600">Gastos</div>
  <div class="mono neg" style="font-size:17px">{fmt_brl(saldo.total_gastos, compact=True)}</div>
</div>
  </div>
  <div class="k-spend-track">
<div style="position:absolute;height:100%;width:{_pct_mes:.1f}%;
  background:var(--rule-2);border-radius:var(--radius-pill)"></div>
<div style="position:absolute;height:100%;width:{_pct_gasto:.1f}%;
  background:{_fill_color};border-radius:var(--radius-pill);opacity:0.85"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;
font-size:10px;font-family:var(--font-sans);color:var(--ink-4)">
<span>dia {hoje.day} de {_dias_no_mes}</span>
<span class="mono">{_pct_gasto:.0f}% gasto · {_pct_mes:.0f}% do mês decorrido</span>
  </div>
  {_bud_note}
</div>""", unsafe_allow_html=True)

# ── Hero strip ─────────────────────────────────────────────────────────────────
gastos_hoje  = sum(t.amount for t in transacoes if t.type == TransactionType.GASTO and t.date == hoje)
ganhos_hoje  = sum(t.amount for t in transacoes if t.type == TransactionType.GANHO and t.date == hoje)
liquido_hoje = ganhos_hoje - gastos_hoje

hero_left = f"""
{kicker(f"O dia em dinheiro · {dia_semana}, {hoje.day} {mes_nome[:3].lower()}")}
<div style="display:flex;align-items:baseline;gap:14px;margin-top:8px">
  <span class="mono" style="font-size:36px;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums"
>{fmt_brl(liquido_hoje)}</span>
  <span class="mono muted" style="font-size:12px">líquido hoje</span>
</div>
<div style="display:flex;gap:18px;margin-top:14px">
  <div style="display:flex;align-items:center;gap:8px">
<span style="width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;background:rgba(123,198,138,0.12);color:var(--moss);
  font-family:var(--font-mono);font-size:12px;font-weight:600">↗</span>
<div>
  <div style="font-size:9.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-3);font-weight:600">entrou</div>
  <div class="mono" style="font-size:13px;color:var(--moss);font-weight:500">{fmt_brl(ganhos_hoje, compact=True)}</div>
</div>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
<span style="width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;background:var(--surface-2);color:var(--ink-2);
  font-family:var(--font-mono);font-size:12px;font-weight:600">↙</span>
<div>
  <div style="font-size:9.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-3);font-weight:600">saiu</div>
  <div class="mono" style="font-size:13px;color:var(--ink);font-weight:500">{fmt_brl(gastos_hoje, compact=True)}</div>
</div>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
<span style="width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;background:var(--brass-soft);color:var(--brass);
  font-family:var(--font-mono);font-size:12px;font-weight:600">◈</span>
<div>
  <div style="font-size:9.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-3);font-weight:600">parcelas/mês</div>
  <div class="mono" style="font-size:13px;color:var(--brass);font-weight:500">{fmt_brl(comp_mes, compact=True)}</div>
</div>
  </div>
</div>
<div style="border-top:1px solid var(--rule);margin-top:14px;padding-top:14px">
  <div class="serif" style="font-style:italic;font-size:13.5px;color:var(--ink-2);line-height:1.5">
"{antiBs_text}"
  </div>
  <div class="mono" style="font-size:10px;color:var(--ink-4);margin-top:6px">↳ narrativa Anti-BS · {hoje.strftime("%H:%M")}</div>
</div>
"""

hero_mid = f"""
{kicker(f"{mes_nome[:3]} · até hoje")}
<div class="k-grid k-cols-2" style="margin-top:8px;gap:14px">
  <div class="k-metric">
<span class="k-metric-l">Entradas</span>
<span class="k-metric-v pos" style="font-size:22px">{fmt_brl(saldo.total_ganhos, compact=True)}</span>
  </div>
  <div class="k-metric">
<span class="k-metric-l">Saídas</span>
<span class="k-metric-v" style="font-size:22px">{fmt_brl(saldo.total_gastos, compact=True)}</span>
  </div>
</div>
<div style="margin-top:14px">
  <div style="height:8px;border-radius:var(--radius-pill);overflow:hidden;
background:var(--surface-2);border:1px solid var(--rule)">
<div style="height:100%;width:{min(saldo.taxa_poupanca, 100):.0f}%;
  background:linear-gradient(90deg,var(--sea),var(--moss));border-radius:var(--radius-pill)"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:10px;
font-family:var(--font-sans);color:var(--ink-4)">
<span>poupança atual</span>
<span class="mono {'pos' if saldo.taxa_poupanca >= 20 else 'neg'}">{fmt_pct(saldo.taxa_poupanca)}</span>
  </div>
</div>
"""

score_color = "#10B981" if score.total >= 80 else "#F59E0B" if score.total >= 60 else "#D87C6A"

hero_right = f"""
{kicker("Comportamento · score")}
<div style="display:flex;align-items:center;gap:14px;margin-top:8px">
  <div style="position:relative;width:56px;height:56px;flex-shrink:0">
<svg viewBox="0 0 56 56" style="width:56px;height:56px">
  <circle cx="28" cy="28" r="24" fill="none" stroke="var(--rule)" stroke-width="3"/>
  <circle cx="28" cy="28" r="24" fill="none" stroke="{score_color}" stroke-width="3"
    stroke-dasharray="{score.total / 100 * 150.8:.1f} 150.8"
    stroke-linecap="round" transform="rotate(-90 28 28)"/>
</svg>
<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-family:var(--font-serif);font-size:18px;color:{score_color}">{score.total}</div>
  </div>
  <div style="min-width:0;flex:1">
<div style="font-family:var(--font-sans);font-size:13px;color:var(--ink);font-weight:500;line-height:1.3">
  {"Excelente" if score.total >= 80 else "Bom" if score.total >= 60 else "Atenção" if score.total >= 40 else "Crítico"} — score financeiro
</div>
<div class="muted" style="font-size:11px;margin-top:4px">Meta: 80+ pts · {score.total}/100</div>
  </div>
</div>
<div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--rule);
  display:grid;grid-template-columns:1fr 1fr;gap:10px">
  <div>
<div class="muted" style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;font-weight:600">poupança</div>
<div class="serif {'pos' if score.atingiu_meta_poupanca else 'neg'}" style="font-size:16px"
  >{"✓ meta" if score.atingiu_meta_poupanca else "✗ abaixo"}</div>
  </div>
  <div>
<div class="muted" style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;font-weight:600">caixa M2</div>
<div class="serif {'pos' if score.caixa_m2_ok else 'neg'}" style="font-size:16px"
  >{"✓ ok" if score.caixa_m2_ok else "✗ baixo"}</div>
  </div>
</div>
"""

col1, col2, col3 = st.columns([1.4, 1, 1])
with col1:
    st.markdown(f'<div class="k-card gilt"><div class="k-card-b">{hero_left}</div></div>',
                unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="k-card"><div class="k-card-b">{hero_mid}</div></div>',
                unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="k-card"><div class="k-card-b">{hero_right}</div></div>',
                unsafe_allow_html=True)

# ── Charts row — donut + bar mensal ──────────────────────────────────────────
_PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#A89F8C", size=10, family="ui-monospace,monospace"),
    margin=dict(l=0, r=0, t=28, b=0),
)
_chart_col_left, _chart_col_right = st.columns([1.2, 1])

with _chart_col_left:
    _dados_bar = preparar_dados_barras_mensais(_historico_6m)
    # inclui o mês atual
    _dados_bar.append({
        "mes": f"{['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'][mes-1]}/{str(ano)[-2:]}",
        "Entradas": float(saldo.total_ganhos),
        "Saídas": float(saldo.total_gastos),
    })
    if _dados_bar:
        _fig_bar = px.bar(
            _dados_bar, x="mes", y=["Entradas", "Saídas"],
            barmode="group",
            color_discrete_map={"Entradas": "#7BC68A", "Saídas": "#D87C6A"},
            title="Entradas × Saídas — 6 meses",
        )
        _fig_bar.update_traces(hovertemplate="R$ %{y:,.2f}<extra></extra>")
        _fig_bar.update_layout(
            **_PLOTLY_BASE,
            title_font=dict(size=11, color="#7B8B96"),
            title_x=0,
            xaxis=dict(showgrid=False, tickfont=dict(color="#7B8B96", size=9)),
            yaxis=dict(
                showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                tickprefix="R$ ", tickfont=dict(color="#7B8B96", size=9),
                zeroline=False,
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                font=dict(color="#7B8B96", size=9),
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(_fig_bar, use_container_width=True, config={"displayModeBar": False})

with _chart_col_right:
    _dados_donut = preparar_dados_donut_categorias(transacoes)
    if _dados_donut:
        from core.styles import CAT_COLORS
        _color_map = {cat: cor for cat, (cor, _) in CAT_COLORS.items()}
        _fig_donut = px.pie(
            _dados_donut, values="total", names="categoria",
            hole=0.62,
            color="categoria",
            color_discrete_map=_color_map,
            title="Gastos por categoria",
        )
        _fig_donut.update_traces(
            textposition="inside",
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>",
            textfont_size=9,
        )
        _total_gastos_donut = sum(d["total"] for d in _dados_donut)
        _fig_donut.update_layout(
            **_PLOTLY_BASE,
            title_font=dict(size=11, color="#7B8B96"),
            title_x=0,
            showlegend=True,
            legend=dict(
                font=dict(color="#7B8B96", size=9),
                bgcolor="rgba(0,0,0,0)",
                orientation="v",
                yanchor="middle", y=0.5,
                xanchor="left", x=1.0,
            ),
            annotations=[dict(
                text=f"<b>{fmt_brl(_total_gastos_donut, compact=True)}</b>",
                x=0.5, y=0.5, font_size=13, showarrow=False,
                font_color="#E8DEC8",
            )],
        )
        st.plotly_chart(_fig_donut, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown(
            '<div style="height:200px;display:flex;align-items:center;justify-content:center;'
            'font-family:var(--font-sans);font-size:12px;color:var(--ink-4)">'
            'Sem gastos no período</div>',
            unsafe_allow_html=True,
        )

# ── Sparkline score histórico ──────────────────────────────────────────────────
_spark_regs = list(_historico_6m) + [(ano, mes, saldo.total_ganhos, saldo.total_gastos)]
_spark_data  = preparar_sparkline_score_historico(_spark_regs)
if _spark_data:
    _fig_spark = go.Figure(go.Scatter(
        x=[d["mes"] for d in _spark_data],
        y=[d["score"] for d in _spark_data],
        mode="lines+markers",
        line=dict(color="#D9A74A", width=2),
        marker=dict(color="#D9A74A", size=5),
        fill="tozeroy",
        fillcolor="rgba(217,167,74,0.08)",
        hovertemplate="%{x}<br>Score: %{y}<extra></extra>",
    ))
    _fig_spark.update_layout(
        height=110,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=16, b=0),
        title=dict(
            text="Score financeiro — 7 meses",
            font=dict(size=11, color="#7B8B96"),
            x=0,
        ),
        xaxis=dict(showgrid=False, tickfont=dict(color="#7B8B96", size=9)),
        yaxis=dict(
            range=[0, 105],
            showgrid=True, gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(color="#7B8B96", size=9),
            zeroline=False,
        ),
        font=dict(color="#A89F8C", size=10, family="ui-monospace,monospace"),
    )
    st.plotly_chart(_fig_spark, use_container_width=True, config={"displayModeBar": False})

# ── Main grid — feed + rail ────────────────────────────────────────────────────
st.markdown(section_header("Feed financeiro", "ao vivo · todos os fluxos"), unsafe_allow_html=True)

col_feed, col_rail = st.columns([1.7, 1])

with col_feed:
    if not transacoes:
        st.markdown(
            k_premium_empty_state(
                "⊕",
                "Sem transações no período",
                "Lance a primeira transação usando ⚡ Lançar rápido na página Movimento.",
            ),
            unsafe_allow_html=True,
        )
    else:
        by_date: dict = defaultdict(list)
        for t in transacoes[:40]:
            by_date[t.date].append(t)

        feed_html = '<div class="k-feed">'
        for d, txs in sorted(by_date.items(), reverse=True):
            d_label = "hoje" if d == hoje else "ontem" if (hoje - d).days == 1 else d.strftime("%d/%m")
            net = sum((t.amount if t.type == TransactionType.GANHO else -t.amount) for t in txs)
            net_str = fmt_brl(net, compact=True)
            net_cls = "pos" if net >= 0 else "neg"
            feed_html += f"""<div class="k-feed-day">
  <div class="k-feed-day-h">{d_label}
<span class="sub">{len(txs)} lançamento{"s" if len(txs) > 1 else ""}</span>
<span class="sub mono {net_cls}">{net_str}</span>
  </div>
  <div class="k-feed-list">"""
            for t in txs:
                is_in    = t.type == TransactionType.GANHO
                is_inv   = t.category.value == "Investimento"
                val_cls  = "pos" if is_in else "invest" if is_inv else ""
                val_sign = "+" if is_in else "−"
                cat      = "Renda" if is_in else t.category.value
                title    = html.escape(t.notes[:42]) if t.notes else t.category.value
                pm       = t.payment_method.value.lower().replace("_", " ")
                meta     = f"{t.category.value} · {pm}"
                feed_html += tx_row(
                    category=cat,
                    name=title,
                    date_str=d_label,
                    subcategory=meta,
                    amount=f"{val_sign} {fmt_brl(t.amount, compact=True)}",
                    tone="pos" if is_in else "neg",
                )
            feed_html += "</div></div>"
        feed_html += "</div>"
        st.markdown(f'<div class="k-card"><div class="k-card-b">{feed_html}</div></div>',
                    unsafe_allow_html=True)

with col_rail:
    top_cat = calcular_top_categorias(transacoes)
    insights = []
    if top_cat:
        biggest = top_cat[0]
        insights.append(("▲", "neg", biggest.category,
                         f"{fmt_brl(biggest.total)} · {biggest.percentual:.0f}% dos gastos"))
    if score.atingiu_meta_poupanca:
        insights.append(("✓", "pos", "Poupança em dia", f"{saldo.taxa_poupanca:.1f}% · meta ≥ 20%"))
    if violations > 0:
        insights.append(("!", "neg", "M2 alerta", f"{violations} violação{'ões' if violations > 1 else ''} detectada(s)"))
    if alertas_pad:
        a = alertas_pad[0]
        insights.append(("↑", "warn", f"{a.category} acima da média",
                         f"{fmt_brl(a.gasto_atual)} vs média {fmt_brl(a.media_3m)}"))
    if not insights:
        insights.append(("◉", "pos", "Tudo dentro do esperado", "Sem alertas no período"))

    brief_rows = f"""<div class="k-decision-brief">
  <div class="k-brief-item"><div class="k-brief-dot"></div><div>
<div class="k-brief-title">Disciplina operacional</div>
<div class="k-brief-copy">{_brief_main}</div>
  </div></div>
  <div class="k-brief-item"><div class="k-brief-dot"></div><div>
<div class="k-brief-title">Comportamento de gastos</div>
<div class="k-brief-copy">{_brief_budget}</div>
  </div></div>
  <div class="k-brief-item"><div class="k-brief-dot"></div><div>
<div class="k-brief-title">Compromissos futuros</div>
<div class="k-brief-copy">{_brief_commitment}</div>
  </div></div>
</div>"""

    st.markdown(k_card_with_header(
        "Decision brief",
        brief_rows,
        hint="contexto antes de ação",
        gilt=True,
    ), unsafe_allow_html=True)

    ins_rows = ""
    for icon, tone, title, body in insights[:4]:
        color = {"pos": "var(--moss)", "neg": "var(--rust)", "warn": "var(--lantern)"}.get(tone, "var(--sea)")
        bg    = {"pos": "rgba(123,198,138,0.08)", "neg": "rgba(216,124,106,0.08)",
                 "warn": "rgba(244,213,141,0.08)"}.get(tone, "rgba(127,179,200,0.08)")
        ins_rows += f"""<div style="display:grid;grid-template-columns:24px 1fr;gap:10px;align-items:flex-start">
  <div style="width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;
font-family:var(--font-mono);font-size:13px;font-weight:600;color:{color};background:{bg};border:1px solid {color}">
{icon}</div>
  <div>
<div style="font-family:var(--font-sans);font-size:12.5px;color:var(--ink);font-weight:500;line-height:1.3">{title}</div>
<div class="serif" style="font-size:12px;font-style:italic;color:var(--ink-3);margin-top:3px;line-height:1.45">{body}</div>
  </div>
</div>"""

    st.markdown(k_card_with_header(
        "Sinais", f'<div style="display:flex;flex-direction:column;gap:12px;margin-top:6px">{ins_rows}</div>',
        hint="anomalias e disciplina",
    ), unsafe_allow_html=True)

    # ── Accounts rail (Simplifi-style) ────────────────────────────────────────
    _HEX_RE = re.compile(r"^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?$")

    def _dot(color: str, fb: str = "var(--brass)") -> str:
        return color if _HEX_RE.match(color or "") else fb

    acc_rows = ""
    saldo_total_contas = Decimal(0)
    for c in contas:
        bal_color = "var(--moss)" if c.balance >= 0 else "var(--rust)"
        acc_rows += (
            f'<div class="k-acc-row">'
            f'<div class="k-acc-dot" style="background:{_dot(c.color)}"></div>'
            f'<div style="flex:1;min-width:0">'
            f'<div class="k-acc-name">{html.escape(c.name)}</div>'
            f'<div class="k-acc-sub">{html.escape(c.bank or "")} · {c.type.value}</div>'
            f'</div>'
            f'<div class="k-acc-val" style="color:{bal_color}">{fmt_brl(c.balance, compact=True)}</div>'
            f'</div>'
        )
        saldo_total_contas += c.balance

    card_rows = ""
    for cd in cartoes:
        fatura = cd.fatura_atual([t for t in transacoes if t.card_id == cd.id])
        disponivel_card = max(cd.limit_total - fatura, 0)
        pct = (fatura / cd.limit_total * 100) if cd.limit_total > 0 else 0
        pct_color = "var(--rust)" if pct >= 80 else "var(--lantern)" if pct >= 50 else "var(--ink-3)"
        card_rows += (
            f'<div class="k-acc-row">'
            f'<div class="k-acc-dot" style="background:{_dot(cd.color, "var(--sea)")}"></div>'
            f'<div style="flex:1;min-width:0">'
            f'<div class="k-acc-name">{html.escape(cd.name)}</div>'
            f'<div class="k-acc-sub">fatura {fmt_brl(fatura, compact=True)} · vence dia {cd.due_day}</div>'
            f'</div>'
            f'<div class="k-acc-val" style="color:{pct_color}">{fmt_brl(disponivel_card, compact=True)}</div>'
            f'</div>'
        )

    all_rows = acc_rows + card_rows
    patrimonio_total = total_portfolio + saldo_total_contas
    if all_rows:
        acc_content = (
            f'<div style="margin-top:4px">{all_rows}</div>'
            f'<div style="margin-top:10px;padding-top:10px;border-top:1px solid var(--rule);'
            f'display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-size:10px;color:var(--ink-4);font-family:var(--font-sans);'
            f'letter-spacing:0.1em;text-transform:uppercase">Patrimônio total</span>'
            f'<span class="mono" style="font-size:14px;color:var(--brass)">{fmt_brl(patrimonio_total, compact=True)}</span>'
            f'</div>'
        )
    else:
        acc_content = (
            f'<div class="mono" style="font-size:26px;color:var(--ink);font-variant-numeric:tabular-nums">'
            f'{fmt_brl(patrimonio_total, compact=True)}</div>'
            f'<div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">'
            f'{chip(f"FII {fmt_brl(total_portfolio, compact=True)}", "brass")}'
            f'{chip(f"Caixa {caixa_pct:.0f}%", "pos" if caixa_pct >= 20 else "neg")}'
            f'</div>'
        )

    st.markdown(k_card_with_header(
        "Contas & Cartões", acc_content,
        hint="saldo disponível →",
    ), unsafe_allow_html=True)

    if installments:
        comp_map = calcular_comprometimento_mensal(installments)
        next_months = sorted(comp_map.keys())[:3]
        if next_months:
            rows_parc = ""
            for mk in next_months:
                rows_parc += f"""<div style="display:flex;justify-content:space-between;padding:8px 0;
                  border-top:1px solid var(--rule)">
                  <span class="mono muted" style="font-size:11px">{mk}</span>
                  <span class="mono brass-c" style="font-size:13px">{fmt_brl(comp_map[mk])}</span>
                </div>"""
            st.markdown(k_card_with_header(
                "Comprometimento futuro",
                f'<div style="margin-top:4px">{rows_parc}</div>',
                hint="parcelas ativas",
            ), unsafe_allow_html=True)

    # ── Kira · Briefing IA ────────────────────────────────────────────────────
    briefing_key = f"kira_briefing_{ano}_{mes}"
    if briefing_key not in st.session_state:
        st.session_state[briefing_key] = None

    briefing_text: str | None = st.session_state[briefing_key]

    briefing_inner = ""
    if briefing_text:
        import html as _html_br
        briefing_inner = (
            f'<div class="k-kira-bubble" style="margin-top:6px">'
            f'{_html_br.escape(briefing_text)}'
            f'</div>'
        )
    else:
        briefing_inner = (
            '<div style="font-family:var(--font-sans);font-size:12px;'
            'color:var(--ink-4);font-style:italic;padding:8px 0">'
            'Clique em "Gerar" para o briefing do dia.</div>'
        )

    st.markdown(k_card_with_header(
        "Kira · Briefing",
        f'<div class="k-kira-header" style="padding:0 0 8px">'
        f'<div class="k-kira-dot"></div>'
        f'<span class="k-kira-label">IA Financeira · NVIDIA NIM</span>'
        f'</div>{briefing_inner}',
        hint="análise do mês gerada por IA",
        gilt=True,
    ), unsafe_allow_html=True)

    if st.button("Gerar briefing", use_container_width=True, key="btn_kira_briefing"):
        try:
            from core.financial_ai import auto_briefing
            with st.spinner("Kira está analisando seus dados…"):
                result = auto_briefing(_ai_ctx)
            st.session_state[briefing_key] = result
            st.rerun()
        except RuntimeError as e:
            st.warning(f"Kira indisponível: {e}")
        except Exception:
            st.error("Erro ao gerar briefing. Configure NVIDIA_API_KEY.")
