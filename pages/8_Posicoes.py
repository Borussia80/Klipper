"""Posições · Klipper — tabela de mercado ao vivo."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from core.fragility import calcular_fragility_score, reduzir_exposicao_por_fragilidade
from core.m1_quant import calcular_score_m1, classificar_score, Decisao
from core.m2_governance import verificar_limites, hard_fail
from core.m3_context import Confidence, MarketRegime, ajustar_prudencia
from core.repositories import InvestmentRepository
from core.auth import require_auth
from core.styles import (
    bar_track, fmt_brl, inject_css, k_card_with_header, section_header,
    sidebar_engines, sidebar_user, sidebar_ai_qa, render_navigation, stat_card, chip, load_page_icon,
    setup_sidebar,
)

st.set_page_config(page_title="Posições · Klipper", page_icon=load_page_icon(), layout="wide", initial_sidebar_state="collapsed")
inject_css()
require_auth()

repo = InvestmentRepository()

# ── Layout ────────────────────────────────────────────────────────────────────

setup_sidebar()

# ── M3 Context controls inline ────────────────────────────────────────────
m3c1, m3c2, m3c3 = st.columns([2, 2, 2])
with m3c1:
    regime = MarketRegime(
        st.selectbox("Regime M3", [r.value for r in MarketRegime], index=0,
                     label_visibility="collapsed")
    )
with m3c2:
    confidence = Confidence(
        st.selectbox("Confidence", [c.value for c in Confidence], index=2,
                     label_visibility="collapsed")
    )
with m3c3:
    caixa_disponivel = st.number_input(
        "Caixa (R$)", min_value=0.0, step=100.0, value=0.0,
        label_visibility="collapsed",
    )

# ── Load data ─────────────────────────────────────────────────────────────
try:
    portfolio = repo.get_portfolio()
except Exception as e:
    st.error(f"Erro ao carregar portfólio: {e}")
    st.stop()

st.markdown(section_header("Posições", "tabela de mercado · portfólio completo"), unsafe_allow_html=True)

if not portfolio:
    st.markdown(
        '<div style="padding:64px 0;text-align:center;color:var(--ink-4)">'
        'portfólio vazio · adicione ativos em Patrimônio</div>',
        unsafe_allow_html=True,
    )
    st.stop()

total_portfolio = sum(inv.current_value for inv in portfolio)
total_gl        = sum(inv.gain_loss for inv in portfolio)
total_cost      = sum(inv.quantity * inv.avg_price for inv in portfolio)
gl_pct          = (total_gl / total_cost * 100) if total_cost > 0 else 0.0

alertas_m2       = verificar_limites(portfolio, float(caixa_disponivel))
violations       = len([a for a in alertas_m2 if a.severity == "CRITICAL"])

# ── KPI strip ─────────────────────────────────────────────────────────────
gl_tone = "pos" if total_gl >= 0 else "neg"
avg_dy  = sum(inv.dy_12m for inv in portfolio) / len(portfolio) if portfolio else 0.0
avg_vol = sum(inv.volatility for inv in portfolio) / len(portfolio) if portfolio else 0.0

st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:22px">
  {stat_card("Valor de mercado", fmt_brl(total_portfolio, compact=True),
         f"{len(portfolio)} ativos")}
  {stat_card("P&L total", fmt_brl(total_gl, compact=True),
         f"{gl_pct:+.2f}% sobre custo", gl_tone)}
  {stat_card("DY médio 12m", f"{avg_dy:.1f}%",
         "dividend yield ponderado")}
  {stat_card("Volatilidade média", f"{avg_vol:.1f}%",
         f"{violations} violações M2", "neg" if violations else "pos")}
</div>
""", unsafe_allow_html=True)

# ── Positions table ────────────────────────────────────────────────────────
_DECISAO_TONE = {
    Decisao.COMPRAR: "pos",
    Decisao.MANTER:  "brass",
    Decisao.REDUZIR: "neg",
}

rows_html = ""
for inv in sorted(portfolio, key=lambda x: -x.current_value):
    peso_pct   = (inv.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
    score_m1   = calcular_score_m1(
        dy=inv.dy_12m, pvp=inv.pvp, liquidez=inv.liquidity_daily,
        volatilidade=inv.volatility, spread_cdi=inv.spread_vs_cdi,
    )
    score_adj  = ajustar_prudencia(score_m1, regime, confidence)
    fragility  = calcular_fragility_score(inv, peso_portfolio_pct=peso_pct)
    score_fin  = reduzir_exposicao_por_fragilidade(score_adj, fragility.total)
    decisao    = classificar_score(score_fin)
    dec_tone   = _DECISAO_TONE.get(decisao, "")
    gl_c       = "var(--moss)" if inv.gain_loss >= 0 else "var(--rust)"
    gl_sign    = "+" if inv.gain_loss >= 0 else ""
    frag_c     = "var(--rust)" if fragility.total > 0.65 else "var(--lantern)" if fragility.total > 0.40 else "var(--moss)"

    rows_html += f"""<div style="display:grid;
  grid-template-columns:80px 64px 70px 110px 110px 120px 120px 72px 80px 64px;
  gap:0;align-items:center;padding:10px 18px;border-top:1px solid var(--rule);
  font-family:var(--font-mono);font-size:11.5px;transition:background 140ms">
  <span style="color:var(--ink);font-weight:600;font-family:var(--font-sans)">{inv.ticker}</span>
  <span style="color:var(--ink-3);font-family:var(--font-sans);font-size:11px">{inv.type.value}</span>
  <span class="muted">{inv.quantity:.0f}</span>
  <span class="muted">{fmt_brl(inv.avg_price)}</span>
  <span style="color:var(--ink)">{fmt_brl(inv.current_price)}</span>
  <span style="color:var(--ink);font-weight:500">{fmt_brl(inv.current_value, compact=True)}</span>
  <span style="color:{gl_c}">{gl_sign}{fmt_brl(inv.gain_loss, compact=True)} ({inv.gain_loss_pct:+.1f}%)</span>
  <span style="color:var(--ink-2)">{inv.dy_12m:.1f}%</span>
  <span style="color:{frag_c}">{fragility.total:.2f}</span>
  <span>{chip(decisao.value, dec_tone)}</span>
</div>"""

header_html = """<div style="display:grid;
  grid-template-columns:80px 64px 70px 110px 110px 120px 120px 72px 80px 64px;
  gap:0;padding:10px 18px 8px;
  font-family:var(--font-sans);font-size:9.5px;letter-spacing:0.14em;
  text-transform:uppercase;color:var(--ink-4);font-weight:600;
  border-bottom:1px solid var(--rule-2)">
  <span>Ativo</span><span>Classe</span><span>Qtd</span>
  <span>PM (R$)</span><span>Atual (R$)</span><span>Valor</span>
  <span>P&amp;L</span><span>DY 12m</span><span>Frag.</span><span>M1</span>
</div>"""

st.markdown(
    k_card_with_header(
        "Tabela de posições",
        header_html + rows_html,
        hint=f"{len(portfolio)} ativos · ordenado por valor de mercado",
        gilt=False,
    ),
    unsafe_allow_html=True,
)

# ── Per-asset detail bar chart ─────────────────────────────────────────────
st.markdown(section_header("Alocação por ativo", "peso % no portfólio"), unsafe_allow_html=True)

alloc_rows = ""
for inv in sorted(portfolio, key=lambda x: -x.current_value):
    peso = (inv.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
    alloc_rows += f"""<div style="margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;
font-family:var(--font-sans);font-size:12px;margin-bottom:5px">
<span style="color:var(--ink)">{inv.ticker}
  <span class="mono muted" style="font-size:10px;margin-left:8px">{inv.type.value}</span>
</span>
<span class="mono" style="color:var(--brass)">{peso:.1f}%
  <span class="muted" style="font-size:10px;margin-left:6px">{fmt_brl(inv.current_value, compact=True)}</span>
</span>
  </div>
  {bar_track(peso, 100)}
</div>"""

st.markdown(
    k_card_with_header("Alocação", alloc_rows, hint="peso sobre valor de mercado total"),
    unsafe_allow_html=True,
)
