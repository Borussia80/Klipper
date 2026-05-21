"""Dashboard — Visão executiva mensal premium."""

from __future__ import annotations

import calendar
from datetime import date

import plotly.express as px
import streamlit as st

from core.analytics import calcular_saldo_mensal, calcular_top_categorias
from core.behavioral import calcular_score_financeiro, calcular_uso_orcamento, detectar_alertas_padrao
from core.installment_engine import calcular_comprometimento_mensal
from core.m2_governance import CAIXA_MIN_PCT
from core.repositories import (
    InvestmentRepository, TransactionRepository,
    InstallmentRepository, BudgetRepository,
)
from core.styles import inject_css, metric_card, budget_bar, score_circle, fmt_brl, payment_badge

st.set_page_config(page_title="Dashboard · Klipper", page_icon="📊", layout="wide")
inject_css()

# ── Período ──────────────────────────────────────────────────────────────────
hoje = date.today()
c_ano, c_mes, _ = st.columns([1, 1, 4])
with c_ano:
    ano = int(st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1), index=0))
with c_mes:
    mes = int(st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                           format_func=lambda m: calendar.month_abbr[m]))

# ── Carregar dados ────────────────────────────────────────────────────────────
tx_repo   = TransactionRepository()
inv_repo  = InvestmentRepository()
inst_repo = InstallmentRepository()
bud_repo  = BudgetRepository()

with st.spinner("Carregando..."):
    try:
        transacoes   = tx_repo.list_by_month(ano, mes)
        portfolio    = inv_repo.get_portfolio()
        installments = inst_repo.list_active()
        budgets      = bud_repo.list_by_month(ano, mes)
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        st.stop()

# Meses anteriores para média comportamental
transacoes_3m: list = []
for delta in range(1, 4):
    m_prev = mes - delta
    y_prev = ano
    while m_prev < 1:
        m_prev += 12
        y_prev -= 1
    try:
        transacoes_3m.extend(tx_repo.list_by_month(y_prev, m_prev))
    except Exception:
        pass

saldo          = calcular_saldo_mensal(transacoes, ano, mes)
total_portfolio = sum(inv.current_value for inv in portfolio)
parcelas_mes   = sum(calcular_comprometimento_mensal(installments).get(f"{ano}-{mes:02d}", 0.0) for _ in [1])
parcelas_mes   = calcular_comprometimento_mensal(installments).get(f"{ano}-{mes:02d}", 0.0)

total_ativos   = saldo.total_ganhos + total_portfolio
caixa_pct      = (saldo.saldo / total_ativos * 100) if total_ativos > 0 else 0.0

score = calcular_score_financeiro(
    transacoes=transacoes,
    budgets=budgets,
    installments=installments,
    taxa_poupanca_atual=saldo.taxa_poupanca,
    meta_poupanca=20.0,
    caixa_pct=caixa_pct,
    transacoes_3_meses=transacoes_3m,
)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Visão Geral</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    metric_card("Ganhos", fmt_brl(saldo.total_ganhos), cor="success")
with k2:
    metric_card("Gastos", fmt_brl(saldo.total_gastos), cor="danger")
with k3:
    saldo_cor = "success" if saldo.saldo >= 0 else "danger"
    metric_card("Saldo", fmt_brl(saldo.saldo),
                subtitulo=f"{saldo.taxa_poupanca:.1f}% poupado", cor=saldo_cor)
with k4:
    metric_card("Portfólio", fmt_brl(total_portfolio), cor="accent")
with k5:
    metric_card("Parcelas/mês", fmt_brl(parcelas_mes), subtitulo="comprometimento")

# ── Alertas M2 + Comportamental ──────────────────────────────────────────────
st.markdown("")
if caixa_pct < CAIXA_MIN_PCT and saldo.total_ganhos > 0:
    st.warning(
        f"**M2 Governance:** Caixa livre {caixa_pct:.1f}% < mínimo {CAIXA_MIN_PCT}%. "
        "Reforce reserva antes de novos aportes."
    )

alertas_pad = detectar_alertas_padrao(transacoes, transacoes_3m) if transacoes_3m else []
for a in alertas_pad:
    st.warning(
        f"**Padrão de Gasto:** {a.category} — {fmt_brl(a.gasto_atual)} "
        f"({a.ratio:.1f}× acima da média de {fmt_brl(a.media_3m)}/mês)"
    )

# ── Gráficos ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Análise</div>', unsafe_allow_html=True)

if not transacoes:
    st.info("Nenhuma transação registrada para este período.")
else:
    col_left, col_right = st.columns([65, 35])

    with col_left:
        st.markdown("**Gastos por categoria**")
        top_cat = calcular_top_categorias(transacoes)

        if budgets and top_cat:
            budget_map = {b.category: b.monthly_limit for b in budgets}
            for cat in top_cat:
                if cat.category in budget_map:
                    budget_bar(cat.category, cat.total, budget_map[cat.category])

        if top_cat:
            fig = px.bar(
                x=[c.total for c in top_cat],
                y=[c.category for c in top_cat],
                orientation="h",
                text=[fmt_brl(c.total) for c in top_cat],
                labels={"x": "R$", "y": ""},
                color=[c.percentual for c in top_cat],
                color_continuous_scale="Blues",
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=280,
                              margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("**Score Financeiro**")
        score_circle(score.total)
        st.markdown("")
        criterios = [
            ("Orçamento", score.detalhes.get("orcamento", 0), 30),
            ("Poupança",  score.detalhes.get("poupanca", 0),  25),
            ("Caixa M2",  score.detalhes.get("caixa", 0),     20),
            ("Padrão",    score.detalhes.get("media", 0),      15),
            ("Parcelas",  score.detalhes.get("parcelas", 0),   10),
        ]
        for label, pts, max_pts in criterios:
            icon = "✅" if pts > 0 else "❌"
            st.caption(f"{icon} {label}: {pts}/{max_pts} pts")

        st.markdown("")
        st.markdown("**Fluxo do mês**")
        fig2 = px.bar(
            x=["Ganhos", "Gastos", "Saldo"],
            y=[saldo.total_ganhos, saldo.total_gastos, max(saldo.saldo, 0)],
            color=["Ganhos", "Gastos", "Saldo"],
            color_discrete_map={"Ganhos": "#10B981", "Gastos": "#EF4444", "Saldo": "#6366F1"},
            text=[fmt_brl(saldo.total_ganhos), fmt_brl(saldo.total_gastos), fmt_brl(saldo.saldo)],
        )
        fig2.update_layout(showlegend=False, height=220, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)

# ── Parcelamentos ativos ───────────────────────────────────────────────────────
if installments:
    st.markdown('<div class="section-title">Comprometimento Futuro</div>', unsafe_allow_html=True)
    comp = calcular_comprometimento_mensal(installments)
    meses_futuros = sorted(comp.keys())[:6]
    if meses_futuros:
        import pandas as pd
        df_comp = pd.DataFrame({
            "Mês": meses_futuros,
            "Parcelas (R$)": [comp[m] for m in meses_futuros],
        })
        fig3 = px.bar(df_comp, x="Mês", y="Parcelas (R$)", text="Parcelas (R$)",
                      color_discrete_sequence=["#6366F1"])
        fig3.update_traces(texttemplate="%{text:,.2f}")
        fig3.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig3, use_container_width=True)

# ── Últimas transações ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Últimas Transações</div>', unsafe_allow_html=True)
if transacoes:
    import pandas as pd
    rows = []
    for t in transacoes[:10]:
        rows.append({
            "Data":       t.date.strftime("%d/%m"),
            "Tipo":       t.type.value,
            "Categoria":  t.category.value,
            "Valor":      fmt_brl(t.amount),
            "Pagamento":  t.payment_method.value,
            "Status":     t.status.value,
            "Notas":      t.notes[:40] if t.notes else "",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.caption("Nenhuma transação no período.")
