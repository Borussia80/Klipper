"""Patrimônio · Klipper — posições, governança e WikiAgent engines."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.anti_bs import verificar_alertas, PERGUNTA_OBRIGATORIA
from core.formatters import formatar_moeda_brl, formatar_percentual
from core.fragility import calcular_fragility_score, reduzir_exposicao_por_fragilidade
from core.m1_quant import calcular_score_m1, classificar_score, Decisao
from core.m2_governance import verificar_limites, hard_fail
from core.m3_context import Confidence, MarketRegime, ajustar_prudencia
from core.repositories import InvestmentRepository
from core.auth import require_auth
from core.styles import (
    bar_track, fmt_brl, inject_css, k_card_with_header,
    section_header, sidebar_brand, sidebar_engines, sidebar_user, sidebar_nav,
    stat_card, load_page_icon,
)
from models.investment import Investment, InvestmentType

st.set_page_config(page_title="Patrimônio · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

repo = InvestmentRepository()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_brand(), unsafe_allow_html=True)
    sidebar_nav()

    # M3 Context
    st.markdown(
        '<div style="padding:6px 12px 2px;font-family:var(--font-sans);font-size:9.5px;'
        'letter-spacing:0.16em;text-transform:uppercase;color:var(--ink-4);font-weight:600">'
        'M3 · Contexto</div>',
        unsafe_allow_html=True,
    )
    regime = MarketRegime(
        st.selectbox("Regime", [r.value for r in MarketRegime], index=0,
                     label_visibility="collapsed")
    )
    confidence = Confidence(
        st.selectbox("Confidence", [c.value for c in Confidence], index=2,
                     label_visibility="collapsed")
    )
    caixa_disponivel = st.number_input(
        "Caixa disponível (R$)", min_value=0.0, step=100.0, value=0.0,
        label_visibility="collapsed",
    )

    with st.expander("+ Adicionar / Atualizar ativo"):
        with st.form("form_investimento", clear_on_submit=True):
            ticker      = st.text_input("Ticker (ex: MXRF11)").upper()
            tipo        = st.selectbox("Tipo", [t.value for t in InvestmentType])
            setor       = st.text_input("Setor")
            quantidade  = st.number_input("Cotas", min_value=0.01, step=1.0)
            preco_medio = st.number_input("Preço médio (R$)", min_value=0.01, step=0.01, format="%.2f")
            preco_atual = st.number_input("Preço atual (R$)", min_value=0.01, step=0.01, format="%.2f")
            dy_12m      = st.number_input("DY 12m (%)", min_value=0.0, step=0.1, format="%.2f")
            pvp         = st.number_input("P/VP", min_value=0.0, step=0.01, format="%.4f")
            liquidez    = st.number_input("Liquidez diária (R$)", min_value=0.0, step=1000.0)
            volatilidade = st.slider("Volatilidade anual (%)", 0.0, 60.0, 10.0, 0.5)
            spread_cdi  = st.slider("Spread vs CDI (p.p.)", -5.0, 10.0, 2.0, 0.25)
            notas_inv   = st.text_area("Notas")
            if st.form_submit_button("Salvar ativo", type="primary", width='stretch'):
                if not ticker:
                    st.error("Ticker obrigatório.")
                else:
                    try:
                        repo.upsert(Investment(
                            ticker=ticker, type=InvestmentType(tipo),
                            quantity=quantidade, avg_price=preco_medio, current_price=preco_atual,
                            dy_12m=dy_12m, pvp=pvp, liquidity_daily=liquidez,
                            volatility=volatilidade, spread_vs_cdi=spread_cdi,
                            sector=setor, notes=notas_inv,
                        ))
                        st.success(f"{ticker} salvo.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

    st.markdown(sidebar_engines(), unsafe_allow_html=True)
    sidebar_user()

# ── Load portfolio ─────────────────────────────────────────────────────────────
try:
    portfolio = repo.get_portfolio()
except Exception as e:
    st.error(f"Erro ao carregar portfólio: {e}")
    st.stop()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(section_header("Patrimônio", "posições · governança · engines"), unsafe_allow_html=True)

if not portfolio:
    st.markdown(
        '<div style="padding:64px 0;text-align:center;color:var(--ink-4)">portfólio vazio · adicione o primeiro ativo pelo menu lateral</div>',
        unsafe_allow_html=True,
    )
    st.stop()

total_portfolio = sum(inv.current_value for inv in portfolio)
total_gl        = sum(inv.gain_loss for inv in portfolio)
gl_pct          = (total_gl / (total_portfolio - total_gl) * 100) if (total_portfolio - total_gl) != 0 else 0

# M2 governance
alertas_m2       = verificar_limites(portfolio, float(caixa_disponivel))
has_hard_fail, motivo_fail = hard_fail(alertas_m2)
violations       = len([a for a in alertas_m2 if a.severity == "CRITICAL"])

if has_hard_fail:
    st.error(f"M2 Hard Fail: {motivo_fail}")

# ── Patrimônio hero ───────────────────────────────────────────────────────────
gl_tone  = "pos" if total_gl >= 0 else "neg"
gl_color = "var(--moss)" if total_gl >= 0 else "var(--rust)"
gl_sign  = "+" if total_gl >= 0 else ""
_type_totals: dict[str, float] = {}
for _inv in portfolio:
    _type_totals[_inv.type.value] = _type_totals.get(_inv.type.value, 0.0) + _inv.current_value
_chips = " ".join(
    f'<span class="k-chip">{t} · {v / total_portfolio * 100:.0f}%</span>'
    for t, v in sorted(_type_totals.items(), key=lambda x: -x[1])
)
st.markdown(f"""<div class="k-card gilt" style="margin-bottom:20px">
  <div class="k-card-b">
    <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:20px;flex-wrap:wrap">
      <div>
        <div class="k-kicker">Patrimônio total · portfólio</div>
        <div class="serif" style="font-size:40px;line-height:1;letter-spacing:-0.02em;color:var(--ink);
          font-variant-numeric:tabular-nums;margin-top:8px">{fmt_brl(total_portfolio)}</div>
        <div style="margin-top:10px">
          <span class="mono" style="font-size:13px;color:{gl_color}">{gl_sign}{fmt_brl(total_gl, compact=True)}</span>
          <span class="mono muted" style="font-size:11px;margin-left:8px">({gl_pct:+.1f}% sobre custo)</span>
        </div>
      </div>
      <div style="text-align:right;flex-shrink:0">
        <div class="k-kicker" style="text-align:right">composição</div>
        <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;justify-content:flex-end">{_chips}</div>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ── KPI strip ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:20px">
  {stat_card("Posições ativas", str(len(portfolio)),
             fmt_brl(total_portfolio, compact=True))}
  {stat_card("Ganho / Perda total", fmt_brl(total_gl, compact=True),
             f"{gl_pct:+.1f}% sobre custo", gl_tone)}
  {stat_card("Regime M3", regime.value, f"confidence · {confidence.value}")}
  {stat_card("Violações M2", str(violations),
             "hard fail" if has_hard_fail else "dentro dos limites",
             "neg" if violations > 0 else "pos")}
</div>
""", unsafe_allow_html=True)

# ── Score & positions ─────────────────────────────────────────────────────────
# Compute per-asset scores
rows = []
decisao_counts = {"COMPRAR": 0, "MANTER": 0, "REDUZIR": 0}

for inv in portfolio:
    peso_pct     = (inv.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
    score_m1     = calcular_score_m1(
        dy=inv.dy_12m, pvp=inv.pvp, liquidez=inv.liquidity_daily,
        volatilidade=inv.volatility, spread_cdi=inv.spread_vs_cdi,
    )
    score_ajust  = ajustar_prudencia(score_m1, regime, confidence)
    fragility    = calcular_fragility_score(inv, peso_portfolio_pct=peso_pct)
    score_final  = reduzir_exposicao_por_fragilidade(score_ajust, fragility.total)
    decisao      = classificar_score(score_final)
    decisao_counts[decisao.value] += 1

    dec_col = {
        "COMPRAR": "var(--moss)",
        "MANTER":  "var(--lantern)",
        "REDUZIR": "var(--rust)",
    }[decisao.value]

    rows.append({
        "Ticker":      inv.ticker,
        "Tipo":        inv.type.value,
        "Valor (R$)":  formatar_moeda_brl(inv.current_value),
        "Peso %":      formatar_percentual(peso_pct),
        "DY 12m":      formatar_percentual(inv.dy_12m),
        "P/VP":        f"{inv.pvp:.2f}",
        "Score M1":    f"{score_m1:.2f}",
        "Ajust. M3":   f"{score_ajust:.2f}",
        "Fragility":   f"{fragility.total:.2f}",
        "Score final": f"{score_final:.2f}",
        "Decisão":     decisao.value,
        "G/L":         formatar_moeda_brl(inv.gain_loss),
        "G/L %":       formatar_percentual(inv.gain_loss_pct),
    })

col_left, col_right = st.columns([2, 1], gap="large")

with col_left:
    # Positions table
    df = pd.DataFrame(rows)
    st.markdown(k_card_with_header("Posições", "", f"{len(portfolio)} ativos"), unsafe_allow_html=True)
    st.dataframe(df, width='stretch', hide_index=True, height=400)

with col_right:
    # Allocation by type
    by_type: dict[str, float] = {}
    for inv in portfolio:
        by_type[inv.type.value] = by_type.get(inv.type.value, 0) + inv.current_value

    type_colors = {
        "FII": "#D9B26F", "ACAO": "#7FB3C8", "RENDA_FIXA": "#7BC68A",
        "CRIPTO": "#E08855", "INTERNACIONAL": "#C9BC9E", "OUTRO": "#5C5746",
    }
    sorted_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)

    # Donut chart via Plotly
    labels = [t for t, _ in sorted_types]
    values = [v for _, v in sorted_types]
    colors = [type_colors.get(t, "#5C5746") for t in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker=dict(colors=colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        textinfo="none",
        hovertemplate="%{label}<br>%{value:,.2f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        height=220, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        annotations=[dict(
            text=fmt_brl(total_portfolio, compact=True),
            x=0.5, y=0.5, font_size=16,
            font_family="Instrument Serif, Georgia, serif",
            font_color="#F2EAD3", showarrow=False,
        )],
    )

    st.markdown(k_card_with_header("Alocação por classe", "", "snapshot · hoje"), unsafe_allow_html=True)
    st.plotly_chart(fig, width='stretch')

    # Legend
    leg_rows = "".join(
        f'<div style="display:grid;grid-template-columns:10px 1fr auto;align-items:center;gap:10px;font-size:12px;padding:4px 0">'
        f'<span style="width:10px;height:10px;border-radius:2px;background:{type_colors.get(t,"#5C5746")};display:inline-block"></span>'
        f'<span style="color:var(--ink-3)">{t}</span>'
        f'<span class="mono" style="font-size:11px;color:var(--ink-2)">{v/total_portfolio*100:.0f}%</span>'
        f'</div>'
        for t, v in sorted_types
    )
    st.markdown(f'<div style="padding:0 4px">{leg_rows}</div>', unsafe_allow_html=True)

# ── M2 Governance ─────────────────────────────────────────────────────────────
st.markdown(section_header("Governance · M2", "beginner mode · limites duros"), unsafe_allow_html=True)

col_gov, col_bs = st.columns(2, gap="large")

with col_gov:
    # Find max single asset weight
    max_asset_pct = max(
        (inv.current_value / total_portfolio * 100) for inv in portfolio
    ) if portfolio else 0
    max_asset_inv = max(portfolio, key=lambda i: i.current_value, default=None)

    # Max tese (group by sector if available)
    by_sector: dict[str, float] = {}
    for inv in portfolio:
        s = inv.sector or inv.type.value
        by_sector[s] = by_sector.get(s, 0) + (inv.current_value / total_portfolio * 100)
    max_thesis_pct = max(by_sector.values()) if by_sector else 0

    # Caixa %
    caixa_pct_gov = (caixa_disponivel / (total_portfolio + caixa_disponivel) * 100) if (total_portfolio + caixa_disponivel) > 0 else 0

    gov_items = [
        ("Max por ativo",  max_asset_pct,  10.0, max_asset_inv.ticker if max_asset_inv else "—"),
        ("Max por tese",   max_thesis_pct, 25.0, max((by_sector or {"—": 0}), key=by_sector.get)),
        ("Caixa mínimo",   caixa_pct_gov,  20.0, "M2 floor"),
    ]

    gov_rows = []
    for label_g, val, limit, ref in gov_items:
        ok      = val <= limit if label_g != "Caixa mínimo" else val >= limit
        sc      = "var(--moss)" if ok else "var(--rust)"
        tick    = "✓" if ok else "✗"
        tone    = "pos" if ok else "neg"
        gov_rows.append(f"""<div class="k-gov-row">
  <div>
    <div style="font-family:var(--font-sans);font-size:12px;color:var(--ink)">{label_g}</div>
    <div class="mono muted" style="font-size:10px">{ref} · limite {limit:.0f}%</div>
  </div>
  <div style="text-align:right">
    <div class="mono" style="font-size:15px;color:{sc}">{val:.1f}%</div>
    <div style="font-size:10px;color:{sc};font-weight:600">{tick} {'OK' if ok else 'VIOLAÇÃO'}</div>
  </div>
</div>""")

    st.markdown(
        k_card_with_header("Governance · M2", "".join(gov_rows), "beginner mode"),
        unsafe_allow_html=True,
    )

with col_bs:
    # Anti-BS per selected asset
    st.markdown(
        f'<div style="font-family:var(--font-mono);font-size:10px;color:var(--ink-4);'
        f'font-style:italic;margin-bottom:8px">{PERGUNTA_OBRIGATORIA}</div>',
        unsafe_allow_html=True,
    )
    ticker_sel = st.selectbox("Ativo para análise Anti-BS", [inv.ticker for inv in portfolio],
                               label_visibility="collapsed")
    inv_sel  = next(inv for inv in portfolio if inv.ticker == ticker_sel)
    peso_sel = (inv_sel.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
    alertas_bs = verificar_alertas(inv_sel, peso_sel)

    if alertas_bs:
        bs_rows = []
        for alerta in alertas_bs:
            col = "var(--rust)" if alerta.severity == "CRITICAL" else "var(--lantern)"
            bs_rows.append(f"""<div style="padding:10px 14px;margin-bottom:8px;
              background:rgba(216,124,106,0.06);border:1px solid rgba(216,124,106,0.25);
              border-radius:var(--radius-xs)">
  <div style="font-family:var(--font-mono);font-size:10px;color:{col};font-weight:600;margin-bottom:4px">{alerta.code}</div>
  <div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-2)">{alerta.message}</div>
</div>""")
        st.markdown(
            k_card_with_header(f"Anti-BS · {ticker_sel}", "".join(bs_rows), f"peso {peso_sel:.1f}%"),
            unsafe_allow_html=True,
        )
    else:
        ok_html = f"""<div style="padding:20px 0;text-align:center">
  <div style="color:var(--moss);font-size:20px;margin-bottom:8px">✓</div>
  <div style="color:var(--ink-2);font-family:var(--font-sans);font-size:13px">Nenhum alerta Anti-BS para {ticker_sel}</div>
</div>"""
        st.markdown(
            k_card_with_header(f"Anti-BS · {ticker_sel}", ok_html, f"peso {peso_sel:.1f}%"),
            unsafe_allow_html=True,
        )
