"""Orçamento · Klipper — orçamentos, meta de poupança, score e alertas."""

from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core.analytics import calcular_saldo_mensal
from core.behavioral import (
    _gastos_por_categoria,
    calcular_score_financeiro,
    calcular_uso_orcamento,
    detectar_alertas_padrao,
)
from core.repositories import (
    BudgetRepository, InstallmentRepository,
    InvestmentRepository, TransactionRepository,
)
from core.auth import require_auth
from core.styles import (
    bar_track, budget_bar, fmt_brl, inject_css, k_card_with_header,
    metric_card, score_circle, section_header,
    sidebar_engines, sidebar_user, sidebar_ai_qa, render_navigation, stat_card, load_page_icon,
)
from models.budget import Budget
from models.transaction import Category

st.set_page_config(page_title="Orçamento · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

tx_repo   = TransactionRepository()
inst_repo = InstallmentRepository()
bud_repo  = BudgetRepository()
inv_repo  = InvestmentRepository()

hoje = date.today()

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
    # ── Budget form inline ────────────────────────────────────────────────────
    with st.expander("+ Configurar orçamento"):
        with st.form("form_budget"):
            bf1, bf2 = st.columns(2)
            with bf1:
                cat_bud    = st.selectbox("Categoria", [c.value for c in Category])
                limite_bud = st.number_input("Limite mensal (R$)", min_value=0.01, step=10.0, format="%.2f")
            with bf2:
                ano_bud    = st.number_input("Ano", min_value=2020, max_value=2030, value=hoje.year)
                mes_bud    = st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                                           format_func=lambda m: calendar.month_abbr[m], key="mes_bud")
            if st.form_submit_button("Salvar", type="primary", use_container_width=True):
                try:
                    bud_repo.upsert(Budget(
                        category=cat_bud, monthly_limit=limite_bud,
                        year=int(ano_bud), month=int(mes_bud),
                    ))
                    st.success("Orçamento salvo.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(section_header("Orçamento & Score", "comportamento financeiro"), unsafe_allow_html=True)

    f1, f2 = st.columns([1, 1])
    with f1:
        ano = int(st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1),
                               label_visibility="collapsed"))
    with f2:
        mes = int(st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                               format_func=lambda m: calendar.month_abbr[m],
                               label_visibility="collapsed"))

    # ── Load data ─────────────────────────────────────────────────────────────
    try:
        transacoes   = tx_repo.list_by_month(ano, mes)
        installments = inst_repo.list_active()
        budgets      = bud_repo.list_by_month(ano, mes)
        portfolio    = inv_repo.get_portfolio()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()

    transacoes_3m: list = []
    for delta in range(1, 4):
        m_prev = mes - delta
        y_prev = ano
        while m_prev < 1:
            m_prev += 12
            y_prev -= 1
        try:
            transacoes_3m.extend(tx_repo.list_by_month(y_prev, m_prev))
        except Exception:
            pass

    saldo           = calcular_saldo_mensal(transacoes, ano, mes)
    total_portfolio = sum(inv.current_value for inv in portfolio)
    total_ativos    = saldo.total_ganhos + total_portfolio
    caixa_pct       = (saldo.saldo / total_ativos * 100) if total_ativos > 0 else 0.0

    # ── KPI strip ─────────────────────────────────────────────────────────────
    n_ok     = sum(1 for b in budgets if True)  # placeholder; computed after status
    status_list = calcular_uso_orcamento(transacoes, budgets) if budgets else []
    n_estouro   = sum(1 for s in status_list if s.status == "ESTOURO")
    n_alerta    = sum(1 for s in status_list if s.status == "ALERTA")

    score = calcular_score_financeiro(
        transacoes=transacoes,
        budgets=budgets,
        installments=installments,
        taxa_poupanca_atual=saldo.taxa_poupanca,
        meta_poupanca=20.0,
        caixa_pct=caixa_pct,
        transacoes_3_meses=transacoes_3m,
    )

    score_color = "pos" if score.total >= 80 else "brass" if score.total >= 60 else "warn" if score.total >= 40 else "neg"

    st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:20px">
  {stat_card("Orçamentos ativos", str(len(budgets)), f"{n_estouro} estouro · {n_alerta} alerta")}
  {stat_card("Taxa de poupança", f"{saldo.taxa_poupanca:.1f}%",
             "atingiu meta 20%" if saldo.taxa_poupanca >= 20 else "abaixo da meta",
             "pos" if saldo.taxa_poupanca >= 20 else "neg")}
  {stat_card("Score financeiro", str(score.total),
             "excelente" if score.total >= 80 else "bom" if score.total >= 60 else "atenção" if score.total >= 40 else "crítico",
             score_color)}
  {stat_card("Caixa M2", f"{caixa_pct:.1f}%",
             "acima do mínimo 20%" if caixa_pct >= 20 else "abaixo do mínimo M2",
             "pos" if caixa_pct >= 20 else "neg")}
</div>
""", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_orc, tab_meta, tab_score_tab, tab_alertas = st.tabs(
        ["Orçamentos", "Meta de Poupança", "Score Financeiro", "Alertas de Padrão"]
    )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — Orçamentos
    # ══════════════════════════════════════════════════════════════════════════
    with tab_orc:
        if budgets:
            col_bars, col_summary = st.columns([2, 1], gap="large")

            with col_bars:
                st.markdown(k_card_with_header("Controle de gastos", "", "mês corrente"), unsafe_allow_html=True)
                for s in status_list:
                    tone  = "neg" if s.status == "ESTOURO" else "warn" if s.status == "ALERTA" else "pos"
                    sc    = "var(--rust)" if s.status == "ESTOURO" else "var(--lantern)" if s.status == "ALERTA" else "var(--moss)"
                    lbl   = s.status
                    st.markdown(f"""<div style="margin-bottom:16px">
  <div style="display:flex;justify-content:space-between;font-family:var(--font-sans);font-size:13px;margin-bottom:6px">
    <span style="color:var(--ink);font-weight:500">{s.category}</span>
    <span style="display:flex;align-items:center;gap:8px">
      <span class="mono" style="font-size:12px;color:var(--ink-2)">{fmt_brl(s.gasto, compact=True)} / {fmt_brl(s.limite, compact=True)}</span>
      <span style="font-family:var(--font-sans);font-size:10px;color:{sc};font-weight:600;letter-spacing:0.08em">{lbl}</span>
    </span>
  </div>
  {bar_track(s.gasto, s.limite, tone)}
  <div style="text-align:right;margin-top:4px;font-family:var(--font-mono);font-size:10px;color:{sc}">{s.pct:.1f}%</div>
</div>""", unsafe_allow_html=True)

            with col_summary:
                total_limite_bud = sum(b.monthly_limit for b in budgets)
                total_gasto_bud  = sum(s.gasto for s in status_list)
                pct_overall      = (total_gasto_bud / total_limite_bud * 100) if total_limite_bud > 0 else 0
                tone_overall     = "neg" if pct_overall >= 100 else "warn" if pct_overall >= 80 else "pos"

                summary_html = f"""
<div class="k-metric" style="margin-bottom:16px">
  <div class="k-kicker">Total orçado</div>
  <div class="k-metric-v">{fmt_brl(total_limite_bud, compact=True)}</div>
  <div class="k-metric-d pos">{fmt_brl(total_limite_bud - total_gasto_bud, compact=True)} disponível</div>
</div>
<div class="k-metric" style="margin-bottom:16px">
  <div class="k-kicker">Total gasto</div>
  <div class="k-metric-v {'neg' if pct_overall >= 100 else 'warn' if pct_overall >= 80 else ''}">{fmt_brl(total_gasto_bud, compact=True)}</div>
  <div class="k-metric-d">{pct_overall:.0f}% do limite</div>
</div>
{bar_track(total_gasto_bud, total_limite_bud, tone_overall)}
"""
                st.markdown(k_card_with_header("Resumo", summary_html), unsafe_allow_html=True)

                with st.expander("Remover orçamento"):
                    opts = {f"{b.category} ({calendar.month_abbr[b.month]}/{b.year})": b.id for b in budgets}
                    sel  = st.selectbox("Selecione", list(opts.keys()), key="del_bud",
                                         label_visibility="collapsed")
                    if st.button("Remover", key="btn_del_bud"):
                        try:
                            bud_repo.delete(opts[sel])
                            st.success("Orçamento removido.")
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
        else:
            st.markdown(
                '<div style="padding:48px 0;text-align:center;color:var(--ink-4)">nenhum orçamento configurado · use o formulário acima</div>',
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — Meta de Poupança
    # ══════════════════════════════════════════════════════════════════════════
    with tab_meta:
        col_meta, col_hist = st.columns([1, 2], gap="large")

        with col_meta:
            meta_poupanca = st.slider("Meta de poupança (%)", 0, 50, 20, step=5)
            poupanca_real = saldo.taxa_poupanca
            tone_m        = "pos" if poupanca_real >= meta_poupanca else "neg"
            meta_html = f"""
<div class="k-metric" style="margin-bottom:12px">
  <div class="k-kicker">Taxa de poupança real</div>
  <div class="k-metric-v {tone_m}" style="font-size:40px">{poupanca_real:.1f}%</div>
  <div class="k-metric-d">meta: {meta_poupanca}%</div>
</div>
{bar_track(poupanca_real, 50)}
<div style="margin-top:10px;font-family:var(--font-sans);font-size:12px;color:{'var(--moss)' if poupanca_real >= meta_poupanca else 'var(--rust)'}">
  {'Meta atingida' if poupanca_real >= meta_poupanca else f'Faltam {meta_poupanca - poupanca_real:.1f}pp para a meta'}
</div>
"""
            st.markdown(k_card_with_header("Poupança", meta_html, "mês selecionado"), unsafe_allow_html=True)

        with col_hist:
            historico = []
            for delta in range(5, -1, -1):
                m_h = mes - delta
                y_h = ano
                while m_h < 1:
                    m_h += 12
                    y_h -= 1
                try:
                    txs_h = tx_repo.list_by_month(y_h, m_h)
                    sal_h = calcular_saldo_mensal(txs_h, y_h, m_h)
                    historico.append({
                        "Mês": f"{calendar.month_abbr[m_h]}/{y_h}",
                        "Poupança (%)": sal_h.taxa_poupanca,
                    })
                except Exception:
                    pass

            if historico:
                df_hist = pd.DataFrame(historico)
                fig = px.line(df_hist, x="Mês", y="Poupança (%)", markers=True)
                fig.add_hline(y=meta_poupanca, line_dash="dash", line_color="#D87C6A",
                              annotation_text=f"Meta {meta_poupanca}%",
                              annotation_font_color="#D87C6A")
                fig.update_traces(line_color="#D9B26F", marker_color="#D9B26F")
                fig.update_layout(
                    height=300, margin=dict(l=0, r=0, t=24, b=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                               tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                    font={"color": "#C9BC9E"},
                )
                st.markdown(k_card_with_header("Histórico 6 meses", "", "evolução da poupança"), unsafe_allow_html=True)
                st.plotly_chart(fig, width='stretch')

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — Score Financeiro
    # ══════════════════════════════════════════════════════════════════════════
    with tab_score_tab:
        meta_score = st.slider("Meta de poupança para score (%)", 0, 50, 20, step=5, key="meta_score")

        score_full = calcular_score_financeiro(
            transacoes=transacoes, budgets=budgets, installments=installments,
            taxa_poupanca_atual=saldo.taxa_poupanca, meta_poupanca=float(meta_score),
            caixa_pct=caixa_pct, transacoes_3_meses=transacoes_3m,
        )

        col_gauge, col_break = st.columns([1, 2], gap="large")

        with col_gauge:
            score_circle(score_full.total)
            label = (
                "EXCELENTE" if score_full.total >= 80 else
                "BOM" if score_full.total >= 60 else
                "ATENÇÃO" if score_full.total >= 40 else "CRÍTICO"
            )
            lc = "var(--moss)" if score_full.total >= 80 else "var(--brass)" if score_full.total >= 60 else "var(--lantern)" if score_full.total >= 40 else "var(--rust)"
            st.markdown(
                f'<div style="text-align:center;font-family:var(--font-sans);font-size:12px;'
                f'letter-spacing:0.16em;color:{lc};font-weight:600">{label}</div>',
                unsafe_allow_html=True,
            )

        with col_break:
            criterios = [
                ("Orçamento (todas as cat.)",       "orcamento", 30),
                ("Meta de poupança atingida",        "poupanca",  25),
                ("Caixa M2 ≥ 20%",                  "caixa",     20),
                ("Sem gasto acima da média 3 meses", "media",     15),
                ("Sem parcela atrasada",             "parcelas",  10),
            ]
            rows_html = []
            for label_c, key, max_pts in criterios:
                pts     = score_full.detalhes.get(key, 0)
                sc_tone = "pos" if pts > 0 else "neg"
                sc_col  = "var(--moss)" if pts > 0 else "var(--rust)"
                tick    = "✓" if pts > 0 else "✗"
                rows_html.append(f"""<div style="margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;font-family:var(--font-sans);font-size:12px;margin-bottom:6px">
    <span style="color:{'var(--ink)' if pts > 0 else 'var(--ink-3)'}">{tick} {label_c}</span>
    <span class="mono" style="color:{sc_col};font-size:11px">{pts}/{max_pts}</span>
  </div>
  {bar_track(pts, max_pts, sc_tone)}
</div>""")
            st.markdown(
                k_card_with_header("Breakdown", "".join(rows_html), "critérios do score"),
                unsafe_allow_html=True,
            )

        # Historical score chart
        st.markdown(section_header("Histórico do Score", "6 meses"), unsafe_allow_html=True)
        hist_score = []
        for delta in range(5, -1, -1):
            m_h = mes - delta
            y_h = ano
            while m_h < 1:
                m_h += 12
                y_h -= 1
            try:
                txs_h = tx_repo.list_by_month(y_h, m_h)
                sal_h = calcular_saldo_mensal(txs_h, y_h, m_h)
                bud_h = bud_repo.list_by_month(y_h, m_h)
                sc_h  = calcular_score_financeiro(
                    transacoes=txs_h, budgets=bud_h, installments=installments,
                    taxa_poupanca_atual=sal_h.taxa_poupanca,
                    meta_poupanca=float(meta_score), caixa_pct=caixa_pct,
                )
                hist_score.append({"Mês": f"{calendar.month_abbr[m_h]}/{y_h}", "Score": sc_h.total})
            except Exception:
                pass

        if hist_score:
            df_sc = pd.DataFrame(hist_score)
            fig_sc = px.line(df_sc, x="Mês", y="Score", markers=True, range_y=[0, 100])
            fig_sc.add_hline(y=80, line_dash="dash", line_color="#7BC68A", annotation_text="Excelente",
                              annotation_font_color="#7BC68A")
            fig_sc.add_hline(y=60, line_dash="dash", line_color="#D9B26F", annotation_text="Bom",
                              annotation_font_color="#D9B26F")
            fig_sc.update_traces(line_color="#D9B26F", marker_color="#D9B26F")
            fig_sc.update_layout(
                height=260, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                           tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                font={"color": "#C9BC9E"},
            )
            st.plotly_chart(fig_sc, width='stretch')

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — Alertas de Padrão
    # ══════════════════════════════════════════════════════════════════════════
    with tab_alertas:
        if not transacoes_3m:
            st.markdown(
                '<div style="padding:48px 0;text-align:center;color:var(--ink-4)">sem histórico dos últimos 3 meses</div>',
                unsafe_allow_html=True,
            )
        else:
            alertas = detectar_alertas_padrao(transacoes, transacoes_3m)

            if not alertas:
                st.markdown(
                    '<div class="k-card" style="padding:24px 20px;text-align:center">'
                    '<div style="color:var(--moss);font-size:22px;margin-bottom:8px">✓</div>'
                    '<div style="color:var(--ink-2)">Nenhum gasto acima da média dos últimos 3 meses</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            else:
                alert_rows = []
                for a in alertas:
                    alert_rows.append(f"""<div style="padding:14px 0;border-top:1px solid var(--rule)">
  <div style="display:flex;justify-content:space-between;align-items:baseline;font-family:var(--font-sans)">
    <div>
      <div style="font-size:14px;color:var(--ink);font-weight:500">{a.category}</div>
      <div style="font-size:11px;color:var(--ink-3);margin-top:3px">acima da média em {a.ratio:.1f}×</div>
    </div>
    <div style="text-align:right">
      <div class="mono" style="font-size:18px;color:var(--rust);font-variant-numeric:tabular-nums">{fmt_brl(a.gasto_atual, compact=True)}</div>
      <div class="mono muted" style="font-size:10px">média 3m: {fmt_brl(a.media_3m, compact=True)}</div>
    </div>
  </div>
  {bar_track(a.gasto_atual, a.gasto_atual, "neg")}
</div>""")
                st.markdown(
                    k_card_with_header("Alertas de gasto", "".join(alert_rows),
                                       f"{len(alertas)} categoria{'s' if len(alertas) > 1 else ''} acima da média"),
                    unsafe_allow_html=True,
                )

            # Comparison chart
            st.markdown(section_header("Comparativo por categoria", "mês atual vs média 3 meses"), unsafe_allow_html=True)
            gastos_atual = _gastos_por_categoria(transacoes)
            gastos_3m_d  = _gastos_por_categoria(transacoes_3m)
            todas_cats   = sorted(set(list(gastos_atual.keys()) + list(gastos_3m_d.keys())))

            if todas_cats:
                df_comp = pd.DataFrame({
                    "Categoria":     todas_cats,
                    "Mês atual":     [gastos_atual.get(c, 0.0) for c in todas_cats],
                    "Média 3 meses": [gastos_3m_d.get(c, 0.0) / 3.0 for c in todas_cats],
                })
                fig_comp = px.bar(
                    df_comp, x="Categoria", y=["Mês atual", "Média 3 meses"],
                    barmode="group",
                    color_discrete_sequence=["#D87C6A", "#5C5746"],
                )
                fig_comp.update_layout(
                    height=300, margin=dict(l=0, r=0, t=10, b=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                               tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                    legend=dict(font=dict(family="General Sans, sans-serif", color="#8F8770", size=11)),
                    font={"color": "#C9BC9E"},
                )
                st.plotly_chart(fig_comp, width='stretch')
