"""Sobre · Klipper — arquitetura, versão e créditos."""

from __future__ import annotations

import streamlit as st

from core.auth import require_auth
from core.styles import (
    inject_css, k_card_with_header, load_page_icon,
    render_navigation, section_header, sidebar_engines,
    sidebar_user,
)

st.set_page_config(page_title="Sobre · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

# ── Layout ────────────────────────────────────────────────────────────────────
nav_col, content_col = st.columns([1, 4])

with nav_col:
    st.markdown("""
<style>
section[data-testid="column"]:first-child {
    padding: 0.5rem 0.25rem !important;
    min-width: 80px;
}
section[data-testid="column"]:first-child button,
section[data-testid="column"]:first-child a {
    width: 100%;
    text-align: left;
    padding: 0.4rem 0.5rem;
    margin-bottom: 0.15rem;
    font-size: 0.82rem;
}
</style>
""", unsafe_allow_html=True)
    render_navigation()
    st.markdown(sidebar_engines(), unsafe_allow_html=True)
    sidebar_user()

with content_col:
    st.markdown(section_header("Sobre", "arquitetura · versão · créditos"), unsafe_allow_html=True)

    # ── Identidade ────────────────────────────────────────────────────────────
    st.markdown(k_card_with_header("Klipper", """
<div style="font-family:var(--font-sans);font-size:13px;color:var(--ink-2);line-height:1.7;max-width:600px">
  App pessoal de gestão financeira de <strong>Roberto Milet</strong>.<br>
  Nome inspirado nos <em>Clipper ships</em> — velocidade, organização e precisão.<br><br>
  Decisões de investimento e gastos ancoradas em matemática.
  Contexto modula risco; narrativa sem evidência não altera decisão.
</div>
""", "v2.0 · Wealth Operating System"), unsafe_allow_html=True)

    # ── Stack técnico ─────────────────────────────────────────────────────────
    stack_rows = "".join(
        f"""<div style="display:grid;grid-template-columns:120px 1fr;align-items:start;
          gap:12px;padding:9px 0;border-top:1px solid var(--rule)">
  <span style="font-family:var(--font-mono);font-size:11px;color:var(--brass);font-weight:600">{tech}</span>
  <span style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3)">{desc}</span>
</div>"""
        for tech, desc in [
            ("Python 3.12",     "linguagem principal — type hints, Pydantic v2, dataclasses"),
            ("Streamlit",       "interface web — layout de colunas, dialogs, expanders, session_state"),
            ("Supabase",        "PostgreSQL gerenciado — transações, investimentos, contas, parcelas"),
            ("LiteLLM",         "roteamento multi-provider IA — Claude · Gemini · GPT-4o · Qwen · Kimi"),
            ("NVIDIA NIM",      "Kira · IA financeira pessoal — meta/llama-3.3-70b-instruct"),
            ("yfinance / BCB",  "cotações B3, Tesouro Direto, PTAX, câmbio em tempo real"),
            ("Redis / fakeredis","cache de cotações com TTL — fallback in-memory sem infra"),
            ("pytest",          "TDD · 370+ testes · cobertura ≥ 80% · suite < 10s"),
            ("GitHub Actions",  "CI/CD — Ruff · mypy · pytest a cada push"),
            ("Streamlit Cloud", "deploy automático em cada merge em main"),
            ("Railway",         "Telegram Bot — captura zero-fricção via mensagem"),
        ]
    )
    st.markdown(k_card_with_header("Stack técnico", stack_rows, "tecnologias utilizadas"),
                unsafe_allow_html=True)

    # ── Engines WikiAgent ─────────────────────────────────────────────────────
    engine_rows = "".join(
        f"""<div style="display:grid;grid-template-columns:28px 140px 1fr;align-items:center;
          gap:12px;padding:9px 0;border-top:1px solid var(--rule)">
  <span style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.06em;
    padding:2px 4px;border-radius:3px;background:rgba(123,198,138,0.08);
    border:1px solid rgba(123,198,138,0.3);color:var(--moss);text-align:center">{eid}</span>
  <span style="font-family:var(--font-sans);font-size:12px;color:var(--ink);font-weight:500">{name}</span>
  <span style="font-family:var(--font-sans);font-size:11px;color:var(--ink-3)">{desc}</span>
</div>"""
        for eid, name, desc in [
            ("M1", "Quant Engine",    "DY · P/VP · liquidez · volatilidade · spread CDI → score 0–1"),
            ("M2", "Governance",      "Hard limits: max ativo 10% · max tese 25% · caixa mínimo 20%"),
            ("M3", "Context Layer",   "Regime de mercado modula prudência — nunca compra ativo"),
            ("M4", "AI Consilium",    "Claude · Gemini · GPT-4o · Qwen · Kimi — multi-provider"),
            ("AB", "Anti-BS Engine",  "Detecta narrativas sem evidência quantitativa"),
            ("FR", "Fragility Score", "Resiliência a choques: liquidez, concentração, correlação"),
            ("KR", "Kira",            "IA financeira pessoal NVIDIA NIM — briefing e Q&A contextual"),
        ]
    )
    st.markdown(k_card_with_header("WikiAgent Financeiro v2.0", engine_rows,
                                   "engines de decisão ancorada em matemática"),
                unsafe_allow_html=True)

    # ── Links ─────────────────────────────────────────────────────────────────
    link_rows = "".join(
        f"""<div style="padding:8px 0;border-top:1px solid var(--rule);
          font-family:var(--font-sans);font-size:12px;color:var(--ink-3)">
  <strong style="color:var(--ink-2)">{label}</strong> &nbsp;·&nbsp; {value}
</div>"""
        for label, value in [
            ("Produção",   "klipper.streamlit.app"),
            ("Repositório","github.com/Borussia80/Klipper"),
            ("Supabase",   "obmudpulqzhwtcniyzcj.supabase.co"),
        ]
    )
    st.markdown(k_card_with_header("Referências", link_rows, "endpoints e repositório"),
                unsafe_allow_html=True)
