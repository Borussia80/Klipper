"""Transações — Lançar e visualizar gastos e ganhos."""

from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
import streamlit as st

from core.formatters import formatar_moeda_brl
from core.repositories import TransactionRepository
from models.transaction import Category, Transaction, TransactionType

st.set_page_config(page_title="Transações · Klipper", page_icon="💸", layout="wide")
st.title("💸 Transações")

repo = TransactionRepository()

# --- Formulário de lançamento ---
with st.expander("➕ Nova transação", expanded=True):
    with st.form("form_transacao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", [t.value for t in TransactionType])
            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
        with col2:
            data = st.date_input("Data", value=date.today(), max_value=date.today())
            categoria = st.selectbox("Categoria", [c.value for c in Category])
        notas = st.text_input("Notas (opcional)")

        submitted = st.form_submit_button("Salvar", type="primary", use_container_width=True)
        if submitted:
            try:
                tx = Transaction(
                    date=data,
                    amount=float(valor),
                    type=TransactionType(tipo),
                    category=Category(categoria),
                    notes=notas,
                )
                repo.create(tx)
                st.success(f"Transação salva: {tipo} de {formatar_moeda_brl(float(valor))}")
            except ValueError as e:
                st.error(f"Dados inválidos: {e}")
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- Filtros ---
st.divider()
hoje = date.today()
col_ano, col_mes, col_tipo, col_cat = st.columns(4)
with col_ano:
    ano = st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1))
with col_mes:
    mes = st.selectbox("Mês", range(1, 13), index=hoje.month - 1, format_func=lambda m: calendar.month_abbr[m])
with col_tipo:
    filtro_tipo = st.selectbox("Tipo", ["Todos"] + [t.value for t in TransactionType])
with col_cat:
    filtro_cat = st.selectbox("Categoria", ["Todas"] + [c.value for c in Category])

# --- Carregar e exibir ---
try:
    txs = repo.list_by_month(int(ano), int(mes))
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

if filtro_tipo != "Todos":
    txs = [t for t in txs if t.type.value == filtro_tipo]
if filtro_cat != "Todas":
    txs = [t for t in txs if t.category.value == filtro_cat]

if txs:
    df = pd.DataFrame([
        {
            "ID": t.id,
            "Data": t.date.strftime("%d/%m/%Y"),
            "Tipo": t.type.value,
            "Categoria": t.category.value,
            "Valor": formatar_moeda_brl(t.amount),
            "Notas": t.notes,
        }
        for t in txs
    ])
    st.dataframe(df.drop(columns=["ID"]), use_container_width=True, hide_index=True)

    # Export CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Exportar CSV", csv, "transacoes.csv", "text/csv")

    # Totais
    from models.transaction import TransactionType as TT
    ganhos = sum(t.amount for t in txs if t.type == TT.GANHO)
    gastos = sum(t.amount for t in txs if t.type == TT.GASTO)
    st.caption(
        f"**{len(txs)} registros** | Ganhos: {formatar_moeda_brl(ganhos)} | "
        f"Gastos: {formatar_moeda_brl(gastos)} | Saldo: {formatar_moeda_brl(ganhos - gastos)}"
    )

    # Deletar
    st.divider()
    with st.expander("🗑 Deletar transação"):
        id_del = st.selectbox("ID da transação", [t.id for t in txs])
        if st.button("Deletar", type="secondary"):
            try:
                repo.delete(id_del)
                st.success("Transação deletada.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
else:
    st.info("Nenhuma transação encontrada para os filtros selecionados.")
