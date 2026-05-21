"""Dashboard — Visão executiva mensal."""

from __future__ import annotations

import calendar
from datetime import date

import plotly.express as px
import streamlit as st

from core.analytics import calcular_saldo_mensal, calcular_top_categorias
from core.formatters import formatar_moeda_brl, formatar_percentual
from core.m2_governance import CAIXA_MIN_PCT
from core.repositories import InvestmentRepository, TransactionRepository

st.set_page_config(page_title="Dashboard · Klipper", page_icon="📊", layout="wide")
st.title("📊 Dashboard")

# --- Seletor de período ---
hoje = date.today()
col_ano, col_mes, _ = st.columns([1, 1, 4])
with col_ano:
    ano = st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1), index=0)
with col_mes:
    mes = st.selectbox(
        "Mês",
        range(1, 13),
        index=hoje.month - 1,
        format_func=lambda m: calendar.month_abbr[m],
    )

# --- Carregar dados ---
tx_repo = TransactionRepository()
inv_repo = InvestmentRepository()

with st.spinner("Carregando..."):
    try:
        transacoes = tx_repo.list_by_month(int(ano), int(mes))
        portfolio = inv_repo.get_portfolio()
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        st.stop()

saldo = calcular_saldo_mensal(transacoes, int(ano), int(mes))
total_portfolio = sum(inv.current_value for inv in portfolio)

# --- KPI Cards ---
st.divider()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Ganhos", formatar_moeda_brl(saldo.total_ganhos))
k2.metric("Gastos", formatar_moeda_brl(saldo.total_gastos))
k3.metric(
    "Saldo",
    formatar_moeda_brl(saldo.saldo),
    delta=formatar_percentual(saldo.taxa_poupanca) + " poupado",
    delta_color="normal",
)
k4.metric("Portfólio", formatar_moeda_brl(total_portfolio))

# --- Alerta M2 Caixa ---
if saldo.total_ganhos > 0:
    caixa_pct = (saldo.saldo / (saldo.total_ganhos + total_portfolio)) * 100 if (saldo.total_ganhos + total_portfolio) > 0 else 0
    if caixa_pct < CAIXA_MIN_PCT:
        st.warning(
            f"⚠️ **M2 Alert:** Caixa livre {caixa_pct:.1f}% < mínimo {CAIXA_MIN_PCT}%. "
            "Reforce reserva antes de novos aportes.",
            icon="⚠️",
        )

st.divider()

# --- Gráficos ---
if not transacoes:
    st.info("Nenhuma transação registrada para este período.")
else:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Gastos por categoria")
        top_cat = calcular_top_categorias(transacoes)
        if top_cat:
            fig = px.bar(
                x=[c.total for c in top_cat],
                y=[c.category for c in top_cat],
                orientation="h",
                text=[formatar_moeda_brl(c.total) for c in top_cat],
                labels={"x": "R$", "y": ""},
                color=[c.percentual for c in top_cat],
                color_continuous_scale="Blues",
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Fluxo do mês")
        fig2 = px.bar(
            x=["Ganhos", "Gastos", "Saldo"],
            y=[saldo.total_ganhos, saldo.total_gastos, saldo.saldo],
            color=["Ganhos", "Gastos", "Saldo"],
            color_discrete_map={"Ganhos": "#22c55e", "Gastos": "#ef4444", "Saldo": "#3b82f6"},
            text=[
                formatar_moeda_brl(saldo.total_ganhos),
                formatar_moeda_brl(saldo.total_gastos),
                formatar_moeda_brl(saldo.saldo),
            ],
        )
        fig2.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig2, use_container_width=True)

# --- Últimas transações ---
st.subheader("Últimas transações")
if transacoes:
    import pandas as pd
    df = pd.DataFrame([
        {
            "Data": t.date.strftime("%d/%m"),
            "Tipo": t.type.value,
            "Categoria": t.category.value,
            "Valor": formatar_moeda_brl(t.amount),
            "Notas": t.notes,
        }
        for t in transacoes[:10]
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.caption("Nenhuma transação no período.")
