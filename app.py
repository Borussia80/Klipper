"""Klipper — Wealth Operating System"""

from datetime import date
from decimal import Decimal

import streamlit as st
from core.auth import require_auth
from core.styles import (
    _brand_b64,
    action_card,
    brand_icon_img,
    context_card,
    fmt_brl,
    inject_css,
    kpi_card,
    load_page_icon,
    render_navigation,
    sidebar_engines,
    sidebar_user,
    stat_card,
)

st.set_page_config(
    page_title="Klipper",
    page_icon=load_page_icon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()

require_auth()

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
@media (max-width: 640px) {
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    flex: 0 0 0 !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {
    flex: 1 1 100% !important;
    width: 100% !important;
  }
}
</style>
""", unsafe_allow_html=True)
    render_navigation(key_suffix="_col")
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

    # ── Daily briefing ────────────────────────────────────────────────────────────
    _hoje = date.today()
    try:
        from core.repositories import TransactionRepository, BankAccountRepository
        from models.transaction import TransactionType as _TT
        _txs    = TransactionRepository().list_by_month(_hoje.year, _hoje.month)
        _contas = BankAccountRepository().list_active()
        _ganhos = sum((t.amount for t in _txs if t.type == _TT.GANHO), Decimal(0))
        _gastos = sum((t.amount for t in _txs if t.type == _TT.GASTO), Decimal(0))
        _saldo  = _ganhos - _gastos
        _caixa  = sum((c.balance for c in _contas), Decimal(0))
        _n_pend = sum(1 for t in _txs if t.status.value == "PENDENTE")
        _mes    = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'][_hoje.month-1]
        _saldo_tone = "pos" if _saldo >= 0 else "neg"
        _saldo_delta = f"{'▲' if _saldo >= 0 else '▼'} {fmt_brl(abs(_saldo), compact=True)}"

        # Row 1 — Caixa (action card) + KPI cards
        st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:24px">
  {action_card("Caixa disponível", fmt_brl(_caixa, compact=True),
               f"{_n_pend} pendentes" if _n_pend else "sem pendências")}
  {kpi_card("Entradas · mês", fmt_brl(_ganhos, compact=True),
            f"{sum(1 for t in _txs if t.type == _TT.GANHO)} fontes", "pos")}
  {kpi_card("Saídas · mês", fmt_brl(_gastos, compact=True),
            f"{sum(1 for t in _txs if t.type == _TT.GASTO)} lançamentos")}
  {kpi_card("Saldo líquido", fmt_brl(_saldo, compact=True),
            f"{_saldo_delta} · {_mes}/{_hoje.year}", _saldo_tone)}
</div>
""", unsafe_allow_html=True)
    except Exception as _e:
        import logging as _logging
        _logging.getLogger(__name__).warning("Briefing indisponível: %s", _e)
        st.caption("⚠ Briefing indisponível — banco de dados inacessível.")

    # ── Quick actions row ─────────────────────────────────────────────────────────
    st.markdown("""
<div style="display:flex;gap:10px;margin-bottom:24px;flex-wrap:wrap">
  <a href="/Transacoes" style="text-decoration:none">
    <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;
      background:var(--surface-2);border:1px solid var(--rule-2);border-radius:var(--radius-input);
      font-family:var(--font-sans);font-size:13px;font-weight:500;color:var(--ink);
      cursor:pointer;transition:background 120ms;white-space:nowrap">
      <span style="font-size:16px">＋</span> Lançar
    </div>
  </a>
  <a href="/Transacoes" style="text-decoration:none">
    <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;
      background:var(--surface-2);border:1px solid var(--rule-2);border-radius:var(--radius-input);
      font-family:var(--font-sans);font-size:13px;font-weight:500;color:var(--ink);
      cursor:pointer;transition:background 120ms;white-space:nowrap">
      <span style="font-size:16px">⇄</span> Transferir
    </div>
  </a>
  <a href="/Extratos" style="text-decoration:none">
    <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;
      background:var(--surface-2);border:1px solid var(--rule-2);border-radius:var(--radius-input);
      font-family:var(--font-sans);font-size:13px;font-weight:500;color:var(--ink);
      cursor:pointer;transition:background 120ms;white-space:nowrap">
      <span style="font-size:16px">⬆</span> Importar
    </div>
  </a>
  <a href="/Investimentos" style="text-decoration:none">
    <div style="display:flex;align-items:center;gap:8px;padding:10px 16px;
      background:var(--surface-2);border:1px solid var(--rule-2);border-radius:var(--radius-input);
      font-family:var(--font-sans);font-size:13px;font-weight:500;color:var(--ink);
      cursor:pointer;transition:background 120ms;white-space:nowrap">
      <span style="font-size:16px">◈</span> Investir
    </div>
  </a>
</div>
""", unsafe_allow_html=True)

    # ── WikiAgent modules ──────────────────────────────────────────────────────────
    engine_items = [
        ("M1", "Quant Engine",    "DY · P/VP · liquidez · volatilidade · spread CDI → score 0–1"),
        ("M2", "Governance",      "Hard limits: max ativo 10% · max tese 25% · caixa 20%"),
        ("M3", "Context Layer",   "Regime de mercado modula prudência — não compra ativo"),
        ("AB", "Anti-BS Engine",  "Detecta narrativas sem evidência quantitativa"),
        ("FR", "Fragility Score", "Resiliência a choques: liquidez, concentração, correlação"),
    ]
    engines_body = "".join(
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

    st.markdown(
        context_card("WikiAgent Financeiro v2.0", engines_body, "engines M · decisão ancorada em matemática"),
        unsafe_allow_html=True
    )

