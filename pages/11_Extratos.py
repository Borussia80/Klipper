"""Extratos · Klipper — importação de extratos bancários e faturas em PDF."""

from __future__ import annotations

import html as _html
from datetime import date

import pandas as pd
import streamlit as st

from core.statement_reader import ParsedTransaction, StatementResult, read_statement
from core.auth import require_auth
from core.styles import (
    fmt_brl, inject_css, load_page_icon, section_header,
    sidebar_brand, sidebar_user, sidebar_ai_qa, sidebar_nav, stat_card,
)
from models.transaction import Category, PaymentMethod, Transaction, TransactionType

st.set_page_config(page_title="Extratos · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()

with st.sidebar:
    st.markdown(sidebar_brand(), unsafe_allow_html=True)
    sidebar_nav()
    sidebar_user()
    sidebar_ai_qa()



require_auth()
# ── Topbar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:baseline;gap:14px;margin-bottom:4px">
  <span style="font-family:var(--font-sans);font-size:26px;font-weight:600;
    color:var(--ink);letter-spacing:-0.02em">Extratos</span>
  <span style="font-family:var(--font-sans);font-size:11px;letter-spacing:0.16em;
    text-transform:uppercase;color:var(--ink-3);font-weight:500">PDF · banco e cartão</span>
</div>
<div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);
  margin-bottom:24px">
  Faça upload do extrato em PDF — o sistema detecta texto ou OCR automaticamente
</div>
""", unsafe_allow_html=True)

# ── Cache do engine OCR (evita re-inicialização por rerun) ─────────────────────
@st.cache_resource(show_spinner="Carregando engine OCR…")
def _ocr_engine():
    from paddleocr import PaddleOCR
    return PaddleOCR(use_angle_cls=False, lang="pt", show_log=False)


# ── Upload ─────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Selecione o PDF do extrato ou fatura",
    type=["pdf"],
    accept_multiple_files=False,
    label_visibility="collapsed",
)

if not uploaded:
    st.markdown("""
<div class="k-card" style="margin-top:24px;text-align:center;padding:40px 20px">
  <div style="font-size:32px;margin-bottom:12px">📄</div>
  <div style="font-family:var(--font-sans);font-size:14px;color:var(--ink-2)">
    Arraste o PDF ou clique em Browse files acima
  </div>
  <div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);margin-top:8px">
    Funciona com extratos de Nubank, Bradesco, Itaú, BB, Santander e outros.<br>
    PDFs com texto nativo são lidos diretamente. Faturas digitalizadas usam OCR.
  </div>
</div>
""", unsafe_allow_html=True)
    st.stop()

# ── Processar PDF ──────────────────────────────────────────────────────────────
with st.spinner("Lendo PDF…"):
    try:
        result: StatementResult = read_statement(uploaded.getvalue())
    except Exception as e:
        st.error(f"Erro ao processar PDF: {e}")
        st.stop()

# Aviso sobre warnings de OCR
for w in result.warnings:
    st.warning(w)

txs = result.transactions

# ── KPI strip ─────────────────────────────────────────────────────────────────
total_gastos  = sum(t.amount for t in txs if t.tx_type == TransactionType.GASTO)
total_ganhos  = sum(t.amount for t in txs if t.tx_type == TransactionType.GANHO)
n_high_conf   = sum(1 for t in txs if t.confidence >= 0.85)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(stat_card("Transações", str(len(txs)),
                           sub=f"{result.page_count} pág · {result.pdf_type.upper()}"),
                unsafe_allow_html=True)
with c2:
    st.markdown(stat_card("Gastos detectados", fmt_brl(total_gastos),
                           sub=f"{sum(1 for t in txs if t.tx_type == TransactionType.GASTO)} lançamentos",
                           tone="neg"), unsafe_allow_html=True)
with c3:
    st.markdown(stat_card("Receitas detectadas", fmt_brl(total_ganhos),
                           sub=f"{sum(1 for t in txs if t.tx_type == TransactionType.GANHO)} lançamentos",
                           tone="pos"), unsafe_allow_html=True)
with c4:
    conf_pct = int(n_high_conf / len(txs) * 100) if txs else 0
    st.markdown(stat_card("Alta confiança", f"{conf_pct}%",
                           sub=f"{n_high_conf} de {len(txs)}",
                           tone="pos" if conf_pct >= 80 else "warn"),
                unsafe_allow_html=True)

if not txs:
    st.warning("Nenhuma transação detectada. Verifique se o PDF é um extrato bancário válido.")
    with st.expander("Ver texto extraído"):
        st.text(result.raw_text[:3000])
    st.stop()

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown(section_header("Revisar e editar", "Ajuste categorias e tipos antes de importar"),
            unsafe_allow_html=True)

# ── Tabela editável ────────────────────────────────────────────────────────────
cat_options   = [c.value for c in Category]
type_options  = [t.value for t in TransactionType]

df = pd.DataFrame([{
    "Data":        t.date.isoformat(),
    "Descrição":   t.description,
    "Valor (R$)":  t.amount,
    "Tipo":        t.tx_type.value,
    "Categoria":   t.category.value,
    "Confiança":   f"{t.confidence:.0%}",
    "_raw":        t.raw_line,
} for t in txs])

edited = st.data_editor(
    df.drop(columns=["_raw"]),
    width='stretch',
    num_rows="dynamic",
    column_config={
        "Data":       st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "Valor (R$)": st.column_config.NumberColumn("Valor (R$)", format="%.2f", min_value=0.01),
        "Tipo":       st.column_config.SelectboxColumn("Tipo", options=type_options),
        "Categoria":  st.column_config.SelectboxColumn("Categoria", options=cat_options),
        "Confiança":  st.column_config.TextColumn("Confiança", disabled=True),
    },
    hide_index=True,
)

# ── Importar ───────────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
col_btn, col_info = st.columns([1, 3])

with col_btn:
    importar = st.button("⬆️ Importar para Klipper", type="primary", width='stretch')

with col_info:
    st.markdown(
        '<div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);'
        'padding-top:8px">Importa todas as linhas da tabela acima. '
        'Erros de linha individual são pulados e reportados.</div>',
        unsafe_allow_html=True,
    )

if importar:
    _import_transactions(edited)


def _import_transactions(df: pd.DataFrame) -> None:
    try:
        from core.repositories import TransactionRepository
        repo = TransactionRepository()
    except Exception as e:
        st.error(f"Banco de dados indisponível: {e}")
        return

    ok_count = 0
    errors: list[str] = []

    for _, row in df.iterrows():
        try:
            tx_date = date.fromisoformat(str(row["Data"])) if isinstance(row["Data"], str) \
                      else row["Data"]
            tx = Transaction(
                date=tx_date,
                amount=float(row["Valor (R$)"]),
                type=TransactionType(row["Tipo"]),
                category=Category(row["Categoria"]),
                notes=str(row["Descrição"])[:200],
                payment_method=PaymentMethod.PIX,
            )
            repo.create(tx)
            ok_count += 1
        except Exception as e:
            errors.append(f"Linha '{row.get('Descrição', '?')}': {e}")

    if ok_count:
        st.success(f"✅ {ok_count} transações importadas com sucesso.")
    for err in errors:
        st.warning(err)
