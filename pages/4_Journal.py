"""Decision Journal · Klipper — Decision Template auditável."""

from __future__ import annotations

from datetime import date

import streamlit as st

from core.formatters import formatar_data_br
from core.repositories import DecisionRepository, InvestmentRepository
from core.auth import require_auth
from core.styles import (
    inject_css, fmt_brl, k_card_with_header, section_header,
    sidebar_brand, sidebar_engines, sidebar_user, stat_card, chip,
    load_page_icon,
)
from models.decision import DecisionOutcome, DecisionRecord

st.set_page_config(page_title="Journal · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

repo     = DecisionRepository()
inv_repo = InvestmentRepository()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_brand(), unsafe_allow_html=True)
    st.markdown(sidebar_engines(), unsafe_allow_html=True)
    sidebar_user()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(section_header("Journal", "decision template · auditável"), unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────────
try:
    all_decisions = repo.list_all()
except Exception:
    all_decisions = []

n_comprar = sum(1 for d in all_decisions if d.outcome and d.outcome.value == "COMPRAR")
n_manter  = sum(1 for d in all_decisions if d.outcome and d.outcome.value == "MANTER")
n_reduzir = sum(1 for d in all_decisions if d.outcome and d.outcome.value in ("REDUZIR", "VENDER"))
n_total   = len(all_decisions)

st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:22px">
  {stat_card("Decisões registradas", str(n_total), "histórico completo")}
  {stat_card("Comprar", str(n_comprar), f"{n_comprar/n_total*100:.0f}% do total" if n_total else "—", "pos")}
  {stat_card("Manter", str(n_manter), f"{n_manter/n_total*100:.0f}% do total" if n_total else "—", "brass")}
  {stat_card("Reduzir / Vender", str(n_reduzir), f"{n_reduzir/n_total*100:.0f}% do total" if n_total else "—", "neg")}
</div>
""", unsafe_allow_html=True)

tab_novo, tab_hist = st.tabs(["Nova Decisão", "Histórico"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Nova Decisão
# ══════════════════════════════════════════════════════════════════════════════
with tab_novo:
    portfolio = inv_repo.get_portfolio()
    tickers = [inv.ticker for inv in portfolio] + ["(outro)"]

    with st.form("form_decision", clear_on_submit=True):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(
                '<div class="k-kicker" style="margin-bottom:8px">Ativo & decisão</div>',
                unsafe_allow_html=True,
            )
            ticker = st.selectbox("Ativo", tickers)
            if ticker == "(outro)":
                ticker = st.text_input("Ticker manual").upper()
            outcome = st.selectbox("Decisão", [o.value for o in DecisionOutcome])
            invalidation = st.text_input("Condição de saída / invalidação")

        with col2:
            st.markdown(
                '<div class="k-kicker" style="margin-bottom:8px">Scores WikiAgent</div>',
                unsafe_allow_html=True,
            )
            score_m1 = st.number_input("Score M1", 0.0, 1.0, step=0.01, format="%.4f")
            regime = st.text_input("Regime M3")
            confidence = st.text_input("Confidence M3")
            fragility = st.number_input("Fragility Score", 0.0, 1.0, step=0.01, format="%.4f")

        st.markdown(
            '<div class="k-kicker" style="margin-top:16px;margin-bottom:8px">Antes da compra</div>',
            unsafe_allow_html=True,
        )
        thesis     = st.text_area("Tese de investimento", height=80)
        risk       = st.text_area("Riscos identificados", height=60)
        inv_cond   = st.text_area("Cenário de invalidação", height=60)
        expectation = st.text_area("Expectativa", height=60)
        alt_scenario = st.text_area("Cenário alternativo", height=60)

        st.markdown(
            '<div class="k-kicker" style="margin-top:16px;margin-bottom:8px">Depois · preencher após resultado</div>',
            unsafe_allow_html=True,
        )
        result   = st.text_area("Resultado", height=60)
        error    = st.text_area("Erro cometido", height=60)
        learning = st.text_area("Aprendizado", height=60)
        bias     = st.text_area("Viés identificado", height=60)

        submitted = st.form_submit_button("Salvar decisão", type="primary", use_container_width=True)

    if submitted:
        if not ticker:
            st.error("Ticker obrigatório.")
        else:
            try:
                rec = DecisionRecord(
                    ticker=ticker,
                    outcome=DecisionOutcome(outcome),
                    score_m1=score_m1,
                    regime=regime,
                    confidence=confidence,
                    fragility=fragility,
                    invalidation_condition=invalidation,
                    thesis=thesis,
                    risk=risk,
                    alternative_scenario=alt_scenario,
                    expectation=expectation,
                    result=result,
                    error=error,
                    learning=learning,
                    bias_identified=bias,
                )
                repo.create(rec)
                st.success(f"Decision Record salvo: {ticker} — {outcome}")
            except Exception as e:
                st.error(f"Erro: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Histórico
# ══════════════════════════════════════════════════════════════════════════════
with tab_hist:
    try:
        decisions = repo.list_all()
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        st.stop()

    if not decisions:
        st.markdown(
            '<div style="padding:48px 0;text-align:center;color:var(--ink-4)">nenhuma decisão registrada ainda</div>',
            unsafe_allow_html=True,
        )
    else:
        ticker_fil = st.selectbox(
            "Filtrar por ativo",
            ["Todos"] + sorted({d.ticker for d in decisions}),
        )
        if ticker_fil != "Todos":
            decisions = [d for d in decisions if d.ticker == ticker_fil]

        _OUTCOME_TONE = {
            "COMPRAR": ("pos", "↗"),
            "MANTER":  ("brass", "→"),
            "REDUZIR": ("warn", "↘"),
            "VENDER":  ("neg", "↓"),
        }

        for dec in decisions:
            ov    = dec.outcome.value if dec.outcome else "N/A"
            tone, arrow = _OUTCOME_TONE.get(ov, ("", "·"))
            chip_html = chip(f"{arrow} {ov}", tone)
            date_str  = formatar_data_br(dec.date)

            scores = (
                f'<div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:10px">'
                f'<span class="mono muted" style="font-size:11px">M1 · {dec.score_m1:.4f}</span>'
                f'<span class="mono muted" style="font-size:11px">Regime · {dec.regime or "—"}</span>'
                f'<span class="mono muted" style="font-size:11px">Fragility · {dec.fragility:.4f}</span>'
                f'</div>'
            )

            thesis_html = (
                f'<div class="serif" style="font-style:italic;font-size:13px;color:var(--ink-2);'
                f'line-height:1.5;margin-top:12px;padding-top:12px;border-top:1px solid var(--rule)">'
                f'&#8220;{dec.thesis}&#8221;</div>'
            ) if dec.thesis else ""

            result_html = ""
            if dec.result:
                result_html = (
                    f'<div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--rule)">'
                    f'<div class="k-kicker">resultado</div>'
                    f'<div style="font-family:var(--font-sans);font-size:12.5px;color:var(--ink-2);'
                    f'line-height:1.55;margin-top:6px">{dec.result}</div>'
                    f'</div>'
                )

            body = f'{scores}{thesis_html}{result_html}'

            with st.expander(f"{dec.ticker}  ·  {date_str}  ·  {ov}"):
                st.markdown(
                    k_card_with_header(
                        f"{dec.ticker}",
                        body,
                        hint=f"{date_str} · {dec.regime or '—'}",
                    ),
                    unsafe_allow_html=True,
                )
