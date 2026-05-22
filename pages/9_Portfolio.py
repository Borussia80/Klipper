"""Portfólio · Klipper — master/detail por tese de investimento."""

from __future__ import annotations

from collections import defaultdict

import streamlit as st

from core.fragility import calcular_fragility_score, reduzir_exposicao_por_fragilidade
from core.m1_quant import calcular_score_m1, classificar_score, Decisao
from core.m2_governance import verificar_limites
from core.m3_context import Confidence, MarketRegime, ajustar_prudencia
from core.repositories import InvestmentRepository
from core.auth import require_auth
from core.styles import (
    bar_track, chip, fmt_brl, inject_css, k_card_with_header, section_header,
    sidebar_engines, sidebar_user, sidebar_ai_qa, render_navigation, stat_card, load_page_icon,
)

st.set_page_config(page_title="Portfólio · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

repo = InvestmentRepository()

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
    sidebar_ai_qa()

with content_col:
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

    st.markdown(section_header("Portfólio", "agrupamento por setor · conviction · âncora quant"), unsafe_allow_html=True)

    if not portfolio:
        st.markdown(
            '<div style="padding:64px 0;text-align:center;color:var(--ink-4)">'
            'portfólio vazio · adicione ativos em Patrimônio</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    total_portfolio = sum(inv.current_value for inv in portfolio)

    # ── Aggregate by sector (= thesis) ────────────────────────────────────────
    by_sector: dict[str, list] = defaultdict(list)
    for inv in portfolio:
        key = inv.sector or inv.type.value
        by_sector[key].append(inv)

    # Compute thesis-level metrics
    theses = []
    for sector, assets in by_sector.items():
        total_val  = sum(a.current_value for a in assets)
        total_gl   = sum(a.gain_loss for a in assets)
        total_cost = sum(a.quantity * a.avg_price for a in assets)
        gl_pct     = (total_gl / total_cost * 100) if total_cost > 0 else 0.0
        alloc_pct  = (total_val / total_portfolio * 100) if total_portfolio > 0 else 0.0
        avg_dy     = sum(a.dy_12m for a in assets) / len(assets)
        avg_vol    = sum(a.volatility for a in assets) / len(assets)
        avg_frag   = sum(a.fragility_score for a in assets) / len(assets)

        # Conviction: 1-5 derived from avg M1 score
        peso_pcts = [(a.current_value / total_portfolio * 100) for a in assets]
        m1_scores = [
            calcular_score_m1(
                dy=a.dy_12m, pvp=a.pvp, liquidez=a.liquidity_daily,
                volatilidade=a.volatility, spread_cdi=a.spread_vs_cdi,
            ) for a in assets
        ]
        avg_m1   = sum(m1_scores) / len(m1_scores) if m1_scores else 0
        conviction = max(1, min(5, int(avg_m1 * 5) + 1))

        # Status
        if alloc_pct > 25:
            status, status_tone = "over-limit", "neg"
        elif gl_pct < -10:
            status, status_tone = "breach", "neg"
        elif gl_pct < 0:
            status, status_tone = "watch", "warn"
        else:
            status, status_tone = "on-track", "pos"

        # Anchor: collect non-empty notes
        anchor_texts = [a.notes for a in assets if a.notes]
        anchor = anchor_texts[0] if anchor_texts else f"DY {avg_dy:.1f}% · vol {avg_vol:.1f}% · {len(assets)} ativo{'s' if len(assets) != 1 else ''}"

        theses.append({
            "sector": sector,
            "assets": assets,
            "total_val": total_val,
            "total_gl": total_gl,
            "gl_pct": gl_pct,
            "alloc_pct": alloc_pct,
            "avg_dy": avg_dy,
            "avg_vol": avg_vol,
            "avg_frag": avg_frag,
            "avg_m1": avg_m1,
            "conviction": conviction,
            "status": status,
            "status_tone": status_tone,
            "anchor": anchor,
        })

    theses.sort(key=lambda x: -x["total_val"])

    # ── KPI strip ─────────────────────────────────────────────────────────────
    n_ok      = sum(1 for t in theses if t["status"] == "on-track")
    n_watch   = sum(1 for t in theses if t["status"] == "watch")
    n_breach  = sum(1 for t in theses if t["status"] in ("breach", "over-limit"))
    avg_conv  = sum(t["conviction"] for t in theses) / len(theses) if theses else 0

    st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:22px">
  {stat_card("Portfólio ativo", str(len(theses)), f"{total_portfolio/1e6:.2f}M total")}
  {stat_card("On-track", str(n_ok), f"{n_watch} em atenção", "pos")}
  {stat_card("Em breach", str(n_breach), "violação de limite ou perda", "neg" if n_breach else "pos")}
  {stat_card("Conviction médio", f"{avg_conv:.1f}/5", "score M1 médio do portfólio", "brass")}
</div>
""", unsafe_allow_html=True)

    # ── Master / Detail layout ────────────────────────────────────────────────
    col_list, col_detail = st.columns([1, 2], gap="large")

    with col_list:
        st.markdown(section_header("Portfólio", f"{len(theses)} grupos"), unsafe_allow_html=True)

        thesis_sel_idx = None
        for i, t in enumerate(theses):
            conv_dots = "◆" * t["conviction"] + "◇" * (5 - t["conviction"])
            alloc_bar = bar_track(t["alloc_pct"], 100)
            is_sel = (st.session_state.get("tese_sel") == t["sector"])
            border_style = "border:1px solid var(--brass);box-shadow:var(--glow-brass);" if is_sel else ""

            card_body = f"""
<div style="font-size:9.5px;letter-spacing:0.12em;text-transform:uppercase;
  color:var(--brass);font-weight:600;margin-bottom:6px">{t['sector']}</div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
  <span style="font-family:var(--font-mono);font-size:11px;color:var(--ink-3)">{conv_dots}</span>
  {chip(t['status'].replace('-', ' '), t['status_tone'])}
</div>
<div style="display:flex;justify-content:space-between;
  font-family:var(--font-mono);font-size:11px;color:var(--ink-2);margin-bottom:8px">
  <span>{fmt_brl(t['total_val'], compact=True)}</span>
  <span style="color:{'var(--moss)' if t['gl_pct'] >= 0 else 'var(--rust)'}">{t['gl_pct']:+.1f}%</span>
  <span class="muted">{t['alloc_pct']:.1f}% portfólio</span>
</div>
{alloc_bar}"""

            st.markdown(
                f'<div class="k-card" style="margin-bottom:10px;cursor:pointer;{border_style}">'
                f'<div class="k-card-b">{card_body}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Ver {t['sector']}", key=f"tese_btn_{i}",
                         width='stretch', type="secondary"):
                st.session_state["tese_sel"] = t["sector"]
                st.rerun()

    with col_detail:
        tese_sel = st.session_state.get("tese_sel")
        t = next((x for x in theses if x["sector"] == tese_sel), theses[0] if theses else None)

        if t is None:
            st.markdown(
                '<div style="padding:48px 0;text-align:center;color:var(--ink-4)">selecione uma tese</div>',
                unsafe_allow_html=True,
            )
        else:
            gl_c  = "var(--moss)" if t["gl_pct"] >= 0 else "var(--rust)"
            frag_c = "var(--rust)" if t["avg_frag"] > 0.65 else "var(--lantern)" if t["avg_frag"] > 0.40 else "var(--moss)"

            # 4-metric strip
            st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:18px">
  {stat_card("Alocação", f"{t['alloc_pct']:.1f}%", fmt_brl(t['total_val'], compact=True))}
  {stat_card("Perf (P&L)", f"{t['gl_pct']:+.1f}%", fmt_brl(t['total_gl'], compact=True),
             "pos" if t['gl_pct'] >= 0 else "neg")}
  {stat_card("DY médio 12m", f"{t['avg_dy']:.1f}%", f"vol média {t['avg_vol']:.1f}%")}
  {stat_card("Score M1 médio", f"{t['avg_m1']:.2f}", f"conviction {t['conviction']}/5", "brass")}
</div>
""", unsafe_allow_html=True)

            # Âncora quant (italic serif)
            anchor_html = (
                f'<div class="k-kicker">Âncora quant</div>'
                f'<div class="serif" style="font-style:italic;font-size:15px;color:var(--ink);'
                f'line-height:1.6;margin-top:8px;margin-bottom:16px">&#8220;{t["anchor"]}&#8221;</div>'
            )

            # Assets table
            asset_rows = ""
            for a in sorted(t["assets"], key=lambda x: -x.current_value):
                peso = (a.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
                gl_c2 = "var(--moss)" if a.gain_loss >= 0 else "var(--rust)"
                asset_rows += (
                    f'<div style="display:grid;grid-template-columns:80px 90px 1fr 80px 80px;'
                    f'gap:0;padding:9px 18px;border-top:1px solid var(--rule);'
                    f'font-family:var(--font-mono);font-size:11px;align-items:center">'
                    f'<span style="color:var(--ink);font-weight:600;font-family:var(--font-sans)">{a.ticker}</span>'
                    f'<span style="color:var(--ink-2)">{fmt_brl(a.current_value, compact=True)}</span>'
                    f'<div>{bar_track(peso, 100)}</div>'
                    f'<span style="color:{gl_c2};text-align:right">{a.gain_loss_pct:+.1f}%</span>'
                    f'<span class="muted" style="text-align:right">{peso:.1f}%</span>'
                    f'</div>'
                )

            asset_header = (
                '<div style="display:grid;grid-template-columns:80px 90px 1fr 80px 80px;'
                'gap:0;padding:8px 18px;font-family:var(--font-sans);font-size:9.5px;'
                'letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-4);font-weight:600;'
                'border-bottom:1px solid var(--rule-2)">'
                '<span>Ativo</span><span>Valor</span><span>Peso</span>'
                '<span style="text-align:right">G/L%</span><span style="text-align:right">%Port.</span>'
                '</div>'
            )

            # Risk indicators
            risk_html = (
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px">'
                f'<div>'
                f'<div class="k-kicker">Volatilidade média</div>'
                f'<div class="mono" style="font-size:18px;color:var(--ink)">{t["avg_vol"]:.1f}%</div>'
                f'{bar_track(t["avg_vol"], 60, "warn" if t["avg_vol"] > 30 else "")}'
                f'</div>'
                f'<div>'
                f'<div class="k-kicker">Fragility médio</div>'
                f'<div class="mono" style="font-size:18px;color:{frag_c}">{t["avg_frag"]:.2f}</div>'
                f'{bar_track(t["avg_frag"] * 100, 100, "neg" if t["avg_frag"] > 0.65 else "warn" if t["avg_frag"] > 0.40 else "pos")}'
                f'</div>'
                f'</div>'
            )

            body = f'{anchor_html}{asset_header}{asset_rows}{risk_html}'
            st.markdown(
                k_card_with_header(t["sector"], body, hint=f"{len(t['assets'])} ativos · {t['status']}"),
                unsafe_allow_html=True,
            )
