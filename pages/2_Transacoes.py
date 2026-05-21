"""Transações — Lançar e visualizar gastos e ganhos."""

from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
import streamlit as st

from core.formatters import formatar_moeda_brl
from core.installment_engine import gerar_parcelas
from core.repositories import (
    TransactionRepository, BankAccountRepository,
    CreditCardRepository, InstallmentRepository,
)
from core.styles import inject_css, fmt_brl, payment_badge
from models.installment import Installment
from models.transaction import (
    Category, Transaction, TransactionType,
    PaymentMethod, TransactionStatus,
)

st.set_page_config(page_title="Transações · Klipper", page_icon="💸", layout="wide")
inject_css()
st.title("💸 Transações")

tx_repo   = TransactionRepository()
acc_repo  = BankAccountRepository()
card_repo = CreditCardRepository()
inst_repo = InstallmentRepository()

try:
    contas  = acc_repo.list_active()
    cartoes = card_repo.list_active()
except Exception as e:
    st.error(f"Erro ao carregar contas/cartões: {e}")
    contas, cartoes = [], []

conta_map  = {c.name: c.id for c in contas}
cartao_map = {c.name: c.id for c in cartoes}

# ── Formulário de lançamento ──────────────────────────────────────────────────
with st.expander("➕ Nova transação", expanded=True):
    with st.form("form_transacao", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tipo       = st.selectbox("Tipo", [t.value for t in TransactionType])
            valor      = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
            categoria  = st.selectbox("Categoria", [c.value for c in Category])
            pagamento  = st.selectbox("Meio de pagamento", [p.value for p in PaymentMethod])
        with c2:
            data_tx   = st.date_input("Data")
            status_tx = st.selectbox("Status", [s.value for s in TransactionStatus])
            conta_sel = st.selectbox("Conta bancária", ["—"] + list(conta_map.keys()))
            eh_cartao = pagamento in ("CARTAO_CREDITO", "CARTAO_DEBITO")
            if eh_cartao and cartoes:
                cartao_sel = st.selectbox("Cartão", ["—"] + list(cartao_map.keys()))
            else:
                cartao_sel = "—"
                if eh_cartao:
                    st.caption("Cadastre um cartão primeiro em Contas.")

        notas = st.text_input("Notas (opcional)")

        eh_parcelado = st.toggle("É parcelado?")
        n_parcelas = 1
        if eh_parcelado:
            n_parcelas = st.number_input("Número de parcelas", min_value=2, max_value=120, value=12, step=1)

        submitted = st.form_submit_button("Salvar", type="primary", use_container_width=True)
        if submitted:
            try:
                account_id = conta_map.get(conta_sel) if conta_sel != "—" else None
                card_id    = cartao_map.get(cartao_sel) if cartao_sel != "—" else None

                if eh_parcelado:
                    inst = Installment(
                        description=notas or categoria,
                        total_amount=float(valor),
                        n_total=int(n_parcelas),
                        start_date=data_tx,
                        card_id=card_id,
                        account_id=account_id,
                        category=categoria,
                    )
                    inst_repo.create(inst)
                    parcelas = gerar_parcelas(inst)
                    for p in parcelas:
                        tx_repo.create(p)
                    st.success(f"Parcelamento criado: {int(n_parcelas)}× de {fmt_brl(inst.installment_amount)}")
                else:
                    tx = Transaction(
                        date=data_tx,
                        amount=float(valor),
                        type=TransactionType(tipo),
                        category=Category(categoria),
                        notes=notas,
                        payment_method=PaymentMethod(pagamento),
                        account_id=account_id,
                        card_id=card_id,
                        status=TransactionStatus(status_tx),
                    )
                    tx_repo.create(tx)
                    st.success(f"Salvo: {tipo} {fmt_brl(float(valor))}")
            except ValueError as e:
                st.error(f"Dados inválidos: {e}")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# ── Filtros ───────────────────────────────────────────────────────────────────
st.divider()
hoje = date.today()
f1, f2, f3, f4, f5 = st.columns(5)
with f1:
    ano = int(st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1)))
with f2:
    mes = int(st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                           format_func=lambda m: calendar.month_abbr[m]))
with f3:
    filtro_tipo = st.selectbox("Tipo", ["Todos"] + [t.value for t in TransactionType])
with f4:
    filtro_cat = st.selectbox("Categoria", ["Todas"] + [c.value for c in Category])
with f5:
    filtro_status = st.selectbox("Status", ["Todos"] + [s.value for s in TransactionStatus])

try:
    txs = tx_repo.list_by_month(ano, mes)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

if filtro_tipo != "Todos":
    txs = [t for t in txs if t.type.value == filtro_tipo]
if filtro_cat != "Todas":
    txs = [t for t in txs if t.category.value == filtro_cat]
if filtro_status != "Todos":
    txs = [t for t in txs if t.status.value == filtro_status]

# ── Tabela ────────────────────────────────────────────────────────────────────
if txs:
    rows = []
    for t in txs:
        rows.append({
            "ID":         t.id,
            "Data":       t.date.strftime("%d/%m/%Y"),
            "Tipo":       t.type.value,
            "Categoria":  t.category.value,
            "Valor":      fmt_brl(t.amount),
            "Pagamento":  t.payment_method.value,
            "Status":     t.status.value,
            "Notas":      (t.notes[:40] if t.notes else ""),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df.drop(columns=["ID"]), use_container_width=True, hide_index=True)

    ganhos = sum(t.amount for t in txs if t.type == TransactionType.GANHO)
    gastos = sum(t.amount for t in txs if t.type == TransactionType.GASTO)
    st.caption(
        f"**{len(txs)} registros** · Ganhos: {fmt_brl(ganhos)} · "
        f"Gastos: {fmt_brl(gastos)} · Saldo: {fmt_brl(ganhos - gastos)}"
    )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Exportar CSV", csv, "transacoes.csv", "text/csv")

    st.divider()
    with st.expander("🗑 Deletar transação"):
        opts = {f"{t.date} | {t.type.value} | {fmt_brl(t.amount)} | {t.notes[:30]}": t.id for t in txs}
        sel = st.selectbox("Selecione", list(opts.keys()))
        if st.button("Deletar", type="secondary"):
            try:
                tx_repo.delete(opts[sel])
                st.success("Transação deletada.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
else:
    st.info("Nenhuma transação encontrada para os filtros selecionados.")
