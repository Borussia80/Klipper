"""Patrimônio · Klipper — posições, governança e WikiAgent engines."""

from __future__ import annotations

import html as _html_mod
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def _html_esc(s: str) -> str:
    return _html_mod.escape(str(s))

from core.analytics import (
    preparar_dados_bolha, preparar_dados_linha_normalizado,
    preparar_dados_tesouro_historico,
)
from core.anti_bs import verificar_alertas, PERGUNTA_OBRIGATORIA
from core.formatters import formatar_moeda_brl, formatar_percentual
from core.fragility import calcular_fragility_score, reduzir_exposicao_por_fragilidade
from core.m1_quant import calcular_score_m1, classificar_score, Decisao
from core.m2_governance import verificar_limites, hard_fail
from core.m3_context import Confidence, MarketRegime, ajustar_prudencia
from core.market_data import MarketDataService, is_fii
from core.repositories import InvestmentRepository, TransactionRepository
from core.auth import require_auth
from core.styles import (
    bar_track, fmt_brl, fmt_change, inject_css, k_card_with_header,
    section_header, render_navigation, sidebar_engines, sidebar_user, sidebar_ai_qa,
    stat_card, load_page_icon,
    setup_sidebar,
)
from models.investment import Investment, InvestmentType
from models.transaction import Category

st.set_page_config(page_title="Patrimônio · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

repo = InvestmentRepository()

# ── Layout ────────────────────────────────────────────────────────────────────

setup_sidebar()

st.markdown(section_header("Patrimônio", "posições · governança · engines"), unsafe_allow_html=True)

# ── M3 context controls ────────────────────────────────────────────────────
ctx1, ctx2, ctx3 = st.columns(3)
with ctx1:
    regime = MarketRegime(
        st.selectbox("Regime M3", [r.value for r in MarketRegime], index=0)
    )
with ctx2:
    confidence = Confidence(
        st.selectbox("Confidence M3", [c.value for c in Confidence], index=2)
    )
with ctx3:
    caixa_disponivel = st.number_input(
        "Caixa disponível (R$)", min_value=0.0, step=100.0, value=0.0,
    )

# ── Dashboard ao vivo + Cotações (tabs, sempre visíveis) ──────────────────
_tab_live, _tab_quotes = st.tabs(["◉ Ao vivo", "◈ Cotações do portfólio"])

with _tab_live:
    _dash_svc = MarketDataService()
    _dash_portfolio = repo.get_portfolio()

    _dash_refresh_col, _ = st.columns([1, 5])
    with _dash_refresh_col:
        _dash_force = st.button("↺ Atualizar", key="dash_force_btn", use_container_width=True)

    if not _dash_portfolio:
        st.info("Portfólio vazio — adicione ativos no painel abaixo.")
    else:
        # ── Performance strip ─────────────────────────────────────────────
        _dash_tickers_all = [inv.ticker for inv in _dash_portfolio]
        _dash_fiis_all    = [t for t in _dash_tickers_all if is_fii(t)]
        _dash_stocks_all  = [t for t in _dash_tickers_all if not is_fii(t)]
        _bench_tickers    = ["BOVA11", "IFIX11", "IVVB11"]

        try:
            _dsq = _dash_svc.get_stocks_batch(
                _dash_stocks_all + _bench_tickers, force_refresh=_dash_force
            ) if (_dash_stocks_all + _bench_tickers) else {}
            _dfq = _dash_svc.get_fiis_batch(
                _dash_fiis_all, force_refresh=_dash_force
            ) if _dash_fiis_all else {}

            _port_value_now  = sum(
                inv.quantity * (
                    _dfq[inv.ticker].price if inv.ticker in _dfq
                    else _dsq[inv.ticker].price if inv.ticker in _dsq
                    else float(inv.current_price)
                )
                for inv in _dash_portfolio
            )
            _port_change_abs = sum(
                inv.quantity * (
                    _dfq[inv.ticker].change_abs if inv.ticker in _dfq
                    else _dsq[inv.ticker].change_abs if inv.ticker in _dsq
                    else 0.0
                )
                for inv in _dash_portfolio
            )
            _port_value_prev = _port_value_now - _port_change_abs
            _port_change_pct = (_port_change_abs / _port_value_prev * 100) if _port_value_prev else 0.0

            _bova_chg = _dsq.get("BOVA11")
            _ifix_chg = _dsq.get("IFIX11")
            _ivvb_chg = _dsq.get("IVVB11")

            st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:20px">
  {stat_card("Portfólio · hoje", fmt_brl(_port_value_now, compact=True),
         f"{fmt_change(_port_change_pct)} · {fmt_brl(_port_change_abs, compact=True)}",
         "pos" if _port_change_pct >= 0 else "neg")}
  {stat_card("BOVA11 · hoje",
         fmt_change(_bova_chg.change_pct) if _bova_chg else "—",
         fmt_brl(_bova_chg.price) if _bova_chg else "indisponível",
         "pos" if (_bova_chg and _bova_chg.change_pct >= 0) else "neg")}
  {stat_card("IFIX · hoje",
         fmt_change(_ifix_chg.change_pct) if _ifix_chg else "—",
         fmt_brl(_ifix_chg.price) if _ifix_chg else "indisponível",
         "pos" if (_ifix_chg and _ifix_chg.change_pct >= 0) else "neg")}
  {stat_card("IVVB11 · hoje",
         fmt_change(_ivvb_chg.change_pct) if _ivvb_chg else "—",
         fmt_brl(_ivvb_chg.price) if _ivvb_chg else "indisponível",
         "pos" if (_ivvb_chg and _ivvb_chg.change_pct >= 0) else "neg")}
</div>""", unsafe_allow_html=True)

            # ── Posições ao vivo ───────────────────────────────────────────
            _pos_rows = ""
            for inv in sorted(_dash_portfolio, key=lambda x: -x.current_value):
                _q = _dfq.get(inv.ticker) or _dsq.get(inv.ticker)
                if _q:
                    _live_price = _q.price
                    _live_val   = inv.quantity * _live_price
                    _live_gl    = _live_val - float(inv.quantity * inv.avg_price)
                    _chg_c      = "var(--moss)" if _q.change_pct >= 0 else "var(--rust)"
                    _gl_c       = "var(--moss)" if _live_gl >= 0 else "var(--rust)"
                    _gl_sign    = "+" if _live_gl >= 0 else ""
                else:
                    _live_price = float(inv.current_price)
                    _live_val   = float(inv.current_value)
                    _live_gl    = float(inv.gain_loss)
                    _chg_c      = "var(--ink-4)"
                    _gl_c       = "var(--moss)" if _live_gl >= 0 else "var(--rust)"
                    _gl_sign    = "+" if _live_gl >= 0 else ""

                _pos_rows += f"""
<div style="display:grid;grid-template-columns:72px 90px 60px 100px 90px;
  align-items:center;gap:10px;padding:8px 0;border-top:1px solid var(--rule)">
  <span class="mono" style="font-size:12px;color:var(--brass)">{inv.ticker}</span>
  <span class="mono" style="font-size:13px;color:var(--ink);text-align:right">{fmt_brl(_live_price)}</span>
  <span class="mono" style="font-size:11px;color:{_chg_c};text-align:right">{fmt_change(_q.change_pct) if _q else "—"}</span>
  <span class="mono" style="font-size:12px;color:var(--ink-2);text-align:right">{fmt_brl(_live_val, compact=True)}</span>
  <span class="mono" style="font-size:11px;color:{_gl_c};text-align:right">{_gl_sign}{fmt_brl(_live_gl, compact=True)}</span>
</div>"""

            _pos_header = (
                '<div style="display:grid;grid-template-columns:72px 90px 60px 100px 90px;'
                'gap:10px;padding-bottom:4px">'
                '<span style="font-size:10px;color:var(--ink-4)">Ticker</span>'
                '<span style="font-size:10px;color:var(--ink-4);text-align:right">Preço</span>'
                '<span style="font-size:10px;color:var(--ink-4);text-align:right">Var.%</span>'
                '<span style="font-size:10px;color:var(--ink-4);text-align:right">Valor</span>'
                '<span style="font-size:10px;color:var(--ink-4);text-align:right">G/L total</span>'
                '</div>'
            )
            st.markdown(
                k_card_with_header("Posições ao vivo", _pos_header + _pos_rows,
                                   f"{len(_dash_portfolio)} ativos · {fmt_brl(_port_value_now, compact=True)}"),
                unsafe_allow_html=True,
            )

        except Exception:
            st.info("Cotações ao vivo indisponíveis — verifique a conexão.")

        # ── Feed de rendimentos (últimos 60 dias) ─────────────────────────
        try:
            from datetime import date as _date, timedelta
            _today = _date.today()
            _tx_repo = TransactionRepository()

            _rend_txs = []
            for _mo in [_today.month, (_today.month - 1) or 12]:
                _yr = _today.year if _mo <= _today.month else _today.year - 1
                try:
                    _rend_txs += [
                        t for t in _tx_repo.list_by_month(_yr, _mo)
                        if t.category == Category.RENDA
                    ]
                except Exception:
                    pass

            _rend_txs.sort(key=lambda t: t.date, reverse=True)

            if _rend_txs:
                _rend_rows = ""
                _rend_total = sum(float(t.amount) for t in _rend_txs)
                for _rt in _rend_txs[:20]:
                    _rend_rows += f"""
<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-top:1px solid var(--rule)">
  <div style="width:32px;height:32px;border-radius:50%;background:rgba(123,198,138,0.12);
display:flex;align-items:center;justify-content:center;flex-shrink:0">
<span style="font-size:14px">$</span>
  </div>
  <div style="flex:1;min-width:0">
<div style="font-family:var(--font-sans);font-size:12px;color:var(--ink);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{_html_esc(_rt.notes or _rt.category.value)}</div>
<div style="font-family:var(--font-sans);font-size:10px;color:var(--ink-4)">
  {_rt.date.strftime('%d/%b').lower()}</div>
  </div>
  <span class="mono" style="font-size:13px;color:var(--moss);flex-shrink:0">+{fmt_brl(float(_rt.amount))}</span>
</div>"""

                st.markdown(
                    k_card_with_header(
                        "Feed de rendimentos", _rend_rows,
                        f"{len(_rend_txs)} pagamentos · {fmt_brl(_rend_total, compact=True)} total",
                    ),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    k_card_with_header(
                        "Feed de rendimentos",
                        '<div style="padding:20px 0;text-align:center;color:var(--ink-4);font-size:12px">'
                        'Nenhum rendimento nos últimos 60 dias.<br>'
                        'Importe extratos BTG na página Importar para popular este feed.</div>',
                        "últimos 60 dias",
                    ),
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

with _tab_quotes:
    # ── Cotações portfólio + benchmarks ───────────────────────────────────
    _svc_pt = MarketDataService()
    _pt_col, _ = st.columns([1, 4])
    with _pt_col:
        _pt_force = st.button("↺ Atualizar", key="cotacoes_pt_refresh", use_container_width=True)

    _pt_tickers = [inv.ticker for inv in repo.get_portfolio()]
    _bench = ["BOVA11", "SMAL11", "IVVB11"]
    _pt_all = list(dict.fromkeys(_pt_tickers + _bench))
    _pt_fiis   = [t for t in _pt_all if is_fii(t)]
    _pt_stocks = [t for t in _pt_all if not is_fii(t)]

    def _quote_row(ticker: str, q, fii_q=None) -> str:
        if q is None and fii_q is None:
            return (
                f'<div style="display:grid;grid-template-columns:80px 100px 70px 70px 70px 80px;'
                f'gap:10px;padding:8px 0;border-top:1px solid var(--rule)">'
                f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--brass)">{ticker}</span>'
                f'<span style="font-size:11px;color:var(--ink-4)">indisponível</span></div>'
            )
        item = fii_q or q
        chg_color = "var(--moss)" if item.change_pct >= 0 else "var(--rust)"
        dy   = f"{fii_q.dy_12m:.2f}%" if fii_q and fii_q.dy_12m > 0 else "—"
        pvp  = f"{fii_q.pvp:.3f}" if fii_q and fii_q.pvp > 0 else "—"
        rend = fmt_brl(fii_q.last_income) if fii_q and fii_q.last_income > 0 else "—"
        return (
            f'<div style="display:grid;grid-template-columns:80px 100px 70px 70px 70px 80px;'
            f'align-items:center;gap:10px;padding:8px 0;border-top:1px solid var(--rule)">'
            f'<span style="font-family:var(--font-mono);font-size:12px;color:var(--brass)">{ticker}</span>'
            f'<span style="font-family:var(--font-mono);font-size:13px;color:var(--ink);text-align:right">{fmt_brl(item.price)}</span>'
            f'<span style="font-family:var(--font-mono);font-size:12px;color:{chg_color};text-align:right">{fmt_change(item.change_pct)}</span>'
            f'<span style="font-family:var(--font-mono);font-size:11px;color:var(--sea);text-align:right">{dy}</span>'
            f'<span style="font-family:var(--font-mono);font-size:11px;color:var(--ink-3);text-align:right">{pvp}</span>'
            f'<span style="font-family:var(--font-mono);font-size:11px;color:var(--ink-3);text-align:right">{rend}</span>'
            f'</div>'
        )

    _pt_header = (
        '<div style="display:grid;grid-template-columns:80px 100px 70px 70px 70px 80px;'
        'gap:10px;padding-bottom:4px">'
        '<span style="font-size:10px;color:var(--ink-4)">Ticker</span>'
        '<span style="font-size:10px;color:var(--ink-4);text-align:right">Preço</span>'
        '<span style="font-size:10px;color:var(--ink-4);text-align:right">Var.%</span>'
        '<span style="font-size:10px;color:var(--ink-4);text-align:right">DY 12M</span>'
        '<span style="font-size:10px;color:var(--ink-4);text-align:right">P/VP</span>'
        '<span style="font-size:10px;color:var(--ink-4);text-align:right">Ult. Rend.</span>'
        '</div>'
    )

    try:
        _pt_sq = _svc_pt.get_stocks_batch(_pt_stocks, force_refresh=_pt_force) if _pt_stocks else {}
        _pt_fq = _svc_pt.get_fiis_batch(_pt_fiis, force_refresh=_pt_force) if _pt_fiis else {}
        _pt_rows = ""
        for t in _pt_all:
            if is_fii(t):
                _pt_rows += _quote_row(t, None, _pt_fq.get(t))
            else:
                _pt_rows += _quote_row(t, _pt_sq.get(t))
        st.markdown(
            k_card_with_header("Portfólio + Benchmarks", _pt_header + _pt_rows, f"{len(_pt_all)} ativos"),
            unsafe_allow_html=True,
        )
    except Exception:
        st.info("Cotações indisponíveis no momento.")

# ── Adicionar / Atualizar ativo (form colapsável) ──────────────────────────
with st.expander("+ Adicionar / Atualizar ativo"):
    # ── Ticker lookup — fora do st.form para reatividade ───────────────
    _lk_c1, _lk_c2, _lk_c3 = st.columns([2, 1, 2])
    with _lk_c1:
        _lk_ticker = st.text_input(
            "Buscar cotação", key="inv_lk_ticker",
            placeholder="ex: MXRF11, PETR4",
        ).upper().strip()
    with _lk_c2:
        st.markdown('<div style="height:1.75rem"></div>', unsafe_allow_html=True)
        _lk_force = st.button("◈ Buscar", key="inv_lk_btn", use_container_width=True)

    _lk_price: float = 0.01
    _lk_dy: float    = 0.0
    _lk_pvp: float   = 0.0

    if _lk_ticker:
        try:
            _svc_lk = MarketDataService()
            if is_fii(_lk_ticker):
                _fq_lk = _svc_lk.get_fiis_batch(
                    [_lk_ticker], force_refresh=_lk_force
                ).get(_lk_ticker)
                if _fq_lk:
                    _lk_price = float(_fq_lk.price)
                    _lk_dy    = float(_fq_lk.dy_12m)
                    _lk_pvp   = float(_fq_lk.pvp)
                    _cc = "var(--moss)" if _fq_lk.change_pct >= 0 else "var(--rust)"
                    st.markdown(f"""
<div style="display:flex;gap:20px;align-items:center;padding:10px 14px;margin-bottom:10px;
  background:rgba(217,178,111,0.05);border:1px solid var(--rule-brass);border-radius:var(--radius-xs)">
  <span class="mono" style="font-size:13px;color:var(--brass);font-weight:600">{_lk_ticker}</span>
  <span class="mono" style="font-size:15px;color:var(--ink)">{fmt_brl(_fq_lk.price)}</span>
  <span class="mono" style="font-size:12px;color:{_cc}">{fmt_change(_fq_lk.change_pct)}</span>
  <span style="font-size:11px;color:var(--ink-4)">DY {_lk_dy:.2f}% · P/VP {_lk_pvp:.3f} · Rend. {fmt_brl(_fq_lk.last_income)}</span>
</div>""", unsafe_allow_html=True)
            else:
                _sq_lk = _svc_lk.get_stocks_batch(
                    [_lk_ticker], force_refresh=_lk_force
                ).get(_lk_ticker)
                if _sq_lk:
                    _lk_price = float(_sq_lk.price)
                    _cc = "var(--moss)" if _sq_lk.change_pct >= 0 else "var(--rust)"
                    st.markdown(f"""
<div style="display:flex;gap:20px;align-items:center;padding:10px 14px;margin-bottom:10px;
  background:rgba(217,178,111,0.05);border:1px solid var(--rule-brass);border-radius:var(--radius-xs)">
  <span class="mono" style="font-size:13px;color:var(--brass);font-weight:600">{_lk_ticker}</span>
  <span class="mono" style="font-size:15px;color:var(--ink)">{fmt_brl(_sq_lk.price)}</span>
  <span class="mono" style="font-size:12px;color:{_cc}">{fmt_change(_sq_lk.change_pct)}</span>
</div>""", unsafe_allow_html=True)
        except Exception:
            st.caption("Cotação indisponível — preencha o preço manualmente.")

    # ── Formulário ────────────────────────────────────────────────────────
    with st.form("form_investimento", clear_on_submit=True):
        fi1, fi2 = st.columns(2)
        with fi1:
            ticker      = st.text_input("Ticker (ex: MXRF11)").upper()
            tipo        = st.selectbox("Tipo", [t.value for t in InvestmentType])
            setor       = st.text_input("Setor")
            quantidade  = st.number_input("Cotas", min_value=0.01, step=1.0)
            preco_medio = st.number_input("Preço médio (R$)", min_value=0.01, step=0.01, format="%.2f")
            preco_atual = st.number_input(
                "Preço atual (R$)", value=_lk_price, min_value=0.01, step=0.01, format="%.2f",
            )
        with fi2:
            dy_12m       = st.number_input("DY 12m (%)", value=_lk_dy, min_value=0.0, step=0.1, format="%.2f")
            pvp          = st.number_input("P/VP", value=_lk_pvp, min_value=0.0, step=0.01, format="%.4f")
            liquidez     = st.number_input("Liquidez diária (R$)", min_value=0.0, step=1000.0)
            volatilidade = st.slider("Volatilidade anual (%)", 0.0, 60.0, 10.0, 0.5)
            spread_cdi   = st.slider("Spread vs CDI (p.p.)", -5.0, 10.0, 2.0, 0.25)
            notas_inv    = st.text_area("Notas")
        if st.form_submit_button("Salvar ativo", type="primary", use_container_width=True):
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

# ── Load portfolio ─────────────────────────────────────────────────────────
try:
    portfolio = repo.get_portfolio()
except Exception as e:
    st.error(f"Erro ao carregar portfólio: {e}")
    st.stop()

if not portfolio:
    st.markdown(
        '<div style="padding:64px 0;text-align:center;color:var(--ink-4)">portfólio vazio · adicione o primeiro ativo acima</div>',
        unsafe_allow_html=True,
    )
    st.stop()

total_portfolio = sum(inv.current_value for inv in portfolio)
total_gl        = sum(inv.gain_loss for inv in portfolio)
gl_pct          = (total_gl / (total_portfolio - total_gl) * 100) if (total_portfolio - total_gl) != 0 else 0

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
rows = []
decisao_counts = {"COMPRAR": 0, "MANTER": 0, "REDUZIR": 0}

for inv in portfolio:
    peso_pct    = (inv.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
    score_m1    = calcular_score_m1(
        dy=inv.dy_12m, pvp=inv.pvp, liquidez=inv.liquidity_daily,
        volatilidade=inv.volatility, spread_cdi=inv.spread_vs_cdi,
    )
    score_ajust = ajustar_prudencia(score_m1, regime, confidence)
    fragility   = calcular_fragility_score(inv, peso_portfolio_pct=peso_pct)
    score_final = reduzir_exposicao_por_fragilidade(score_ajust, fragility.total)
    decisao     = classificar_score(score_final)
    decisao_counts[decisao.value] += 1

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
    df = pd.DataFrame(rows)
    st.markdown(k_card_with_header("Posições", "", f"{len(portfolio)} ativos"), unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True, height=400)

with col_right:
    by_type: dict[str, float] = {}
    for inv in portfolio:
        by_type[inv.type.value] = by_type.get(inv.type.value, 0) + inv.current_value

    type_colors = {
        "FII": "#D9B26F", "ACAO": "#7FB3C8", "RENDA_FIXA": "#7BC68A",
        "CRIPTO": "#E08855", "INTERNACIONAL": "#C9BC9E", "OUTRO": "#5C5746",
    }
    sorted_types = sorted(by_type.items(), key=lambda x: x[1], reverse=True)

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
    st.plotly_chart(fig, use_container_width=True)

    leg_rows = "".join(
        f'<div style="display:grid;grid-template-columns:10px 1fr auto;align-items:center;gap:10px;font-size:12px;padding:4px 0">'
        f'<span style="width:10px;height:10px;border-radius:2px;background:{type_colors.get(t,"#5C5746")};display:inline-block"></span>'
        f'<span style="color:var(--ink-3)">{t}</span>'
        f'<span class="mono" style="font-size:11px;color:var(--ink-2)">{v/total_portfolio*100:.0f}%</span>'
        f'</div>'
        for t, v in sorted_types
    )
    st.markdown(f'<div style="padding:0 4px">{leg_rows}</div>', unsafe_allow_html=True)

# ── Rentabilidade & Risco/Retorno ──────────────────────────────────────────────
st.markdown(section_header("Análise do Portfólio", "rentabilidade · risco · retorno"), unsafe_allow_html=True)

tab_rent, tab_bolha, tab_tesouro = st.tabs([
    "📈 Rentabilidade vs Benchmarks", "◎ Mapa Risco/Retorno", "🏛 Tesouro Histórico"
])

with tab_rent:
    _BENCH_TICKERS = ["BOVA11", "IFIX11"]
    _port_tickers = [inv.ticker for inv in portfolio]

    with st.spinner("Carregando histórico…"):
        _price_hist = svc.get_price_history(_port_tickers + _BENCH_TICKERS, days=30)

    # Histórico sintético do portfólio: valor diário baseado nos preços individuais
    _port_dates: list = []
    if portfolio and _price_hist:
        _first_ticker = next((t for t in _port_tickers if t in _price_hist), None)
        if _first_ticker:
            _port_dates = [e["date"] for e in _price_hist[_first_ticker]]

    _port_hist_line: list[dict] = []
    for _d in _port_dates:
        _val = sum(
            float(inv.quantity) * next(
                (e["close"] for e in _price_hist.get(inv.ticker, []) if e["date"] == _d),
                float(inv.current_price),
            )
            for inv in portfolio
        )
        _port_hist_line.append({"date": _d, "valor": _val})

    _bench_hist = {t: _price_hist[t] for t in _BENCH_TICKERS if t in _price_hist}
    _linha_data = preparar_dados_linha_normalizado(_port_hist_line, _bench_hist)

    if _linha_data:
        _line_colors = {"Portfólio": "#00C896", "BOVA11": "#4D8DFF", "IFIX11": "#D9B26F"}
        _fig_linha = go.Figure()
        _series = [k for k in _linha_data[0].keys() if k != "date"]
        for _s in _series:
            _fig_linha.add_trace(go.Scatter(
                x=[r["date"] for r in _linha_data],
                y=[r[_s] for r in _linha_data],
                name=_s,
                mode="lines",
                line=dict(color=_line_colors.get(_s, "#888888"), width=2),
                hovertemplate=f"{_s}: %{{y:.1f}}<extra></extra>",
            ))
        _fig_linha.update_layout(
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(showgrid=False, color="#888"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                       color="#888", ticksuffix=""),
            hovermode="x unified",
        )
        _fig_linha.add_hline(y=100, line_dash="dot", line_color="rgba(255,255,255,0.2)")
        st.plotly_chart(_fig_linha, use_container_width=True)
        st.caption("Base 100 no início do período · últimos 30 dias úteis")
    else:
        st.info("Sem histórico disponível para o portfólio atual.")

with tab_bolha:
    _bolha_data = preparar_dados_bolha(portfolio, total_portfolio)
    if _bolha_data:
        _tipo_colors = {
            "FII": "#D9B26F", "Ação": "#7FB3C8", "Renda Fixa": "#7BC68A",
            "Caixa": "#5C5746",
        }
        _fig_bolha = go.Figure()
        _tipos_uniq = list({r["tipo"] for r in _bolha_data})
        for _tipo in _tipos_uniq:
            _subset = [r for r in _bolha_data if r["tipo"] == _tipo]
            _fig_bolha.add_trace(go.Scatter(
                x=[r["dy_12m"] for r in _subset],
                y=[r["pvp"] for r in _subset],
                mode="markers+text",
                name=_tipo,
                text=[r["ticker"] for r in _subset],
                textposition="top center",
                textfont=dict(size=10, color="#F2EAD3"),
                marker=dict(
                    size=[max(10, r["peso_pct"] * 3) for r in _subset],
                    color=_tipo_colors.get(_tipo, "#888888"),
                    opacity=0.85,
                    line=dict(color="rgba(0,0,0,0.2)", width=1),
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "DY 12m: %{x:.1f}%<br>"
                    "P/VP: %{y:.2f}<br>"
                    "Peso: %{customdata:.1f}%<extra></extra>"
                ),
                customdata=[r["peso_pct"] for r in _subset],
            ))
        _fig_bolha.update_layout(
            height=380,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(title="DY 12m (%)", showgrid=True,
                       gridcolor="rgba(255,255,255,0.05)", color="#888"),
            yaxis=dict(title="P/VP", showgrid=True,
                       gridcolor="rgba(255,255,255,0.05)", color="#888"),
            hovermode="closest",
        )
        _fig_bolha.add_hline(y=1.0, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                             annotation_text="P/VP = 1", annotation_font_color="#888")
        st.plotly_chart(_fig_bolha, use_container_width=True)
        st.caption("Tamanho da bolha = peso no portfólio · DY × P/VP — ativos com DY=0 e P/VP=0 excluídos")
    else:
        st.info("Sem ativos com dados fundamentais disponíveis (DY e P/VP).")

with tab_tesouro:
    _TD_BONDS_DEFAULT = [
        "Tesouro IPCA+ 2029", "Tesouro IPCA+ 2035",
        "Tesouro Prefixado 2027", "Tesouro Selic 2027",
    ]
    _bond_sel = st.selectbox(
        "Título",
        _TD_BONDS_DEFAULT,
        key="td_bond_sel",
        label_visibility="collapsed",
    )
    with st.spinner("Carregando histórico do Tesouro…"):
        _td_hist_raw = svc.get_tesouro_history(bond_type=_bond_sel)

    _td_data = preparar_dados_tesouro_historico(_td_hist_raw, _bond_sel)

    if _td_data:
        _col_taxa, _col_preco = st.columns(2, gap="medium")

        with _col_taxa:
            _fig_taxa = go.Figure(go.Scatter(
                x=[r["date"] for r in _td_data],
                y=[r["Taxa (%)"] for r in _td_data],
                mode="lines",
                line=dict(color="#00C896", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,200,150,0.08)",
                hovertemplate="%{x}<br>Taxa: %{y:.2f}%<extra></extra>",
            ))
            _fig_taxa.update_layout(
                title=dict(text="Taxa de Compra (%)", font_size=13, font_color="#888"),
                height=240,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(showgrid=False, color="#888"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                           color="#888", ticksuffix="%"),
            )
            st.plotly_chart(_fig_taxa, use_container_width=True)

        with _col_preco:
            _fig_preco = go.Figure(go.Scatter(
                x=[r["date"] for r in _td_data],
                y=[r["Preço (R$)"] for r in _td_data],
                mode="lines",
                line=dict(color="#4D8DFF", width=2),
                fill="tozeroy",
                fillcolor="rgba(77,141,255,0.08)",
                hovertemplate="%{x}<br>PU: R$ %{y:,.2f}<extra></extra>",
            ))
            _fig_preco.update_layout(
                title=dict(text="Preço Unitário (PU Compra)", font_size=13, font_color="#888"),
                height=240,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(showgrid=False, color="#888"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                           color="#888", tickprefix="R$ "),
            )
            st.plotly_chart(_fig_preco, use_container_width=True)

        _latest = _td_data[-1]
        _oldest = _td_data[0]
        _delta_taxa = _latest["Taxa (%)"] - _oldest["Taxa (%)"]
        _dir = "↑" if _delta_taxa > 0 else "↓"
        _cor = "var(--rust)" if _delta_taxa > 0 else "var(--moss)"
        st.markdown(
            f'<p style="font-size:12px;color:var(--ink-2);margin-top:-8px">'
            f'{_oldest["date"]} → {_latest["date"]} &nbsp;|&nbsp; '
            f'Taxa: <span style="color:{_cor}">{_dir} {abs(_delta_taxa):.2f}pp</span> &nbsp;|&nbsp; '
            f'PU atual: <span style="color:var(--ink-3)">R$ {_latest["Preço (R$)"]:,.2f}</span>'
            f'</p>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"Sem histórico disponível para **{_bond_sel}**. Verifique a conexão ou tente outro título.")

# ── M2 Governance ─────────────────────────────────────────────────────────────
st.markdown(section_header("Governance · M2", "beginner mode · limites duros"), unsafe_allow_html=True)

col_gov, col_bs = st.columns(2, gap="large")

with col_gov:
    max_asset_pct = max(
        (inv.current_value / total_portfolio * 100) for inv in portfolio
    ) if portfolio else 0
    max_asset_inv = max(portfolio, key=lambda i: i.current_value, default=None)

    by_sector: dict[str, float] = {}
    for inv in portfolio:
        s = inv.sector or inv.type.value
        by_sector[s] = by_sector.get(s, 0) + (inv.current_value / total_portfolio * 100)
    max_thesis_pct = max(by_sector.values()) if by_sector else 0

    caixa_pct_gov = (caixa_disponivel / (total_portfolio + caixa_disponivel) * 100) if (total_portfolio + caixa_disponivel) > 0 else 0

    gov_items = [
        ("Max por ativo",  max_asset_pct,  10.0, max_asset_inv.ticker if max_asset_inv else "—"),
        ("Max por tese",   max_thesis_pct, 25.0, max((by_sector or {"—": 0}), key=by_sector.get)),
        ("Caixa mínimo",   caixa_pct_gov,  20.0, "M2 floor"),
    ]

    gov_rows = []
    for label_g, val, limit, ref in gov_items:
        ok   = val <= limit if label_g != "Caixa mínimo" else val >= limit
        sc   = "var(--moss)" if ok else "var(--rust)"
        tick = "✓" if ok else "✗"
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
    st.markdown(
        f'<div style="font-family:var(--font-mono);font-size:10px;color:var(--ink-4);'
        f'font-style:italic;margin-bottom:8px">{PERGUNTA_OBRIGATORIA}</div>',
        unsafe_allow_html=True,
    )
    ticker_sel = st.selectbox("Ativo para análise Anti-BS", [inv.ticker for inv in portfolio],
                               label_visibility="collapsed")
    inv_sel    = next(inv for inv in portfolio if inv.ticker == ticker_sel)
    peso_sel   = (inv_sel.current_value / total_portfolio * 100) if total_portfolio > 0 else 0
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
