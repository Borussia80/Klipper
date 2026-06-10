"""pages/1_Dashboard.py — Dashboard principal do Klipper.

Responsabilidade: renderizar KPIs do mês, charts interativos e lista
de transações recentes. Lógica de dados via core/analytics.py.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import streamlit as st

from core.auth import require_auth
from core.styles import (
    inject_css, setup_sidebar, hero_section, tx_row,
    fmt_brl, CAT_COLORS,
)

st.set_page_config(
    page_title="Dashboard · Klipper",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()
require_auth()
setup_sidebar()

# ── Dados ─────────────────────────────────────────────────────────────────────
_hoje = date.today()
_mes  = _hoje.month
_ano  = _hoje.year
_mes_label = ['jan','fev','mar','abr','mai','jun',
              'jul','ago','set','out','nov','dez'][_mes - 1]

try:
    from core.repositories import TransactionRepository, BankAccountRepository
    from core.analytics import (
        preparar_dados_donut_categorias,
        preparar_dados_barras_mensais,
    )
    from models.transaction import TransactionType as _TT, TransactionStatus as _TS

    _repo   = TransactionRepository()
    _txs    = _repo.list_by_month(_ano, _mes)
    _contas = BankAccountRepository().list_active()

    _ganhos  = sum((t.amount for t in _txs if t.type == _TT.GANHO), Decimal(0))
    _gastos  = sum((t.amount for t in _txs if t.type == _TT.GASTO), Decimal(0))
    _saldo   = _ganhos - _gastos
    _caixa   = sum((c.balance for c in _contas), Decimal(0))
    _n_pend  = sum(1 for t in _txs if t.status == _TS.PENDENTE)
    _tx_rec  = sorted(_txs, key=lambda t: t.date, reverse=True)[:5]

    _df_donut = preparar_dados_donut_categorias(_txs)
    _df_bar   = preparar_dados_barras_mensais(_ano, _mes)
    _data_ok  = True
except Exception as _e:
    import logging
    logging.getLogger(__name__).warning("Dashboard dados indisponíveis: %s", _e)
    _data_ok = False
    _ganhos = _gastos = _saldo = _caixa = Decimal(0)
    _n_pend = 0
    _tx_rec = []
    _df_donut = _df_bar = None

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    hero_section(
        title    = f"{_mes_label} · {_ano}",
        saldo    = fmt_brl(_saldo),
        ganhos   = fmt_brl(_ganhos, compact=True),
        gastos   = fmt_brl(_gastos, compact=True),
        subtitle = f"{_n_pend} pendentes" if _n_pend else "tudo em dia",
    ),
    unsafe_allow_html=True,
)

# ── KPI row ───────────────────────────────────────────────────────────────────
st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

if _data_ok:
    c1, c2, c3, c4 = st.columns(4, gap="small")
    _saldo_tone  = "pos" if _saldo >= 0 else "neg"
    _saldo_arrow = "▲" if _saldo >= 0 else "▼"

    for col, label, value, sub, tone in [
        (c1, "Caixa disponível",   fmt_brl(_caixa, compact=True),
            f"{len(_contas)} conta(s)", ""),
        (c2, "Entradas · mês",     fmt_brl(_ganhos, compact=True),
            f"{sum(1 for t in _txs if t.type == _TT.GANHO)} fontes", "pos"),
        (c3, "Saídas · mês",       fmt_brl(_gastos, compact=True),
            f"{sum(1 for t in _txs if t.type == _TT.GASTO)} lançamentos", "neg"),
        (c4, "Saldo líquido",      fmt_brl(_saldo, compact=True),
            f"{_saldo_arrow} {_mes_label}/{_ano}", _saldo_tone),
    ]:
        with col:
            tone_color = {"pos": "var(--pos)", "neg": "var(--neg)"}.get(tone, "var(--ink)")
            st.markdown(f"""
<div class="k-card" style="padding:16px 20px">
  <div style="font-size:10px;letter-spacing:.12em;text-transform:uppercase;
    color:var(--ink-3);font-weight:600;margin-bottom:6px">{label}</div>
  <div style="font-family:var(--font-mono);font-size:22px;font-weight:600;
    color:{tone_color};font-variant-numeric:tabular-nums">{value}</div>
  <div style="font-size:11px;color:var(--ink-4);margin-top:4px">{sub}</div>
</div>""", unsafe_allow_html=True)
else:
    st.caption("⚠ Dados indisponíveis — banco de dados inacessível.")

# ── Charts row ────────────────────────────────────────────────────────────────
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

if _data_ok and _df_donut is not None and _df_bar is not None:
    import plotly.express as px
    import plotly.graph_objects as go

    _PLOTLY_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        font_family  ="Geist Sans, Inter, sans-serif",
        font_color   ="#94A3B8",
        margin       =dict(t=8, b=8, l=0, r=0),
        legend       =dict(
            font_size=11,
            bgcolor  ="rgba(0,0,0,0)",
            borderwidth=0,
        ),
    )

    col_donut, col_bar = st.columns([1, 1], gap="medium")

    # ── Donut: gastos por categoria
    with col_donut:
        st.markdown("""
<div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin-bottom:12px">Gastos por categoria</div>
""", unsafe_allow_html=True)

        if not _df_donut.empty:
            _cat_color_map = {cat: color for cat, (color, _) in CAT_COLORS.items()}
            fig_donut = px.pie(
                _df_donut,
                values="valor",
                names="categoria",
                color="categoria",
                color_discrete_map=_cat_color_map,
                hole=0.62,
            )
            fig_donut.update_traces(
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>",
                textfont_size=11,
            )
            fig_donut.update_layout(
                **_PLOTLY_LAYOUT,
                showlegend=True,
                height=280,
                legend=dict(
                    orientation="v",
                    x=1.02, y=0.5,
                    font_size=11,
                    bgcolor="rgba(0,0,0,0)",
                ),
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.caption("Sem gastos registrados este mês.")

    # ── Bar: entradas × saídas últimos 6 meses
    with col_bar:
        st.markdown("""
<div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin-bottom:12px">Entradas × Saídas</div>
""", unsafe_allow_html=True)

        if not _df_bar.empty:
            fig_bar = px.bar(
                _df_bar,
                x="mes",
                y="valor",
                color="tipo",
                barmode="group",
                color_discrete_map={"Entradas": "#10B981", "Saídas": "#3B82F6"},
            )
            fig_bar.update_traces(
                hovertemplate="<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>",
            )
            fig_bar.update_layout(
                **_PLOTLY_LAYOUT,
                height=280,
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.05)",
                    zeroline=False,
                    tickformat=",.0f",
                    tickprefix="R$ ",
                ),
                legend=dict(
                    orientation="h", y=1.08,
                    font_size=11, bgcolor="rgba(0,0,0,0)",
                ),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.caption("Histórico ainda não disponível.")

# ── Últimas transações ────────────────────────────────────────────────────────
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
  <div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    color:var(--ink-3);font-weight:600">Últimas transações</div>
  <a href="/Transacoes" style="font-size:12px;color:var(--brass);
    text-decoration:none;font-weight:500">Ver todas →</a>
</div>
""", unsafe_allow_html=True)

if _data_ok and _tx_rec:
    rows_html = "".join(
        tx_row(
            category   = t.category,
            name       = t.description,
            date_str   = t.date.strftime("%d/%b"),
            subcategory= t.category,
            amount     = fmt_brl(t.amount),
            tone       = "pos" if t.type == _TT.GANHO else "neg",
            notes      = t.notes or "",
        )
        for t in _tx_rec
    )
    st.markdown(
        f'<div class="k-card" style="padding:16px 20px">{rows_html}</div>',
        unsafe_allow_html=True,
    )

    # Botão para lançar nova transação
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    if st.button("＋ Lançar transação", type="primary", use_container_width=False):
        from core.modals import modal_add_transaction
        modal_add_transaction()
else:
    st.markdown(
        '<div class="k-card" style="padding:32px;text-align:center;'
        'color:var(--ink-4);font-size:13px">Nenhuma transação este mês.</div>',
        unsafe_allow_html=True,
    )
    if st.button("＋ Lançar primeira transação", type="primary"):
        from core.modals import modal_add_transaction
        modal_add_transaction()
