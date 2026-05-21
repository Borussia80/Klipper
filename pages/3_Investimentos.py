"""Investimentos — Portfólio + WikiAgent M1/M2/M3/Anti-BS/Fragility."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from core.anti_bs import verificar_alertas, PERGUNTA_OBRIGATORIA
from core.formatters import formatar_moeda_brl, formatar_percentual
from core.fragility import calcular_fragility_score, reduzir_exposicao_por_fragilidade
from core.m1_quant import calcular_score_m1, classificar_score, Decisao
from core.m2_governance import verificar_limites, hard_fail
from core.m3_context import Confidence, MarketRegime, ajustar_prudencia
from core.repositories import InvestmentRepository
from models.investment import Investment, InvestmentType

st.set_page_config(page_title="Investimentos · Klipper", page_icon="📈", layout="wide")
st.title("📈 Investimentos")

repo = InvestmentRepository()

# --- Regime M3 (sidebar) ---
with st.sidebar:
    st.subheader("M3 — Contexto de Mercado")
    regime = MarketRegime(
        st.selectbox("Regime", [r.value for r in MarketRegime], index=0)
    )
    confidence = Confidence(
        st.selectbox("Confidence", [c.value for c in Confidence], index=2)
    )
    caixa_disponivel = st.number_input("Caixa disponível (R$)", min_value=0.0, step=100.0, value=0.0)
    st.caption(f"*Contexto não compra ativo — contexto altera prudência.*")

# --- Adicionar / Atualizar ativo ---
with st.expander("➕ Adicionar / Atualizar ativo"):
    with st.form("form_investimento", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            ticker = st.text_input("Ticker (ex: MXRF11)").upper()
            tipo = st.selectbox("Tipo", [t.value for t in InvestmentType])
            setor = st.text_input("Setor")
        with c2:
            quantidade = st.number_input("Quantidade (cotas)", min_value=0.01, step=1.0)
            preco_medio = st.number_input("Preço médio (R$)", min_value=0.01, step=0.01, format="%.2f")
            preco_atual = st.number_input("Preço atual (R$)", min_value=0.01, step=0.01, format="%.2f")
        with c3:
            dy_12m = st.number_input("DY 12m (%)", min_value=0.0, step=0.1, format="%.2f")
            pvp = st.number_input("P/VP", min_value=0.0, step=0.01, format="%.4f")
            liquidez = st.number_input("Liquidez diária (R$)", min_value=0.0, step=1000.0)

        volatilidade = st.slider("Volatilidade anualizada (%)", 0.0, 60.0, 10.0, 0.5)
        spread_cdi = st.slider("Spread vs CDI (p.p.)", -5.0, 10.0, 2.0, 0.25)
        notas = st.text_area("Notas")

        if st.form_submit_button("Salvar ativo", type="primary", use_container_width=True):
            if not ticker:
                st.error("Ticker obrigatório.")
            else:
                try:
                    inv = Investment(
                        ticker=ticker,
                        type=InvestmentType(tipo),
                        quantity=quantidade,
                        avg_price=preco_medio,
                        current_price=preco_atual,
                        dy_12m=dy_12m,
                        pvp=pvp,
                        liquidity_daily=liquidez,
                        volatility=volatilidade,
                        spread_vs_cdi=spread_cdi,
                        sector=setor,
                        notes=notas,
                    )
                    repo.upsert(inv)
                    st.success(f"{ticker} salvo.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

# --- Carregar portfólio ---
try:
    portfolio = repo.get_portfolio()
except Exception as e:
    st.error(f"Erro ao carregar portfólio: {e}")
    st.stop()

if not portfolio:
    st.info("Portfólio vazio. Adicione seu primeiro ativo acima.")
    st.stop()

total_portfolio = sum(inv.current_value for inv in portfolio)

# --- M2 Governance Check ---
alertas_m2 = verificar_limites(portfolio, float(caixa_disponivel))
has_hard_fail, motivo_fail = hard_fail(alertas_m2)

if has_hard_fail:
    st.error(f"🚨 **M2 Hard Fail:** {motivo_fail}", icon="🚨")
elif alertas_m2:
    for alerta in alertas_m2:
        st.warning(f"⚠️ {alerta.message}")

# --- Tabela de portfólio com scores ---
st.divider()
st.subheader("Portfólio")

rows = []
for inv in portfolio:
    peso_pct = (inv.current_value / total_portfolio * 100) if total_portfolio > 0 else 0

    score_m1 = calcular_score_m1(
        dy=inv.dy_12m,
        pvp=inv.pvp,
        liquidez=inv.liquidity_daily,
        volatilidade=inv.volatility,
        spread_cdi=inv.spread_vs_cdi,
    )
    score_ajustado = ajustar_prudencia(score_m1, regime, confidence)
    fragility = calcular_fragility_score(inv, peso_portfolio_pct=peso_pct)
    score_final = reduzir_exposicao_por_fragilidade(score_ajustado, fragility.total)
    decisao = classificar_score(score_final)

    badge = {"COMPRAR": "🟢", "MANTER": "🟡", "REDUZIR": "🔴"}[decisao.value]

    rows.append({
        "Ticker": inv.ticker,
        "Tipo": inv.type.value,
        "Valor (R$)": formatar_moeda_brl(inv.current_value),
        "Peso %": formatar_percentual(peso_pct),
        "DY 12m": formatar_percentual(inv.dy_12m),
        "P/VP": f"{inv.pvp:.2f}",
        "Score M1": f"{score_m1:.2f}",
        "Ajustado M3": f"{score_ajustado:.2f}",
        "Fragility": f"{fragility.total:.2f}",
        "Score Final": f"{score_final:.2f}",
        "Decisão": f"{badge} {decisao.value}",
        "G/L": formatar_moeda_brl(inv.gain_loss),
        "G/L %": formatar_percentual(inv.gain_loss_pct),
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

# --- Totais ---
total_gl = sum(inv.gain_loss for inv in portfolio)
st.caption(
    f"**{len(portfolio)} ativos** | Total: {formatar_moeda_brl(total_portfolio)} | "
    f"G/L: {formatar_moeda_brl(total_gl)}"
)

# --- Detalhe Anti-BS por ativo ---
st.divider()
st.subheader("Anti-BS — Análise por ativo")
st.caption(f"*{PERGUNTA_OBRIGATORIA}*")

ticker_sel = st.selectbox("Selecione o ativo", [inv.ticker for inv in portfolio])
inv_sel = next(inv for inv in portfolio if inv.ticker == ticker_sel)
peso_sel = (inv_sel.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
alertas_bs = verificar_alertas(inv_sel, peso_sel)

if alertas_bs:
    for alerta in alertas_bs:
        if alerta.severity == "CRITICAL":
            st.error(f"🚨 **{alerta.code}:** {alerta.message}")
        else:
            st.warning(f"⚠️ **{alerta.code}:** {alerta.message}")
else:
    st.success("Nenhum alerta Anti-BS para este ativo.")
