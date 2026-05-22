"""Klipper — Wealth Operating System"""

import streamlit as st
from core.auth import require_auth
from core.styles import (
    _brand_b64,
    brand_icon_img,
    inject_css,
    load_page_icon,
    render_navigation,
    sidebar_engines,
    sidebar_user,
)

st.set_page_config(
    page_title="Klipper",
    page_icon=load_page_icon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()

require_auth()

NAV_ITEMS = [
    ("↹",  "Movimento",  "Ledger de transações, parcelamentos e análise de gastos"),
    ("▤",  "Cartões",    "Wallet de cartões, faturas e comprometimento futuro"),
    ("◐",  "Patrimônio", "Portfólio com WikiAgent M1/M2/M3, Anti-BS e Fragility"),
    ("⌗",  "Orçamento",  "Orçamentos por categoria, score financeiro e alertas"),
    ("◈",  "Consilium",  "M4 AI — Claude · Gemini · GPT-4o · Qwen multi-provider"),
    ("◎",  "Saúde",      "Atendimentos Pedro · solicitações de reembolso · operadora"),
]

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
    # ── Hero ───────────────────────────────────────────────────────────────────────
    lockup_uri = _brand_b64("klipper-lockup-dark.png")
    if lockup_uri:
        hero_logo = (
            f'<img src="{lockup_uri}" '
            f'style="height:72px;width:auto;display:block;border-radius:12px;'
            f'margin-bottom:16px" alt="Klipper">'
        )
    else:
        icon = brand_icon_img(52)
        hero_logo = f"""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:6px">
  <div style="width:52px;height:52px;overflow:hidden;border-radius:16px;
    box-shadow:0 0 0 1px var(--rule-brass),0 0 24px rgba(217,178,111,0.08)">
    {icon}
  </div>
  <div>
    <div style="font-family:'General Sans','Inter',sans-serif;font-size:32px;font-weight:600;
      letter-spacing:-0.03em;color:var(--ink);line-height:1">Klipper</div>
    <div style="font-size:11px;letter-spacing:0.18em;text-transform:uppercase;
      color:var(--ink-4);font-weight:500;margin-top:4px">Wealth · operating system</div>
  </div>
</div>"""

    st.markdown(f"""
<div style="padding:16px 0 0">
  {hero_logo}
  <div style="font-family:'Instrument Serif',Georgia,serif;font-size:16px;color:var(--ink-3);
    margin-bottom:24px;line-height:1.5;max-width:560px">
    Matemática ancora. Contexto modula risco. Narrativa sem evidência não altera decisão.
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Nav cards ──────────────────────────────────────────────────────────────────
    cards_html = "".join(
        f"""<div class="k-stat-card" style="display:flex;flex-direction:column;gap:8px">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-family:var(--font-mono);font-size:18px;color:var(--brass)">{mark}</span>
    <span style="font-family:var(--font-sans);font-size:14px;color:var(--ink);font-weight:500">{title}</span>
  </div>
  <div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);line-height:1.5">{desc}</div>
</div>"""
        for mark, title, desc in NAV_ITEMS
    )

    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));'
        f'gap:16px;margin-bottom:32px">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    # ── WikiAgent modules ──────────────────────────────────────────────────────────
    engine_items = [
        ("M1", "Quant Engine",    "DY · P/VP · liquidez · volatilidade · spread CDI → score 0–1"),
        ("M2", "Governance",      "Hard limits: max ativo 10% · max tese 25% · caixa 20%"),
        ("M3", "Context Layer",   "Regime de mercado modula prudência — não compra ativo"),
        ("AB", "Anti-BS Engine",  "Detecta narrativas sem evidência quantitativa"),
        ("FR", "Fragility Score", "Resiliência a choques: liquidez, concentração, correlação"),
    ]
    engines_html = "".join(
        f"""<div style="display:grid;grid-template-columns:28px 120px 1fr;align-items:center;
      gap:12px;padding:10px 0;border-top:1px solid var(--rule)">
  <span style="font-family:var(--font-mono);font-size:9px;letter-spacing:0.06em;
    padding:2px 4px;border-radius:3px;background:rgba(123,198,138,0.08);
    border:1px solid rgba(123,198,138,0.3);color:var(--moss);text-align:center">{eid}</span>
  <span style="font-family:var(--font-sans);font-size:13px;color:var(--ink);font-weight:500">{name}</span>
  <span style="font-family:var(--font-sans);font-size:11px;color:var(--ink-3)">{desc}</span>
</div>"""
        for eid, name, desc in engine_items
    )

    st.markdown(f"""
<div class="k-card gilt" style="margin-bottom:20px">
  <div class="k-card-h">
    <div>
      <div class="k-card-t">WikiAgent Financeiro v2.0</div>
      <div style="font-family:var(--font-sans);font-size:11.5px;color:var(--ink-3);margin-top:2px">
        engines M · decisão ancorada em matemática
      </div>
    </div>
  </div>
  <div class="k-card-b">{engines_html}</div>
</div>
""", unsafe_allow_html=True)

