"""Cotações · Klipper — B3, Tesouro Direto, câmbio em tempo real."""

from __future__ import annotations

from datetime import date

import streamlit as st

from core.auth import require_auth
from core.market_data import MarketDataService, is_fii
from core.styles import (
    fmt_brl, fmt_change, inject_css, k_card_with_header,
    load_page_icon, render_navigation, section_header,
    sidebar_engines, sidebar_user, stat_card,
)

st.set_page_config(page_title="Cotações · Klipper", page_icon=load_page_icon(), layout="wide")
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
    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.markdown(section_header("Cotações", "B3 · Tesouro · câmbio"), unsafe_allow_html=True)
    with top_right:
        refresh = st.button("↺ Atualizar", use_container_width=True)

    svc = MarketDataService()
    force = bool(refresh)

    # ── Câmbio strip ──────────────────────────────────────────────────────────
    ptax = svc.get_ptax(date.today(), force_refresh=force)
    eur  = svc.get_exchange_rate("EUR/BRL", force_refresh=force)
    gbp  = svc.get_exchange_rate("GBP/BRL", force_refresh=force)
    usd  = svc.get_exchange_rate("USD/BRL", force_refresh=force)

    fx_cards = []
    for label, rate in [("PTAX (USD→BRL)", ptax), ("EUR/BRL", eur), ("GBP/BRL", gbp), ("USD/BRL", usd)]:
        if rate is not None:
            fx_cards.append(stat_card(label, f"R$ {rate.mid:.4f}", f"bid {rate.bid:.4f} / ask {rate.ask:.4f}", "brass"))
        else:
            fx_cards.append(stat_card(label, "—", "indisponível"))

    st.markdown(
        f'<div class="k-grid k-cols-4" style="margin-bottom:20px">{"".join(fx_cards)}</div>',
        unsafe_allow_html=True,
    )

    # ── Tickers configurados ──────────────────────────────────────────────────
    _ACOES = ["PETR4", "VALE3", "ITUB4", "BBDC4", "WEGE3", "RENT3", "MGLU3"]
    _FIIS  = ["MXRF11", "HGLG11", "XPML11", "KNRI11", "BCFF11"]
    _BENCH = ["BOVA11", "SMAL11", "IVVB11"]

    tab_tesouro, tab_acoes, tab_fiis = st.tabs(["Tesouro Direto", "Ações & ETFs", "FIIs"])

    # ── Tab: Tesouro Direto ───────────────────────────────────────────────────
    with tab_tesouro:
        bonds = svc.get_tesouro_bonds(force_refresh=force)
        if not bonds:
            st.info("Dados do Tesouro Direto indisponíveis no momento.")
        else:
            from collections import defaultdict
            by_type: dict[str, list] = defaultdict(list)
            for b in bonds:
                by_type[b.bond_type].append(b)

            for bond_type in ["LFT", "NTN-B", "LTN", "NTN-F"]:
                group = by_type.get(bond_type)
                if not group:
                    continue
                rows_html = "".join(
                    f"""<div style="display:grid;grid-template-columns:2fr 90px 90px 90px 110px;
                        align-items:center;gap:12px;padding:9px 0;border-top:1px solid var(--rule)">
  <span style="font-family:var(--font-sans);font-size:12px;color:var(--ink)">{b.name}</span>
  <span style="font-family:var(--font-mono);font-size:12px;color:var(--moss);text-align:right">{b.rate:.2f}%</span>
  <span style="font-family:var(--font-mono);font-size:12px;color:var(--ink-2);text-align:right">{fmt_brl(b.price)}</span>
  <span style="font-family:var(--font-mono);font-size:12px;color:var(--ink-3);text-align:right">{fmt_brl(b.min_amount)}</span>
  <span style="font-family:var(--font-sans);font-size:11px;color:var(--ink-4);text-align:right">{b.maturity.strftime('%d/%m/%Y')}</span>
</div>"""
                    for b in sorted(group, key=lambda x: x.maturity)
                )
                header_html = (
                    '<div style="display:grid;grid-template-columns:2fr 90px 90px 90px 110px;'
                    'gap:12px;padding-bottom:4px">'
                    '<span style="font-size:10px;color:var(--ink-4)">Título</span>'
                    '<span style="font-size:10px;color:var(--ink-4);text-align:right">Taxa a.a.</span>'
                    '<span style="font-size:10px;color:var(--ink-4);text-align:right">Preço</span>'
                    '<span style="font-size:10px;color:var(--ink-4);text-align:right">Mínimo</span>'
                    '<span style="font-size:10px;color:var(--ink-4);text-align:right">Vencimento</span>'
                    '</div>'
                )
                st.markdown(
                    k_card_with_header(bond_type, header_html + rows_html, f"{len(group)} título(s)"),
                    unsafe_allow_html=True,
                )

    # ── Tab: Ações & ETFs ─────────────────────────────────────────────────────
    with tab_acoes:
        all_tickers = _ACOES + _BENCH
        quotes = svc.get_stocks_batch(all_tickers, force_refresh=force)

        def _stock_row(ticker: str, q) -> str:  # type: ignore[no-untyped-def]
            if q is None:
                return (
                    f'<div style="display:grid;grid-template-columns:80px 1fr 90px 80px 80px;'
                    f'align-items:center;gap:12px;padding:9px 0;border-top:1px solid var(--rule)">'
                    f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--brass)">{ticker}</span>'
                    f'<span style="font-size:11px;color:var(--ink-4)">indisponível</span>'
                    f'<span></span><span></span><span></span></div>'
                )
            chg_color = "var(--moss)" if q.change_pct >= 0 else "var(--rust)"
            return (
                f'<div style="display:grid;grid-template-columns:80px 1fr 90px 80px 80px;'
                f'align-items:center;gap:12px;padding:9px 0;border-top:1px solid var(--rule)">'
                f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--brass)">{ticker}</span>'
                f'<span style="font-size:11px;color:var(--ink-4)">{q.timestamp.strftime("%H:%M") if q.timestamp else ""}</span>'
                f'<span style="font-family:var(--font-mono);font-size:13px;color:var(--ink);text-align:right">{fmt_brl(q.price)}</span>'
                f'<span style="font-family:var(--font-mono);font-size:12px;color:{chg_color};text-align:right">{fmt_change(q.change_pct)}</span>'
                f'<span style="font-family:var(--font-mono);font-size:11px;color:var(--ink-3);text-align:right">{fmt_brl(q.change_abs)}</span>'
                f'</div>'
            )

        # Ações
        acoes_rows = "".join(_stock_row(t, quotes.get(t)) for t in _ACOES)
        header_a = (
            '<div style="display:grid;grid-template-columns:80px 1fr 90px 80px 80px;'
            'gap:12px;padding-bottom:4px">'
            '<span style="font-size:10px;color:var(--ink-4)">Ticker</span>'
            '<span style="font-size:10px;color:var(--ink-4)">Horário</span>'
            '<span style="font-size:10px;color:var(--ink-4);text-align:right">Preço</span>'
            '<span style="font-size:10px;color:var(--ink-4);text-align:right">Var.%</span>'
            '<span style="font-size:10px;color:var(--ink-4);text-align:right">Var.R$</span>'
            '</div>'
        )
        st.markdown(
            k_card_with_header("Ações", header_a + acoes_rows, f"{len(_ACOES)} ativos"),
            unsafe_allow_html=True,
        )

        # Benchmarks
        bench_rows = "".join(_stock_row(t, quotes.get(t)) for t in _BENCH)
        st.markdown(
            k_card_with_header("Benchmarks", header_a + bench_rows, "BOVA11 · SMAL11 · IVVB11"),
            unsafe_allow_html=True,
        )

    # ── Tab: FIIs ─────────────────────────────────────────────────────────────
    with tab_fiis:
        fii_quotes = svc.get_fiis_batch(_FIIS, force_refresh=force)

        fii_rows = ""
        for ticker in _FIIS:
            q = fii_quotes.get(ticker)
            if q is None:
                fii_rows += (
                    f'<div style="display:grid;grid-template-columns:80px 90px 70px 70px 90px;'
                    f'align-items:center;gap:12px;padding:9px 0;border-top:1px solid var(--rule)">'
                    f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--brass)">{ticker}</span>'
                    f'<span style="font-size:11px;color:var(--ink-4)">indisponível</span>'
                    f'<span></span><span></span><span></span></div>'
                )
                continue
            chg_color = "var(--moss)" if q.change_pct >= 0 else "var(--rust)"
            fii_rows += (
                f'<div style="display:grid;grid-template-columns:80px 90px 70px 70px 90px;'
                f'align-items:center;gap:12px;padding:9px 0;border-top:1px solid var(--rule)">'
                f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--brass)">{ticker}</span>'
                f'<span style="font-family:var(--font-mono);font-size:13px;color:var(--ink);text-align:right">{fmt_brl(q.price)}</span>'
                f'<span style="font-family:var(--font-mono);font-size:12px;color:{chg_color};text-align:right">{fmt_change(q.change_pct)}</span>'
                f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--sea);text-align:right">{q.dy_12m:.2f}%</span>'
                f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--ink-3);text-align:right">{fmt_brl(q.last_income)}</span>'
                f'</div>'
            )

        header_f = (
            '<div style="display:grid;grid-template-columns:80px 90px 70px 70px 90px;'
            'gap:12px;padding-bottom:4px">'
            '<span style="font-size:10px;color:var(--ink-4)">Ticker</span>'
            '<span style="font-size:10px;color:var(--ink-4);text-align:right">Preço</span>'
            '<span style="font-size:10px;color:var(--ink-4);text-align:right">Var.%</span>'
            '<span style="font-size:10px;color:var(--ink-4);text-align:right">DY 12M</span>'
            '<span style="font-size:10px;color:var(--ink-4);text-align:right">Último Rend.</span>'
            '</div>'
        )
        st.markdown(
            k_card_with_header("FIIs", header_f + fii_rows, f"{len(_FIIS)} fundos"),
            unsafe_allow_html=True,
        )
