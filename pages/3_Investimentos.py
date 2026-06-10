"""pages/3_Investimentos.py — Dashboard de Investimentos do Klipper.

Responsabilidade: exibir portfólio ao vivo, performance vs benchmarks,
alocação e feed de rendimentos. Cotações via core/market_data.py.
Modais via core/modals.py.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal

import streamlit as st

from core.auth import require_auth
from core.styles import (
    inject_css, setup_sidebar, fmt_brl, CAT_COLORS,
)

_log = logging.getLogger(__name__)

st.set_page_config(
    page_title="Investimentos · Klipper",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()
require_auth()
setup_sidebar()

# ── CSS local (promove conteúdo, remove expander legado) ──────────────────────
st.markdown("""
<style>
.inv-hero {
  background: linear-gradient(135deg, #0D1726 0%, #132238 60%, #1B2B45 100%);
  border: 1px solid rgba(217,178,111,0.15);
  border-radius: var(--radius-lg);
  padding: 28px 24px 24px;
  margin-bottom: 20px;
  position: relative; overflow: hidden;
}
.inv-hero::before {
  content:'';position:absolute;top:-30%;right:-10%;
  width:50%;height:160%;
  background:radial-gradient(ellipse, rgba(217,178,111,0.06) 0%, transparent 70%);
  pointer-events:none;
}
.inv-perf-strip {
  display:flex; gap:12px; flex-wrap:wrap; margin-top:16px;
}
.inv-perf-chip {
  display:flex;flex-direction:column;gap:2px;
  padding:10px 16px;
  background:var(--surface-1);
  border:1px solid var(--rule);
  border-radius:var(--radius-sm);
  min-width:120px;
}
.inv-perf-label { font-size:10px;color:var(--ink-4);letter-spacing:.06em;text-transform:uppercase; }
.inv-perf-val   { font-family:var(--font-mono);font-size:15px;font-weight:600; }
.pos-color { color: var(--pos); }
.neg-color { color: var(--neg); }
.neutral   { color: var(--ink-3); }
.inv-table-row {
  display:grid;
  grid-template-columns:90px 1fr 80px 80px 100px 90px 36px;
  align-items:center;gap:8px;
  padding:10px 0;
  border-top:1px solid var(--rule);
  font-size:13px;
}
.inv-table-row:first-child { border-top:none; }
.inv-table-header {
  font-size:10px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--ink-4);font-weight:600;
}
.inv-rend-row {
  display:flex;align-items:center;justify-content:space-between;
  padding:10px 0;border-top:1px solid var(--rule);
}
.inv-rend-row:first-child { border-top:none; }
</style>
""", unsafe_allow_html=True)

# ── Dados ─────────────────────────────────────────────────────────────────────
_hoje = date.today()

try:
    from core.repositories import InvestmentRepository, TransactionRepository
    from core.market_data import get_quote, get_benchmark
    from models.transaction import TransactionType as _TT, Category as _CAT

    _inv_repo = InvestmentRepository()
    _posicoes = _inv_repo.list_active()

    # Enriquece posições com cotação ao vivo
    _posicoes_live = []
    for pos in _posicoes:
        try:
            q = get_quote(pos.ticker)
            valor_atual = q.price * float(pos.quantity)
            custo       = float(pos.avg_price) * float(pos.quantity)
            gl          = valor_atual - custo
            gl_pct      = (gl / custo * 100) if custo else 0
            _posicoes_live.append({
                "ticker":      pos.ticker,
                "setor":       pos.sector,
                "qtd":         pos.quantity,
                "preco_medio": float(pos.avg_price),
                "preco_atual": q.price,
                "var_dia_pct": q.change_pct or 0.0,
                "valor_atual": valor_atual,
                "gl":          gl,
                "gl_pct":      gl_pct,
                "dy":          float(pos.dy or 0),
                "pvp":         float(pos.pvp or 0),
                "inv_id":      str(pos.id),
            })
        except Exception as e:
            _log.warning("Cotação indisponível para %s: %s", pos.ticker, e)
            _posicoes_live.append({
                "ticker": pos.ticker, "setor": pos.sector,
                "qtd": pos.quantity,
                "preco_medio": float(pos.avg_price), "preco_atual": None,
                "var_dia_pct": 0.0,
                "valor_atual": float(pos.avg_price) * float(pos.quantity),
                "gl": 0.0, "gl_pct": 0.0,
                "dy": float(pos.dy or 0), "pvp": float(pos.pvp or 0),
                "inv_id": str(pos.id),
            })

    _total_atual = sum(p["valor_atual"] for p in _posicoes_live)
    _total_custo = sum(p["preco_medio"] * float(p["qtd"]) for p in _posicoes_live)
    _total_gl    = _total_atual - _total_custo
    _total_gl_pct= (_total_gl / _total_custo * 100) if _total_custo else 0

    # Benchmarks
    _benchmarks = {}
    for bm in ["BOVA11", "IFIX", "IVVB11"]:
        try:
            _benchmarks[bm] = get_benchmark(bm)
        except Exception:
            _benchmarks[bm] = None

    # Feed de rendimentos (últimos 60 dias)
    _tx_repo = TransactionRepository()
    _cutoff  = _hoje - timedelta(days=60)
    _rendimentos = [
        t for t in _tx_repo.list_all()
        if t.type == _TT.GANHO
        and hasattr(t, "category")
        and t.category == "Renda"
        and t.date >= _cutoff
    ]
    _rendimentos.sort(key=lambda t: t.date, reverse=True)

    _data_ok = True

except Exception as _e:
    _log.warning("Dados de investimentos indisponíveis: %s", _e)
    _data_ok = False
    _posicoes_live = []
    _total_atual = _total_custo = _total_gl = _total_gl_pct = 0.0
    _benchmarks  = {}
    _rendimentos = []

# ── Hero ──────────────────────────────────────────────────────────────────────
_gl_color = "var(--pos)" if _total_gl >= 0 else "var(--neg)"
_gl_arrow = "▲" if _total_gl >= 0 else "▼"

st.markdown(f"""
<div class="inv-hero">
  <div style="font-family:var(--font-mono);font-size:9px;letter-spacing:.18em;
    text-transform:uppercase;color:var(--brass);font-weight:600;margin-bottom:4px">
    Portfólio · ao vivo
  </div>
  <div style="font-family:var(--font-serif);font-size:36px;line-height:1;
    letter-spacing:-0.02em;color:var(--ink);margin:6px 0 4px">
    {fmt_brl(_total_atual)}
  </div>
  <div style="font-family:var(--font-mono);font-size:14px;color:{_gl_color}">
    {_gl_arrow} {fmt_brl(abs(_total_gl))} ({_total_gl_pct:+.2f}%) custo total
  </div>

  <div class="inv-perf-strip">
    <div class="inv-perf-chip">
      <span class="inv-perf-label">Portfólio</span>
      <span class="inv-perf-val {'pos-color' if _total_gl_pct >= 0 else 'neg-color'}">
        {_total_gl_pct:+.2f}%
      </span>
    </div>
    {''.join(
      f\'\'\'<div class="inv-perf-chip">
        <span class="inv-perf-label">{bm}</span>
        <span class="inv-perf-val {\'pos-color\' if (v and v.change_pct and v.change_pct >= 0) else \'neg-color\' if (v and v.change_pct) else \'neutral\'}">
          {f\'{v.change_pct:+.2f}%\' if v and v.change_pct is not None else \'—\'}
        </span>
      </div>\'\'\'
      for bm, v in _benchmarks.items()
    )}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Ações rápidas ─────────────────────────────────────────────────────────────
col_add, col_refresh, _ = st.columns([1, 1, 4])
with col_add:
    if st.button("＋ Nova posição", type="primary", use_container_width=True):
        from core.modals import modal_add_investment
        modal_add_investment()
with col_refresh:
    if st.button("↺ Atualizar cotações", use_container_width=True):
        st.rerun()

st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

# ── Posições ao vivo ──────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin-bottom:12px">Posições</div>
""", unsafe_allow_html=True)

if _data_ok and _posicoes_live:
    # Cabeçalho
    st.markdown("""
<div class="k-card" style="padding:4px 20px">
  <div class="inv-table-row inv-table-header">
    <span>Ticker</span><span>Setor</span><span style="text-align:right">Preço</span>
    <span style="text-align:right">Var. dia</span>
    <span style="text-align:right">Valor atual</span>
    <span style="text-align:right">G/L</span>
    <span></span>
  </div>
""", unsafe_allow_html=True)

    for pos in sorted(_posicoes_live, key=lambda p: p["valor_atual"], reverse=True):
        _var_color = "var(--pos)" if pos["var_dia_pct"] >= 0 else "var(--neg)"
        _gl_c      = "var(--pos)" if pos["gl"] >= 0 else "var(--neg)"
        _preco_str = fmt_brl(pos["preco_atual"]) if pos["preco_atual"] else "—"
        _edit_key  = f"edit_inv_{pos['ticker']}"

        st.markdown(f"""
<div class="inv-table-row">
  <span style="font-family:var(--font-mono);font-weight:600;
    color:var(--brass);font-size:13px">{pos['ticker']}</span>
  <span style="color:var(--ink-3);font-size:12px">{pos['setor']}</span>
  <span style="font-family:var(--font-mono);text-align:right">{_preco_str}</span>
  <span style="font-family:var(--font-mono);color:{_var_color};text-align:right">
    {pos['var_dia_pct']:+.2f}%
  </span>
  <span style="font-family:var(--font-mono);text-align:right">
    {fmt_brl(pos['valor_atual'], compact=True)}
  </span>
  <span style="font-family:var(--font-mono);color:{_gl_c};text-align:right">
    {pos['gl_pct']:+.1f}%
  </span>
  <span></span>
</div>""", unsafe_allow_html=True)

        # Botão editar fora do HTML (Streamlit não aceita botão dentro de markdown)
        if st.button("✎", key=_edit_key, help=f"Editar {pos['ticker']}"):
            from core.modals import modal_edit_investment
            modal_edit_investment(pos["inv_id"])

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("""
<div class="k-card" style="padding:48px;text-align:center">
  <div style="font-size:32px;margin-bottom:12px">▲</div>
  <div style="color:var(--ink-3);font-size:14px;margin-bottom:4px">
    Nenhuma posição cadastrada.</div>
  <div style="color:var(--ink-4);font-size:12px">
    Clique em "Nova posição" para começar.</div>
</div>""", unsafe_allow_html=True)

# ── Donut alocação ────────────────────────────────────────────────────────────
st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)

if _data_ok and _posicoes_live and _total_atual > 0:
    import plotly.express as px

    # Agrupa por setor
    _setor_map: dict[str, float] = {}
    for p in _posicoes_live:
        _setor_map[p["setor"]] = _setor_map.get(p["setor"], 0) + p["valor_atual"]

    _setor_colors = {
        "FII":         "#D9B26F",
        "Ação":        "#3B82F6",
        "ETF":         "#7FB3C8",
        "Renda Fixa":  "#10B981",
        "Caixa":       "#22C55E",
        "Exterior":    "#8B5CF6",
        "Cripto":      "#F97316",
    }

    col_alloc, col_metrics = st.columns([1, 1], gap="medium")

    with col_alloc:
        st.markdown("""
<div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin-bottom:12px">Alocação</div>
""", unsafe_allow_html=True)
        import pandas as _pd
        _df_alloc = _pd.DataFrame(
            [{"setor": k, "valor": v} for k, v in _setor_map.items()]
        )
        fig_alloc = px.pie(
            _df_alloc, values="valor", names="setor",
            color="setor", color_discrete_map=_setor_colors,
            hole=0.62,
        )
        fig_alloc.update_traces(
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.2f}<extra></extra>",
        )
        fig_alloc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor ="rgba(0,0,0,0)",
            font_family  ="Geist Sans, Inter, sans-serif",
            font_color   ="#94A3B8",
            height=260,
            margin=dict(t=8, b=8, l=0, r=0),
            showlegend=True,
            legend=dict(font_size=11, bgcolor="rgba(0,0,0,0)", borderwidth=0),
        )
        st.plotly_chart(fig_alloc, use_container_width=True)

    with col_metrics:
        st.markdown("""
<div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin-bottom:12px">Por setor</div>
""", unsafe_allow_html=True)
        for setor, valor in sorted(_setor_map.items(), key=lambda x: x[1], reverse=True):
            pct   = valor / _total_atual * 100
            color = _setor_colors.get(setor, "#8F8770")
            st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
  padding:8px 0;border-top:1px solid var(--rule)">
  <div style="display:flex;align-items:center;gap:8px">
    <div style="width:10px;height:10px;border-radius:3px;
      background:{color};flex-shrink:0"></div>
    <span style="font-size:13px;color:var(--ink)">{setor}</span>
  </div>
  <div style="text-align:right">
    <div style="font-family:var(--font-mono);font-size:13px;
      font-weight:600;color:var(--ink)">{fmt_brl(valor, compact=True)}</div>
    <div style="font-size:10px;color:var(--ink-4)">{pct:.1f}%</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Feed de rendimentos ───────────────────────────────────────────────────────
st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="font-size:11px;letter-spacing:.1em;text-transform:uppercase;
  color:var(--ink-3);font-weight:600;margin-bottom:12px">Rendimentos · últimos 60 dias</div>
""", unsafe_allow_html=True)

if _data_ok and _rendimentos:
    _total_rend = sum(r.amount for r in _rendimentos)
    rend_html   = "".join(
        f"""<div class="inv-rend-row">
  <div>
    <div style="font-size:13px;font-weight:500;color:var(--ink)">{r.description}</div>
    <div style="font-size:10.5px;color:var(--ink-4)">{r.date.strftime('%d/%m/%Y')}</div>
  </div>
  <div style="font-family:var(--font-mono);font-size:13px;
    font-weight:600;color:var(--pos)">+{fmt_brl(r.amount)}</div>
</div>"""
        for r in _rendimentos[:15]
    )
    st.markdown(f"""
<div class="k-card" style="padding:16px 20px">
  <div style="display:flex;justify-content:space-between;margin-bottom:12px">
    <span style="font-size:12px;color:var(--ink-3)">
      {len(_rendimentos)} lançamentos</span>
    <span style="font-family:var(--font-mono);font-size:14px;
      font-weight:600;color:var(--pos)">+{fmt_brl(_total_rend)}</span>
  </div>
  {rend_html}
</div>""", unsafe_allow_html=True)
else:
    st.markdown("""
<div class="k-card" style="padding:24px;text-align:center;
  color:var(--ink-4);font-size:13px">
  Nenhum rendimento nos últimos 60 dias.
</div>""", unsafe_allow_html=True)
