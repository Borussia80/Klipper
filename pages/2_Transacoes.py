"""Movimento — Ledger de transações."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date

import html
import pandas as pd
import streamlit as st

from core.installment_engine import gerar_parcelas
from core.repositories import (
    BankAccountRepository, CreditCardRepository,
    InstallmentRepository, TransactionRepository,
)
from core.auth import require_auth
from core.styles import (
    bar_track, fmt_brl, inject_css, k_card_with_header,
    section_header, render_navigation, sidebar_engines, sidebar_user, sidebar_ai_qa,
    stat_card, tx_row_simplifi, load_page_icon,
)
from models.installment import Installment
from models.transaction import (
    Category, PaymentMethod, Transaction,
    TransactionStatus, TransactionType,
)

st.set_page_config(page_title="Movimento · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

tx_repo   = TransactionRepository()
acc_repo  = BankAccountRepository()
card_repo = CreditCardRepository()
inst_repo = InstallmentRepository()

try:
    contas  = acc_repo.list_active()
    cartoes = card_repo.list_active()
except Exception:
    contas, cartoes = [], []

conta_map  = {c.name: c.id for c in contas}
cartao_map = {c.name: c.id for c in cartoes}

_CAT_ICON = {
    "Moradia": "⌂", "Alimentação": "⊕", "Transporte": "⊡",
    "Saúde": "◎", "Educação": "◇", "Lazer": "◈",
    "Investimento": "▣", "Renda": "↑", "Freelance": "∞", "Outros": "○",
}
_PM_LABEL = {
    "PIX": "PIX", "CARTAO_CREDITO": "crédito", "CARTAO_DEBITO": "débito",
    "DINHEIRO": "dinheiro", "TED": "TED", "BOLETO": "boleto",
    "TRANSFERENCIA": "transfer.",
}

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
    # ── Header + Filters ──────────────────────────────────────────────────────────
    st.markdown(section_header("Movimento", "ledger financeiro"), unsafe_allow_html=True)

    hoje = date.today()
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        ano = int(st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1),
                               label_visibility="collapsed"))
    with f2:
        mes = int(st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                               format_func=lambda m: calendar.month_abbr[m],
                               label_visibility="collapsed"))
    with f3:
        filtro_status = st.selectbox(
            "Status", ["Todos"] + [s.value for s in TransactionStatus],
            label_visibility="collapsed",
        )

    try:
        txs_all = tx_repo.list_by_month(ano, mes)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.stop()

    if filtro_status != "Todos":
        txs_all = [t for t in txs_all if t.status.value == filtro_status]

    # ── Quick form — lançar transação ─────────────────────────────────────────────
    with st.expander("+ Lançar transação", expanded=False):
        with st.form("form_tx", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            with fc1:
                tipo      = st.selectbox("Tipo", [t.value for t in TransactionType])
                valor     = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")
                categoria = st.selectbox("Categoria", [c.value for c in Category])
                pagamento = st.selectbox("Pagamento", [p.value for p in PaymentMethod])
            with fc2:
                data_tx   = st.date_input("Data")
                status_tx = st.selectbox("Status", [s.value for s in TransactionStatus])
                conta_sel = st.selectbox("Conta", ["—"] + list(conta_map.keys()))
                eh_cartao = pagamento in ("CARTAO_CREDITO", "CARTAO_DEBITO")
                cartao_sel = "—"
                if eh_cartao and cartoes:
                    cartao_sel = st.selectbox("Cartão", ["—"] + list(cartao_map.keys()))
            notas        = st.text_input("Notas")
            eh_parcelado = st.toggle("É parcelado?")
            n_parcelas   = 1
            if eh_parcelado:
                n_parcelas = st.number_input("Nº parcelas", min_value=2, max_value=120, value=12, step=1)

            if st.form_submit_button("Salvar", type="primary", use_container_width=True):
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
                        for p in gerar_parcelas(inst):
                            tx_repo.create(p)
                        st.success(f"{int(n_parcelas)}× de {fmt_brl(inst.installment_amount)}")
                    else:
                        tx_repo.create(Transaction(
                            date=data_tx, amount=float(valor),
                            type=TransactionType(tipo), category=Category(categoria),
                            notes=notas, payment_method=PaymentMethod(pagamento),
                            account_id=account_id, card_id=card_id,
                            status=TransactionStatus(status_tx),
                        ))
                        st.success(f"Salvo · {fmt_brl(float(valor))}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # ── KPI strip ────────────────────────────────────────────────────────────────
    ganhos   = sum(t.amount for t in txs_all if t.type == TransactionType.GANHO)
    gastos   = sum(
        t.amount for t in txs_all
        if t.type == TransactionType.GASTO and t.category != Category.INVESTIMENTO
    )
    invest   = sum(t.amount for t in txs_all if t.category == Category.INVESTIMENTO)
    saldo    = ganhos - gastos - invest
    n_saidas = len([
        t for t in txs_all
        if t.type == TransactionType.GASTO and t.category != Category.INVESTIMENTO
    ])
    poupanca = (saldo / ganhos * 100) if ganhos > 0 else 0.0

    st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:20px">
  {stat_card("Entradas · mês", fmt_brl(ganhos, compact=True),
             f"{len([t for t in txs_all if t.type==TransactionType.GANHO])} fontes", "pos")}
  {stat_card("Saídas · mês", fmt_brl(gastos, compact=True),
             f"{n_saidas} lançamentos")}
  {stat_card("Saldo líquido", fmt_brl(saldo, compact=True),
             f"poupança · {poupanca:.0f}%", "pos" if saldo >= 0 else "neg")}
  {stat_card("Investido", fmt_brl(invest, compact=True), "aporte mensal", "brass")}
</div>
""", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────────
    tab_tudo, tab_in, tab_out, tab_inv, tab_auto = st.tabs(
        ["Tudo", "Entradas", "Saídas", "Investimento", "Recorrentes"]
    )

    def _build_feed_html(txs: list) -> str:
        by_day: dict[str, list] = defaultdict(list)
        for t in sorted(txs, key=lambda x: x.date, reverse=True):
            by_day[t.date.strftime("%d %b")].append(t)

        rows_html = []
        for day, day_txs in by_day.items():
            day_total = sum(
                (t.amount if t.type == TransactionType.GANHO else -t.amount)
                for t in day_txs
            )
            sign      = "+" if day_total >= 0 else ""
            day_color = "var(--moss)" if day_total >= 0 else "var(--rust)"
            total_span = (
                f'<span class="mono" style="font-size:10px;color:{day_color}">'
                f'{sign}{fmt_brl(abs(day_total), compact=True)}</span>'
            )
            feed_rows = []
            for t in day_txs:
                is_income = t.type == TransactionType.GANHO
                is_invest = t.category == Category.INVESTIMENTO
                val_cls   = "pos" if is_income else ("invest" if is_invest else "")
                cat       = "Renda" if is_income else t.category.value
                title     = html.escape(t.notes) if t.notes else t.category.value
                pm_label  = _PM_LABEL.get(t.payment_method.value, t.payment_method.value)
                pending   = ' · <span class="warn">pendente</span>' if t.status != TransactionStatus.PAGO else ""
                meta      = f'{t.category.value} · {pm_label}{pending}'
                prefix    = "+" if is_income else "−"
                value     = f'{prefix}{fmt_brl(t.amount, compact=True)}'
                feed_rows.append(tx_row_simplifi(cat, title, meta, value, val_cls))

            rows_html.append(f"""<div class="k-feed-day">
  <div class="k-feed-day-h">{day}<span class="sub">{total_span} · {len(day_txs)} lanc.</span></div>
  <div class="k-feed-list">{"".join(feed_rows)}</div>
</div>""")

        return f'<div class="k-feed">{"".join(rows_html)}</div>'

    def _render_tab(txs: list) -> None:
        if not txs:
            st.markdown(
                '<div style="padding:48px 0;text-align:center;color:var(--ink-4)">sem lançamentos</div>',
                unsafe_allow_html=True,
            )
            return

        col_feed, col_right = st.columns([1.7, 1], gap="large")

        with col_feed:
            ledger_html = _build_feed_html(txs)
            st.markdown(
                k_card_with_header("Ledger", ledger_html, f"{len(txs)} lançamentos"),
                unsafe_allow_html=True,
            )
            with st.expander("Ações"):
                opts = {
                    f"{t.date} · {t.category.value} · {fmt_brl(t.amount)}": t.id
                    for t in txs
                }
                sel = st.selectbox("Selecionar", list(opts.keys()), label_visibility="collapsed")
                if st.button("Deletar selecionada", type="secondary"):
                    try:
                        TransactionRepository().delete(opts[sel])
                        st.success("Deletada.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

        with col_right:
            by_cat: dict[str, float] = defaultdict(float)
            for t in txs:
                if t.type == TransactionType.GASTO:
                    by_cat[t.category.value] += t.amount

            if by_cat:
                sorted_cats = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
                max_v = sorted_cats[0][1]
                cat_rows = []
                for cat, v in sorted_cats[:7]:
                    icon = _CAT_ICON.get(cat, "○")
                    cat_rows.append(f"""<div style="margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;font-family:var(--font-sans);font-size:12px;margin-bottom:5px">
    <span style="color:var(--ink)">{icon} {cat}</span>
    <span class="mono muted" style="font-size:11px">{fmt_brl(v, compact=True)}</span>
  </div>
  {bar_track(v, max_v)}
</div>""")
                st.markdown(
                    k_card_with_header("Por categoria", "".join(cat_rows), "gastos · mês corrente"),
                    unsafe_allow_html=True,
                )

            by_pm: dict[str, float] = defaultdict(float)
            for t in txs:
                by_pm[t.payment_method.value] += t.amount

            if by_pm:
                sorted_pm = sorted(by_pm.items(), key=lambda x: x[1], reverse=True)
                max_pm = sorted_pm[0][1]
                pm_rows = []
                for pm, v in sorted_pm[:5]:
                    label = _PM_LABEL.get(pm, pm)
                    pm_rows.append(f"""<div style="margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;font-family:var(--font-sans);font-size:12px;margin-bottom:5px">
    <span style="color:var(--ink-2)">{label}</span>
    <span class="mono muted" style="font-size:11px">{fmt_brl(v, compact=True)}</span>
  </div>
  {bar_track(v, max_pm, "brass")}
</div>""")
                st.markdown(
                    k_card_with_header("Por meio de pagamento", "".join(pm_rows), "volume · mês"),
                    unsafe_allow_html=True,
                )

            rows_csv = [
                {
                    "Data": t.date, "Tipo": t.type.value, "Categoria": t.category.value,
                    "Valor": t.amount, "Pagamento": t.payment_method.value,
                    "Status": t.status.value, "Notas": t.notes,
                }
                for t in txs
            ]
            csv = pd.DataFrame(rows_csv).to_csv(index=False).encode("utf-8")
            st.download_button(
                "Exportar CSV", csv, "transacoes.csv", "text/csv",
                use_container_width=True,
            )

    with tab_tudo:
        _render_tab(txs_all)

    with tab_in:
        _render_tab([t for t in txs_all if t.type == TransactionType.GANHO])

    with tab_out:
        _render_tab([
            t for t in txs_all
            if t.type == TransactionType.GASTO and t.category != Category.INVESTIMENTO
        ])

    with tab_inv:
        _render_tab([t for t in txs_all if t.category == Category.INVESTIMENTO])

    with tab_auto:
        _render_tab([t for t in txs_all if t.installment_id is not None])
