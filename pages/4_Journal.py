"""Journal — Decision Template auditável."""

from __future__ import annotations

from datetime import date

import streamlit as st

from core.formatters import formatar_data_br
from core.repositories import DecisionRepository, InvestmentRepository
from models.decision import DecisionOutcome, DecisionRecord

st.set_page_config(page_title="Journal · Klipper", page_icon="📓", layout="wide")
st.title("📓 Investment Journal")
st.caption("Antes da compra · Depois · Decision Template auditável")

repo = DecisionRepository()
inv_repo = InvestmentRepository()

tab_novo, tab_historico = st.tabs(["Nova Decisão", "Histórico"])

with tab_novo:
    portfolio = inv_repo.get_portfolio()
    tickers = [inv.ticker for inv in portfolio] + ["(outro)"]

    with st.form("form_decision"):
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.selectbox("Ativo", tickers)
            if ticker == "(outro)":
                ticker = st.text_input("Ticker manual").upper()
            outcome = st.selectbox("Decisão", [o.value for o in DecisionOutcome])
            invalidation = st.text_input("Condição de saída / invalidação")

        with col2:
            score_m1 = st.number_input("Score M1", 0.0, 1.0, step=0.01, format="%.4f")
            regime = st.text_input("Regime M3")
            confidence = st.text_input("Confidence M3")
            fragility = st.number_input("Fragility Score", 0.0, 1.0, step=0.01, format="%.4f")

        st.subheader("Antes da compra")
        thesis = st.text_area("Tese de investimento", height=80)
        risk = st.text_area("Riscos identificados", height=60)
        invalidation_cond = st.text_area("Cenário de invalidação", height=60)
        expectation = st.text_area("Expectativa", height=60)
        alt_scenario = st.text_area("Cenário alternativo", height=60)

        st.subheader("Depois (preencher após resultado)")
        result = st.text_area("Resultado", height=60)
        error = st.text_area("Erro cometido", height=60)
        learning = st.text_area("Aprendizado", height=60)
        bias = st.text_area("Viés identificado", height=60)

        if st.form_submit_button("Salvar decisão", type="primary", use_container_width=True):
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

with tab_historico:
    try:
        decisions = repo.list_all()
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        st.stop()

    if not decisions:
        st.info("Nenhuma decisão registrada ainda.")
    else:
        ticker_fil = st.selectbox(
            "Filtrar por ativo",
            ["Todos"] + sorted({d.ticker for d in decisions}),
        )
        if ticker_fil != "Todos":
            decisions = [d for d in decisions if d.ticker == ticker_fil]

        for dec in decisions:
            badge = {
                "COMPRAR": "🟢", "MANTER": "🟡",
                "REDUZIR": "🔴", "VENDER": "⛔",
            }.get(dec.outcome.value if dec.outcome else "", "⬜")

            with st.expander(
                f"{badge} {dec.ticker} — {formatar_data_br(dec.date)} — {dec.outcome.value if dec.outcome else 'N/A'}"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Score M1:** {dec.score_m1:.4f}")
                    st.write(f"**Regime:** {dec.regime} | Confidence: {dec.confidence}")
                    st.write(f"**Fragility:** {dec.fragility:.4f}")
                    st.write(f"**Saída:** {dec.invalidation_condition}")
                with c2:
                    st.write(f"**Tese:** {dec.thesis}")
                    st.write(f"**Risco:** {dec.risk}")
                    st.write(f"**Expectativa:** {dec.expectation}")
                if dec.result:
                    st.divider()
                    st.write(f"**Resultado:** {dec.result}")
                    st.write(f"**Erro:** {dec.error}")
                    st.write(f"**Aprendizado:** {dec.learning}")
                    st.write(f"**Viés:** {dec.bias_identified}")
                if dec.ai_audit:
                    st.divider()
                    st.write(f"**M4 AI Audit ({dec.ai_provider}):** {dec.ai_audit}")
