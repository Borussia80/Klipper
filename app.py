"""Klipper — Personal Financial Management"""

import streamlit as st

st.set_page_config(
    page_title="Klipper",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚓ Klipper")
st.caption("Gestão financeira disciplinada. Matemática ancora.")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Dashboard**\nVisão executiva do mês", icon="📊")
with col2:
    st.info("**Transações**\nGastos e ganhos", icon="💸")
with col3:
    st.info("**Investimentos**\nPortfólio + WikiAgent M1/M2/M3", icon="📈")

col4, col5 = st.columns(2)
with col4:
    st.info("**Journal**\nDecision Template auditável", icon="📓")
with col5:
    st.info("**AI Consilium**\nM4 — Claude · Gemini · GPT-4o · Qwen", icon="🤖")

st.divider()
st.caption("WikiAgent Financeiro v2.0 · Klipper · Roberto Milet")
