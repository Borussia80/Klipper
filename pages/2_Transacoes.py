"""Movimento — Ledger de transações."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal

_MESES_PT = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

import html
import pandas as pd
import streamlit as st

import plotly.graph_objects as go
from core.analytics import preparar_gastos_diarios, preparar_comparativo_categorias
from core.installment_engine import gerar_parcelas
from core.repositories import (
    BankAccountRepository, CreditCardRepository,
    InstallmentRepository, TransactionRepository, tx_balance_delta,
)
from core.auth import require_auth
from core.styles import (
    bar_track, fmt_brl, inject_css, k_card_with_header,
    section_header, render_navigation, sidebar_engines, sidebar_user, sidebar_ai_qa,
    stat_card, tx_row_simplifi, load_page_icon,
    setup_sidebar,
)
from models.installment import Installment
from models.transaction import (
    Category, PaymentMethod, Transaction,
    TransactionStatus, TransactionType, categories_for_type,
)

st.set_page_config(page_title="Movimento · Klipper", page_icon=load_page_icon(), layout="wide", initial_sidebar_state="collapsed")
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

@st.dialog("Editar lançamento")
def _edit_dialog(tx: Transaction) -> None:
    with st.form("form_edit_tx"):
        fc1, fc2 = st.columns(2)
        with fc1:
            tipo = st.selectbox(
                "Tipo", [t.value for t in TransactionType],
                index=[t.value for t in TransactionType].index(tx.type.value),
            )
            valor = st.number_input(
                "Valor (R$)", min_value=0.01, step=0.01, format="%.2f",
                value=float(tx.amount),
            )
            categoria = st.selectbox(
                "Categoria", [c.value for c in Category],
                index=[c.value for c in Category].index(tx.category.value),
            )
            pagamento = st.selectbox(
                "Pagamento", [p.value for p in PaymentMethod],
                index=[p.value for p in PaymentMethod].index(tx.payment_method.value),
            )
        with fc2:
            data_tx = st.date_input("Data", value=tx.date)
            status_tx = st.selectbox(
                "Status", [s.value for s in TransactionStatus],
                index=[s.value for s in TransactionStatus].index(tx.status.value),
            )
            conta_opts = ["—"] + list(conta_map.keys())
            conta_atual = next((k for k, v in conta_map.items() if v == tx.account_id), "—")
            conta_sel = st.selectbox("Conta", conta_opts, index=conta_opts.index(conta_atual))
            cartao_opts = ["—"] + list(cartao_map.keys())
            cartao_atual = next((k for k, v in cartao_map.items() if v == tx.card_id), "—")
            cartao_sel = st.selectbox("Cartão", cartao_opts, index=cartao_opts.index(cartao_atual))
        notas = st.text_input("Notas", value=tx.notes or "")
        col_cancel, col_save = st.columns([1, 2])
        with col_cancel:
            cancelar = st.form_submit_button("Cancelar", use_container_width=True)
        with col_save:
            salvar = st.form_submit_button("Salvar alterações", type="primary", use_container_width=True)
        if cancelar:
            st.rerun()
        if salvar:
            try:
                old_account_id = tx.account_id
                old_delta = tx_balance_delta(float(tx.amount), tx.type)
                updated = Transaction(
                    id=tx.id,
                    date=data_tx,
                    amount=float(valor),
                    type=TransactionType(tipo),
                    category=Category(categoria),
                    notes=notas or None,
                    payment_method=PaymentMethod(pagamento),
                    account_id=conta_map.get(conta_sel) if conta_sel != "—" else None,
                    card_id=cartao_map.get(cartao_sel) if cartao_sel != "—" else None,
                    status=TransactionStatus(status_tx),
                    installment_id=tx.installment_id,
                )
                tx_repo.update(updated)
                # só reverter saldo original se a tx antiga estava PAGA
                if old_account_id and tx.status == TransactionStatus.PAGO:
                    acc_repo.adjust_balance(old_account_id, -old_delta)
                # só aplicar novo saldo se a tx atualizada está PAGA
                if updated.account_id and updated.status == TransactionStatus.PAGO:
                    acc_repo.adjust_balance(updated.account_id, tx_balance_delta(float(updated.amount), updated.type))
                st.success("Salvo.")
                st.rerun()
            except Exception as e:
                st.error(str(e))


# ── Layout ────────────────────────────────────────────────────────────────────

setup_sidebar()

# ── Header + Filters ──────────────────────────────────────────────────────────
st.markdown(section_header("Movimento", "ledger financeiro"), unsafe_allow_html=True)

hoje = date.today()
f1, f2, f3 = st.columns([1, 1, 2])
with f1:
    ano = int(st.selectbox("Ano", range(hoje.year, hoje.year - 4, -1),
                           label_visibility="collapsed"))
with f2:
    mes = int(st.selectbox("Mês", range(1, 13), index=hoje.month - 1,
                           format_func=lambda m: _MESES_PT[m],
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

# ── Quick form — lançar transação (2 etapas) ──────────────────────────────────
with st.expander("+ Lançar transação", expanded=False):
    _step = st.session_state.get("_tx_step", 1)
    if _step == 2 and "_tx_tipo" not in st.session_state:
        _step = 1

    if _step == 1:
        st.markdown(
            '<div style="font-size:11px;color:var(--ink-4);margin-bottom:8px">'
            'Etapa 1 de 2 · tipo · valor · data</div>',
            unsafe_allow_html=True,
        )
        s1c1, s1c2, s1c3 = st.columns([1, 1, 1])
        with s1c1:
            _tipo_1 = st.radio(
                "Tipo", [t.value for t in TransactionType],
                horizontal=True, label_visibility="collapsed",
            )
        with s1c2:
            _valor_1 = st.number_input(
                "Valor (R$)", min_value=0.01, step=0.01, format="%.2f",
                label_visibility="collapsed",
            )
        with s1c3:
            _data_1 = st.date_input("Data", label_visibility="collapsed")
        if st.button("Continuar →", type="primary", use_container_width=True):
            st.session_state["_tx_step"]  = 2
            st.session_state["_tx_tipo"]  = _tipo_1
            st.session_state["_tx_valor"] = float(_valor_1)
            st.session_state["_tx_data"]  = _data_1
            st.rerun()

    else:
        _tipo_s  = st.session_state["_tx_tipo"]
        _valor_s = st.session_state["_tx_valor"]
        _data_s  = st.session_state["_tx_data"]
        st.markdown(
            f'<div class="mono muted" style="font-size:11px;padding:6px 0 10px;'
            f'border-bottom:1px solid var(--rule);margin-bottom:10px">'
            f'{_tipo_s} · {fmt_brl(_valor_s, compact=True)} · {_data_s.strftime("%d/%m/%Y")}'
            f' &nbsp;<span style="color:var(--ink-4)">— etapa 2 de 2</span></div>',
            unsafe_allow_html=True,
        )
        fc1, fc2 = st.columns(2)
        with fc1:
            _cats    = categories_for_type(TransactionType(_tipo_s))
            _cat_opts = [c.value for c in _cats]
            _def_cat  = "Renda" if _tipo_s == "GANHO" else "Alimentação"
            _cat_idx  = _cat_opts.index(_def_cat) if _def_cat in _cat_opts else 0
            categoria = st.selectbox("Categoria", _cat_opts, index=_cat_idx)
            pagamento = st.selectbox("Pagamento", [p.value for p in PaymentMethod])
        with fc2:
            status_tx = st.selectbox("Status", [s.value for s in TransactionStatus])
            conta_sel = st.selectbox("Conta", ["—"] + list(conta_map.keys()))
        eh_cartao = pagamento in ("CARTAO_CREDITO", "CARTAO_DEBITO")
        cartao_sel = "—"
        if eh_cartao:
            if cartoes:
                cartao_sel = st.selectbox("Cartão", ["—"] + list(cartao_map.keys()))
            else:
                st.warning("Nenhum cartão cadastrado. Acesse **Contas** para adicionar um cartão antes de usar esse meio de pagamento.")
        notas        = st.text_input("Notas")
        eh_parcelado = st.toggle("É parcelado?")
        n_parcelas   = 1
        if eh_parcelado:
            n_parcelas = st.number_input("Nº parcelas", min_value=2, max_value=120, value=12, step=1)

        col_back, col_save = st.columns([1, 3])
        with col_back:
            if st.button("← Voltar", use_container_width=True):
                st.session_state["_tx_step"] = 1
                st.rerun()
        with col_save:
            if st.button("Salvar", type="primary", use_container_width=True):
                try:
                    account_id = conta_map.get(conta_sel) if conta_sel != "—" else None
                    card_id    = cartao_map.get(cartao_sel) if cartao_sel != "—" else None
                    if eh_parcelado:
                        inst = Installment(
                            description=notas or categoria,
                            total_amount=_valor_s,
                            n_total=int(n_parcelas),
                            start_date=_data_s,
                            card_id=card_id,
                            account_id=account_id,
                            category=categoria,
                        )
                        inst_repo.create(inst)
                        for p in gerar_parcelas(inst):
                            tx_repo.create(p)
                            # débita conta apenas para parcelas já vencidas (PAGO)
                            if p.account_id and p.status == TransactionStatus.PAGO:
                                acc_repo.adjust_balance(p.account_id, tx_balance_delta(float(p.amount), p.type))
                        st.success(f"{int(n_parcelas)}× de {fmt_brl(inst.installment_amount)}")
                    else:
                        new_tx = Transaction(
                            date=_data_s, amount=_valor_s,
                            type=TransactionType(_tipo_s), category=Category(categoria),
                            notes=notas, payment_method=PaymentMethod(pagamento),
                            account_id=account_id, card_id=card_id,
                            status=TransactionStatus(status_tx),
                        )
                        tx_repo.create(new_tx)
                        # só move saldo quando status = PAGO
                        if account_id and new_tx.status == TransactionStatus.PAGO:
                            acc_repo.adjust_balance(account_id, tx_balance_delta(float(_valor_s), TransactionType(_tipo_s)))
                        st.success(f"Salvo · {fmt_brl(_valor_s)}")
                    for _k in ("_tx_step", "_tx_tipo", "_tx_valor", "_tx_data"):
                        st.session_state.pop(_k, None)
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

# ── Charts de análise ─────────────────────────────────────────────────────────
_tab_diario, _tab_comp = st.tabs(["📅 Gastos diários", "📊 Comparativo por categoria"])

with _tab_diario:
    _diario = preparar_gastos_diarios(txs_all, ano, mes, cumulative=False)
    _diario_acum = preparar_gastos_diarios(txs_all, ano, mes, cumulative=True)
    if _diario:
        _fig_d = go.Figure()
        _fig_d.add_trace(go.Bar(
            x=[r["date"] for r in _diario],
            y=[r["Gastos"] for r in _diario],
            name="Diário",
            marker_color="rgba(77,141,255,0.6)",
            hovertemplate="%{x}: R$ %{y:,.2f}<extra></extra>",
        ))
        _fig_d.add_trace(go.Scatter(
            x=[r["date"] for r in _diario_acum],
            y=[r["Gastos"] for r in _diario_acum],
            name="Acumulado",
            mode="lines",
            line=dict(color="#00C896", width=2),
            yaxis="y2",
            hovertemplate="Acum.: R$ %{y:,.2f}<extra></extra>",
        ))
        _fig_d.update_layout(
            height=260,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(showgrid=False, color="#888"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#888",
                       tickprefix="R$ "),
            yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#888",
                        tickprefix="R$ "),
            hovermode="x unified",
            barmode="group",
        )
        st.plotly_chart(_fig_d, use_container_width=True)
    else:
        st.info("Sem gastos registrados neste mês.")

with _tab_comp:
    _mes_ant = mes - 1 if mes > 1 else 12
    _ano_ant = ano if mes > 1 else ano - 1
    try:
        _txs_ant = tx_repo.list_by_month(_ano_ant, _mes_ant)
    except Exception:
        _txs_ant = []
    _comp = preparar_comparativo_categorias(txs_all, _txs_ant)
    if _comp:
        _fig_c = go.Figure()
        _fig_c.add_trace(go.Bar(
            name="Este mês",
            x=[r["categoria"] for r in _comp],
            y=[r["Este mês"] for r in _comp],
            marker_color="#4D8DFF",
            hovertemplate="%{x}<br>Este mês: R$ %{y:,.2f}<extra></extra>",
        ))
        _fig_c.add_trace(go.Bar(
            name="Mês anterior",
            x=[r["categoria"] for r in _comp],
            y=[r["Mês anterior"] for r in _comp],
            marker_color="rgba(255,255,255,0.15)",
            hovertemplate="%{x}<br>Mês ant.: R$ %{y:,.2f}<extra></extra>",
        ))
        _fig_c.update_layout(
            height=280,
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            xaxis=dict(showgrid=False, color="#888", tickangle=-30),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#888",
                       tickprefix="R$ "),
            hovermode="x unified",
        )
        st.plotly_chart(_fig_c, use_container_width=True)
    else:
        st.info("Sem dados para comparativo.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_tudo, tab_in, tab_out, tab_inv, tab_auto = st.tabs(
    ["Tudo", "Entradas", "Saídas", "Investimento", "Parcelas"]
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
        with st.expander("Editar · Excluir"):
            opts = {
                f"{t.date.strftime('%d/%m')} · {t.category.value} · {fmt_brl(t.amount)}": t
                for t in sorted(txs, key=lambda x: x.date, reverse=True)
            }
            sel_key = st.selectbox(
                "Selecionar lançamento",
                list(opts.keys()),
                label_visibility="collapsed",
            )
            sel_tx = opts[sel_key]
            col_e, col_d = st.columns(2)
            with col_e:
                if st.button("✏ Editar", use_container_width=True, key=f"edit_btn_{sel_tx.id}"):
                    _edit_dialog(sel_tx)
            with col_d:
                _confirm_key = f"confirm_del_{sel_tx.id}"
                if st.session_state.get(_confirm_key):
                    st.warning("Confirmar exclusão?")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("Sim, excluir", type="primary", use_container_width=True, key=f"yes_{sel_tx.id}"):
                            try:
                                # só reverter saldo se a tx estava PAGA
                                if sel_tx.account_id and sel_tx.status == TransactionStatus.PAGO:
                                    acc_repo.adjust_balance(sel_tx.account_id, -tx_balance_delta(float(sel_tx.amount), sel_tx.type))
                                tx_repo.delete(sel_tx.id)
                                st.session_state.pop(_confirm_key, None)
                                st.success("Excluído.")
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))
                    with cc2:
                        if st.button("Cancelar", use_container_width=True, key=f"no_{sel_tx.id}"):
                            st.session_state.pop(_confirm_key, None)
                            st.rerun()
                else:
                    if st.button("🗑 Excluir", type="secondary", use_container_width=True, key=f"del_btn_{sel_tx.id}"):
                        st.session_state[_confirm_key] = True
                        st.rerun()

    with col_right:
        by_cat: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
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

        by_pm: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
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
