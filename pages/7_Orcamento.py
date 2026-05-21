"""Orçamento — Orçamentos, meta de poupança, score financeiro e alertas de padrão."""

from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from core.analytics import calcular_saldo_mensal
from core.behavioral import (
    calcular_score_financeiro, calcular_uso_orcamento, detectar_alertas_padrao,
)
from core.repositories import (
    TransactionRepository, InstallmentRepository,
    BudgetRepository, InvestmentRepository,
)
from core.styles import inject_css, budget_bar, score_circle, fmt_brl, metric_card
from models.budget import Budget
from models.transaction import Category

st.set_page_config(page_title="Orçamento · Klipper", page_icon="🎯", layout="wide")
inject_css()
st.title("🎯 Orçamento & Score")

tx_repo   = TransactionRepository()
inst_repo = InstallmentRepository()
bud_repo  = BudgetRepository()
inv_repo  = InvestmentRepository()

hoje = date.today()
c_ano, c_mes, _ = st.columns([1, 1, 4])
with c_ano:
    ano = int(st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1)))
with c_mes:
    mes = int(st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                           format_func=lambda m: calendar.month_abbr[m]))

with st.spinner("Carregando..."):
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

tab_orc, tab_meta, tab_score, tab_alertas = st.tabs(
    ["Orçamentos", "Meta de Poupança", "Score Financeiro", "Alertas de Padrão"]
)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Orçamentos
# ──────────────────────────────────────────────────────────────────────────────
with tab_orc:
    if budgets:
        status_list = calcular_uso_orcamento(transacoes, budgets)
        for s in status_list:
            budget_bar(s.category, s.gasto, s.limite)
            badge_color = {"OK": "#10B981", "ALERTA": "#F59E0B", "ESTOURO": "#EF4444"}[s.status]
            st.markdown(
                f'<span style="font-size:11px;color:{badge_color};font-weight:600">{s.status} · {s.pct:.1f}%</span>',
                unsafe_allow_html=True,
            )
    else:
        st.info("Nenhum orçamento configurado para este mês.")

    st.markdown("")
    with st.expander("➕ Configurar orçamento"):
        with st.form("form_budget"):
            c1, c2 = st.columns(2)
            with c1:
                cat_bud   = st.selectbox("Categoria", [c.value for c in Category])
                limite_bud = st.number_input("Limite mensal (R$)", min_value=0.01, step=10.0, format="%.2f")
            with c2:
                ano_bud = st.number_input("Ano", min_value=2020, max_value=2030, value=ano)
                mes_bud = st.selectbox("Mês", range(1, 13), index=mes - 1,
                                       format_func=lambda m: calendar.month_abbr[m], key="mes_bud")
            if st.form_submit_button("Salvar orçamento", type="primary"):
                try:
                    bud_repo.upsert(Budget(
                        category=cat_bud, monthly_limit=limite_bud,
                        year=int(ano_bud), month=int(mes_bud),
                    ))
                    st.success("Orçamento salvo.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    if budgets:
        with st.expander("🗑 Remover orçamento"):
            opts = {f"{b.category} ({calendar.month_abbr[b.month]}/{b.year})": b.id for b in budgets}
            sel  = st.selectbox("Selecione", list(opts.keys()), key="del_bud")
            if st.button("Remover", key="btn_del_bud"):
                try:
                    bud_repo.delete(opts[sel])
                    st.success("Orçamento removido.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Meta de Poupança
# ──────────────────────────────────────────────────────────────────────────────
with tab_meta:
    c1, c2 = st.columns(2)
    with c1:
        meta_poupanca = st.slider("Meta de poupança (%)", 0, 50, 20, step=5)
    with c2:
        poupanca_real = saldo.taxa_poupanca
        cor = "success" if poupanca_real >= meta_poupanca else "danger"
        metric_card(
            "Taxa de Poupança Real",
            f"{poupanca_real:.1f}%",
            subtitulo=f"Meta: {meta_poupanca}%",
            cor=cor,
        )

    historico = []
    for delta in range(5, -1, -1):
        m_h = mes - delta
        y_h = ano
        while m_h < 1:
            m_h += 12
            y_h -= 1
        try:
            txs_h  = tx_repo.list_by_month(y_h, m_h)
            sal_h  = calcular_saldo_mensal(txs_h, y_h, m_h)
            historico.append({"Mês": f"{calendar.month_abbr[m_h]}/{y_h}", "Poupança (%)": sal_h.taxa_poupanca})
        except Exception:
            pass

    if historico:
        df_hist = pd.DataFrame(historico)
        fig = px.line(df_hist, x="Mês", y="Poupança (%)", markers=True,
                      title="Histórico de poupança (6 meses)")
        fig.add_hline(y=meta_poupanca, line_dash="dash", line_color="#EF4444",
                      annotation_text=f"Meta {meta_poupanca}%")
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Score Financeiro
# ──────────────────────────────────────────────────────────────────────────────
with tab_score:
    meta_score = st.slider("Meta de poupança para score (%)", 0, 50, 20, step=5, key="meta_score")

    score = calcular_score_financeiro(
        transacoes=transacoes,
        budgets=budgets,
        installments=installments,
        taxa_poupanca_atual=saldo.taxa_poupanca,
        meta_poupanca=float(meta_score),
        caixa_pct=caixa_pct,
        transacoes_3_meses=transacoes_3m,
    )

    c_score, c_break = st.columns([1, 2])
    with c_score:
        score_circle(score.total)
        label = "EXCELENTE" if score.total >= 80 else "BOM" if score.total >= 60 else "ATENÇÃO" if score.total >= 40 else "CRÍTICO"
        st.markdown(f"<div style='text-align:center;font-weight:700;margin-top:8px'>{label}</div>", unsafe_allow_html=True)

    with c_break:
        st.markdown("**Breakdown do Score**")
        criterios = [
            ("Orçamento (todas as cat.)",        "orcamento", 30),
            ("Meta de poupança atingida",         "poupanca",  25),
            ("Caixa M2 ≥ 20%",                   "caixa",     20),
            ("Sem gasto acima da média 3 meses",  "media",     15),
            ("Sem parcela atrasada",              "parcelas",  10),
        ]
        for label, key, max_pts in criterios:
            pts = score.detalhes.get(key, 0)
            icon = "✅" if pts > 0 else "❌"
            pct_fill = (pts / max_pts * 100) if max_pts > 0 else 0
            color = "#10B981" if pts > 0 else "#EF4444"
            st.markdown(
                f"""<div style="margin-bottom:10px">
                <div style="display:flex;justify-content:space-between;font-size:13px">
                  <span>{icon} {label}</span>
                  <span style="font-weight:600;color:{color}">{pts}/{max_pts}</span>
                </div>
                <div style="background:#E2E8F0;border-radius:4px;height:6px;overflow:hidden;margin-top:4px">
                  <div style="width:{pct_fill:.0f}%;height:6px;background:{color};border-radius:4px"></div>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Histórico de score
    st.markdown("**Histórico do Score (6 meses)**")
    hist_score = []
    for delta in range(5, -1, -1):
        m_h = mes - delta
        y_h = ano
        while m_h < 1:
            m_h += 12
            y_h -= 1
        try:
            txs_h  = tx_repo.list_by_month(y_h, m_h)
            sal_h  = calcular_saldo_mensal(txs_h, y_h, m_h)
            bud_h  = bud_repo.list_by_month(y_h, m_h)
            sc_h   = calcular_score_financeiro(
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
        fig_sc.add_hline(y=80, line_dash="dash", line_color="#10B981", annotation_text="Excelente")
        fig_sc.add_hline(y=60, line_dash="dash", line_color="#F59E0B", annotation_text="Bom")
        fig_sc.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_sc, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# TAB 4 — Alertas de Padrão
# ──────────────────────────────────────────────────────────────────────────────
with tab_alertas:
    if not transacoes_3m:
        st.info("Sem histórico dos últimos 3 meses para comparação.")
    else:
        alertas = detectar_alertas_padrao(transacoes, transacoes_3m)
        if not alertas:
            st.success("Nenhum gasto acima da média dos últimos 3 meses.")
        else:
            for a in alertas:
                st.markdown(
                    f"""<div class="klipper-card" style="border-left:4px solid #EF4444">
                    <div style="font-weight:700;font-size:14px">{a.category}</div>
                    <div style="display:flex;justify-content:space-between;margin-top:6px">
                      <div>
                        <div style="color:var(--text-secondary);font-size:12px">Gasto atual</div>
                        <div style="font-weight:700;color:#EF4444;font-size:18px">{fmt_brl(a.gasto_atual)}</div>
                      </div>
                      <div>
                        <div style="color:var(--text-secondary);font-size:12px">Média 3 meses</div>
                        <div style="font-weight:700;font-size:18px">{fmt_brl(a.media_3m)}</div>
                      </div>
                      <div>
                        <div style="color:var(--text-secondary);font-size:12px">Ratio</div>
                        <div style="font-weight:700;color:#EF4444;font-size:18px">{a.ratio:.1f}×</div>
                      </div>
                    </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("**Comparativo por categoria**")
        from core.behavioral import _gastos_por_categoria
        gastos_atual = _gastos_por_categoria(transacoes)
        gastos_3m    = _gastos_por_categoria(transacoes_3m)
        todas_cats   = sorted(set(list(gastos_atual.keys()) + list(gastos_3m.keys())))

        if todas_cats:
            df_comp = pd.DataFrame({
                "Categoria":    todas_cats,
                "Mês atual":    [gastos_atual.get(c, 0.0) for c in todas_cats],
                "Média 3 meses": [gastos_3m.get(c, 0.0) / 3.0 for c in todas_cats],
            })
            fig_comp = px.bar(
                df_comp, x="Categoria", y=["Mês atual", "Média 3 meses"],
                barmode="group", color_discrete_sequence=["#EF4444", "#6366F1"],
            )
            fig_comp.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_comp, use_container_width=True)
