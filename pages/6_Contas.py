"""Contas — Contas bancárias, cartões de crédito e parcelamentos."""

from __future__ import annotations

import calendar
from datetime import date

import streamlit as st

from core.repositories import (
    BankAccountRepository, CreditCardRepository,
    InstallmentRepository, TransactionRepository,
)
from core.installment_engine import calcular_comprometimento_mensal
from core.styles import inject_css, metric_card, fmt_brl
from models.bank_account import BankAccount, AccountType
from models.credit_card import CreditCard

st.set_page_config(page_title="Contas · Klipper", page_icon="🏦", layout="wide")
inject_css()
st.title("🏦 Contas")

acc_repo  = BankAccountRepository()
card_repo = CreditCardRepository()
inst_repo = InstallmentRepository()
tx_repo   = TransactionRepository()

hoje = date.today()

tab_contas, tab_cartoes, tab_parc = st.tabs(["Contas Bancárias", "Cartões de Crédito", "Parcelamentos"])

# ──────────────────────────────────────────────────────────────────────────────
# TAB 1 — Contas Bancárias
# ──────────────────────────────────────────────────────────────────────────────
with tab_contas:
    try:
        contas = acc_repo.list_active()
    except Exception as e:
        st.error(f"Erro ao carregar contas: {e}")
        contas = []

    if contas:
        saldo_total = sum(c.balance for c in contas)
        metric_card("Saldo Total", fmt_brl(saldo_total), cor="success")
        st.markdown("")
        cols = st.columns(min(len(contas), 3))
        for i, conta in enumerate(contas):
            with cols[i % 3]:
                tipo_label = {"CORRENTE": "Corrente", "POUPANCA": "Poupança",
                              "INVESTIMENTO": "Investimento"}.get(conta.type.value, conta.type.value)
                st.markdown(
                    f"""<div class="klipper-card" style="border-left:4px solid {conta.color}">
                    <div style="font-weight:700;font-size:15px">{conta.name}</div>
                    <div style="color:var(--text-secondary);font-size:12px">{conta.bank} · {tipo_label}</div>
                    <div style="font-size:22px;font-weight:700;margin-top:8px;color:{'#10B981' if conta.balance >= 0 else '#EF4444'}">{fmt_brl(conta.balance)}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    else:
        st.info("Nenhuma conta cadastrada.")

    st.markdown("")
    with st.expander("➕ Nova conta bancária"):
        with st.form("form_conta"):
            c1, c2 = st.columns(2)
            with c1:
                nome_conta = st.text_input("Nome da conta*")
                banco      = st.text_input("Banco")
            with c2:
                tipo_conta = st.selectbox("Tipo", [t.value for t in AccountType])
                saldo_ini  = st.number_input("Saldo inicial (R$)", step=0.01, format="%.2f")
            cor_conta = st.color_picker("Cor", "#6366F1")
            if st.form_submit_button("Criar conta", type="primary"):
                if not nome_conta.strip():
                    st.error("Nome é obrigatório.")
                else:
                    try:
                        acc_repo.create(BankAccount(
                            name=nome_conta, bank=banco,
                            type=AccountType(tipo_conta),
                            balance=saldo_ini, color=cor_conta,
                        ))
                        st.success("Conta criada.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    if contas:
        with st.expander("✏ Atualizar saldo"):
            conta_opts = {c.name: c.id for c in contas}
            sel = st.selectbox("Conta", list(conta_opts.keys()), key="upd_acc")
            novo_saldo = st.number_input("Novo saldo (R$)", step=0.01, format="%.2f", key="upd_bal")
            if st.button("Atualizar", key="btn_upd_acc"):
                try:
                    acc_repo.update_balance(conta_opts[sel], novo_saldo)
                    st.success("Saldo atualizado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 2 — Cartões de Crédito
# ──────────────────────────────────────────────────────────────────────────────
with tab_cartoes:
    c_ano, c_mes, _ = st.columns([1, 1, 4])
    with c_ano:
        ano_fat = int(st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1), key="ano_fat"))
    with c_mes:
        mes_fat = int(st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                                   format_func=lambda m: calendar.month_abbr[m], key="mes_fat"))
    try:
        cartoes = card_repo.list_active()
        txs_mes = tx_repo.list_by_month(ano_fat, mes_fat)
    except Exception as e:
        st.error(f"Erro: {e}")
        cartoes, txs_mes = [], []

    if cartoes:
        for cartao in cartoes:
            fatura = cartao.fatura_atual([t for t in txs_mes if t.card_id == cartao.id])
            usado_pct = (fatura / cartao.limit_total * 100) if cartao.limit_total > 0 else 0

            st.markdown(
                f"""<div class="klipper-card" style="border-left:4px solid {cartao.color}">
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <div>
                    <div style="font-weight:700;font-size:15px">{cartao.name}</div>
                    <div style="color:var(--text-secondary);font-size:12px">{cartao.bank} · Fecha dia {cartao.closing_day} · Vence dia {cartao.due_day}</div>
                  </div>
                  <div style="text-align:right">
                    <div style="font-size:20px;font-weight:700;color:#EF4444">{fmt_brl(fatura)}</div>
                    <div style="font-size:12px;color:var(--text-secondary)">Limite: {fmt_brl(cartao.limit_total)} · Disponível: {fmt_brl(max(cartao.limit_total - fatura, 0))}</div>
                  </div>
                </div>
                <div style="margin-top:10px;background:#E2E8F0;border-radius:4px;height:8px;overflow:hidden">
                  <div style="width:{min(usado_pct,100):.1f}%;height:8px;border-radius:4px;background:{'#EF4444' if usado_pct >= 80 else '#F59E0B' if usado_pct >= 50 else '#10B981'}"></div>
                </div>
                <div style="font-size:11px;color:var(--text-secondary);margin-top:4px">{usado_pct:.1f}% do limite usado</div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("Nenhum cartão cadastrado.")

    st.markdown("")
    with st.expander("➕ Novo cartão de crédito"):
        with st.form("form_cartao"):
            c1, c2 = st.columns(2)
            with c1:
                nome_cart  = st.text_input("Nome do cartão*")
                banco_cart = st.text_input("Banco emissor")
                limite     = st.number_input("Limite total (R$)", min_value=0.0, step=100.0, format="%.2f")
            with c2:
                fecha_dia = st.number_input("Dia de fechamento", min_value=1, max_value=31, value=1)
                vence_dia = st.number_input("Dia de vencimento", min_value=1, max_value=31, value=10)
                cor_cart  = st.color_picker("Cor", "#EF4444")
            if st.form_submit_button("Criar cartão", type="primary"):
                if not nome_cart.strip():
                    st.error("Nome é obrigatório.")
                else:
                    try:
                        card_repo.create(CreditCard(
                            name=nome_cart, bank=banco_cart,
                            limit_total=limite,
                            closing_day=int(fecha_dia), due_day=int(vence_dia),
                            color=cor_cart,
                        ))
                        st.success("Cartão criado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

# ──────────────────────────────────────────────────────────────────────────────
# TAB 3 — Parcelamentos
# ──────────────────────────────────────────────────────────────────────────────
with tab_parc:
    try:
        installments = inst_repo.list_active()
    except Exception as e:
        st.error(f"Erro ao carregar parcelamentos: {e}")
        installments = []

    if installments:
        comp = calcular_comprometimento_mensal(installments)
        total_restante = sum(i.total_remaining for i in installments)
        metric_card("Total a pagar (todos parcelamentos)", fmt_brl(total_restante), cor="danger")
        st.markdown("")

        # Gráfico de comprometimento mensal
        if comp:
            import plotly.express as px
            import pandas as pd
            meses = sorted(comp.keys())[:12]
            fig = px.bar(
                x=meses, y=[comp[m] for m in meses],
                labels={"x": "Mês", "y": "R$"},
                color_discrete_sequence=["#6366F1"],
                title="Comprometimento mensal futuro",
            )
            fig.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

        for inst in installments:
            pct = (inst.n_paid / inst.n_total * 100) if inst.n_total > 0 else 0
            prox = inst.next_due_date.strftime("%d/%m/%Y") if inst.next_due_date else "—"
            st.markdown(
                f"""<div class="klipper-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:700">{inst.description}</div>
                    <div style="color:var(--text-secondary);font-size:12px">{inst.category} · Próxima: {prox}</div>
                  </div>
                  <div style="text-align:right">
                    <div style="font-weight:700">{fmt_brl(inst.installment_amount)}/mês</div>
                    <div style="font-size:12px;color:var(--text-secondary)">{inst.n_paid}/{inst.n_total} pagas · Restam {fmt_brl(inst.total_remaining)}</div>
                  </div>
                </div>
                <div style="margin-top:8px;background:#E2E8F0;border-radius:4px;height:6px;overflow:hidden">
                  <div style="width:{pct:.1f}%;height:6px;border-radius:4px;background:#10B981"></div>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("")
        with st.expander("✅ Marcar parcela como paga"):
            opts = {f"{i.description} ({i.n_paid}/{i.n_total})": i.id for i in installments}
            sel  = st.selectbox("Parcelamento", list(opts.keys()), key="mark_paid_sel")
            if st.button("Marcar paga", key="btn_mark_paid"):
                try:
                    inst_repo.mark_paid(opts[sel])
                    st.success("Parcela marcada como paga.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
    else:
        st.info("Nenhum parcelamento ativo.")
