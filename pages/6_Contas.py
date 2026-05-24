"""Cartões · Klipper — wallet, parcelamentos e contas."""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date
from decimal import Decimal
import html
import re

import plotly.graph_objects as go
import streamlit as st

from core.analytics import preparar_dados_gauge_limite
from core.installment_engine import calcular_comprometimento_mensal
from core.repositories import (
    BankAccountRepository, CreditCardRepository,
    InstallmentRepository, TransactionRepository,
)
from core.auth import require_auth
from core.styles import (
    bar_track, fmt_brl, inject_css, k_card_with_header,
    parcela_row, section_header, sidebar_engines, sidebar_user, sidebar_ai_qa, render_navigation,
    stat_card, load_page_icon,
    setup_sidebar,
)
from core.repositories import tx_balance_delta
from models.bank_account import AccountType, BankAccount
from models.credit_card import CreditCard
from models.transaction import Category, TransactionStatus, TransactionType

st.set_page_config(page_title="Cartões · Klipper", page_icon=load_page_icon(), layout="wide", initial_sidebar_state="collapsed")
inject_css()
require_auth()

acc_repo  = BankAccountRepository()
card_repo = CreditCardRepository()
inst_repo = InstallmentRepository()
tx_repo   = TransactionRepository()

hoje = date.today()

try:
    cartoes = card_repo.list_active()
    contas  = acc_repo.list_active()
    insts   = inst_repo.list_active()
    txs_mes = tx_repo.list_by_month(hoje.year, hoje.month)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    cartoes, contas, insts, txs_mes = [], [], [], []

_CAT_ICON = {
    "Moradia": "⌂", "Alimentação": "⊕", "Transporte": "⊡",
    "Saúde": "◎", "Educação": "◇", "Lazer": "◈",
    "Investimento": "▣", "Renda": "↑", "Freelance": "∞", "Outros": "○",
}

_HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?$")


def _safe_color(color: str, fallback: str = "#4A5568") -> str:
    """Valida cor hex antes de injetar em CSS. Retorna fallback se inválida."""
    return color if _HEX_COLOR_RE.match(color or "") else fallback


# ── Layout ────────────────────────────────────────────────────────────────────

setup_sidebar()

# ── Forms inline as expanders ─────────────────────────────────────────────
with st.expander("+ Novo cartão"):
    with st.form("form_cartao"):
        fc1, fc2 = st.columns(2)
        with fc1:
            nome_cart  = st.text_input("Nome*")
            banco_cart = st.text_input("Banco emissor")
            limite     = st.number_input("Limite (R$)", min_value=0.0, step=100.0, format="%.2f")
        with fc2:
            fecha_dia  = st.number_input("Fecha dia", min_value=1, max_value=31, value=1)
            vence_dia  = st.number_input("Vence dia", min_value=1, max_value=31, value=10)
            cor_cart   = st.color_picker("Cor", "#1E3A5F")
        if st.form_submit_button("Criar cartão", type="primary", use_container_width=True):
            if nome_cart.strip():
                try:
                    card_repo.create(CreditCard(
                        name=nome_cart, bank=banco_cart, limit_total=limite,
                        closing_day=int(fecha_dia), due_day=int(vence_dia),
                        color=cor_cart,
                    ))
                    st.success("Cartão criado.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

with st.expander("+ Nova conta bancária"):
    with st.form("form_conta"):
        cc1, cc2 = st.columns(2)
        with cc1:
            nome_conta = st.text_input("Nome*")
            banco_c    = st.text_input("Banco")
        with cc2:
            tipo_c     = st.selectbox("Tipo", [t.value for t in AccountType])
            saldo_ini  = st.number_input("Saldo inicial (R$)", step=0.01, format="%.2f")
            cor_conta  = st.color_picker("Cor", "#0F766E")
        if st.form_submit_button("Criar conta", type="primary", use_container_width=True):
            if nome_conta.strip():
                try:
                    acc_repo.create(BankAccount(
                        name=nome_conta, bank=banco_c,
                        type=AccountType(tipo_c), balance=saldo_ini, color=cor_conta,
                    ))
                    st.success("Conta criada.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

# ── Tabs ──────────────────────────────────────────────────────────────────
tab_cards, tab_parc, tab_contas = st.tabs(["Cartões", "Parcelas", "Contas"])

# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — Cartões
# ══════════════════════════════════════════════════════════════════════════
with tab_cards:
    # KPI strip
    total_usado  = sum(c.fatura_atual([t for t in txs_mes if t.card_id == c.id]) for c in cartoes)
    total_limite = sum(c.limit_total for c in cartoes)
    proxima_fat  = total_usado  # same-month estimate
    prox_venc_card = min(cartoes, key=lambda c: c.due_day, default=None)
    prox_venc_label = f"dia {prox_venc_card.due_day}" if prox_venc_card else "—"
    prox_venc_sub   = prox_venc_card.name if prox_venc_card else "—"

    st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:20px">
  {stat_card("Limite usado · total", fmt_brl(total_usado, compact=True),
         f"{(total_usado/total_limite*100):.0f}% de {fmt_brl(total_limite, compact=True)}" if total_limite else "sem cartões")}
  {stat_card("Próximas faturas · mês", fmt_brl(proxima_fat, compact=True),
         f"{len(cartoes)} cartões ativos", "brass")}
  {stat_card("Cartões ativos", str(len(cartoes)),
         "cadastrados no Klipper")}
  {stat_card("Próximo vencimento", prox_venc_label, prox_venc_sub, "warn")}
</div>
""", unsafe_allow_html=True)

    if not cartoes:
        st.markdown(
            '<div style="padding:64px 0;text-align:center;color:var(--ink-4)">nenhum cartão cadastrado · use o formulário acima</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(section_header("Carteira", "seus cartões"), unsafe_allow_html=True)

        # Wallet row — all cards as HTML
        card_items = []
        for c in cartoes:
            last4     = c.id[-4:].upper()
            bank_abbr = html.escape((c.bank or "")[:5].upper() or "CARD")
            safe_col  = _safe_color(c.color)
            card_items.append(f"""<div class="k-cardobj" style="
          background: linear-gradient(135deg, {safe_col} 0%, #0a0a0a 100%);
          color: white; border: 1px solid rgba(255,255,255,0.12);
          cursor: default;
        ">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <div>
              <div style="font-family:var(--font-sans);font-size:13px;font-weight:600;opacity:0.95">{html.escape(c.bank or c.name)}</div>
              <div style="font-family:var(--font-sans);font-size:11px;opacity:0.55;margin-top:2px">{html.escape(c.name)}</div>
            </div>
            <div style="font-family:var(--font-serif);font-size:14px;opacity:0.7;letter-spacing:0.04em">{bank_abbr}</div>
          </div>
          <div class="k-card-chip" style="position:absolute;top:56px;left:22px"></div>
          <div class="k-card-num" style="color:rgba(255,255,255,0.9)">•••• •••• •••• {last4}</div>
          <div style="display:flex;justify-content:space-between;align-items:flex-end">
            <div style="font-family:var(--font-sans);font-size:10px;opacity:0.5;text-transform:uppercase;letter-spacing:0.06em">{html.escape(str(st.session_state.get("user", "Titular")))}</div>
            <div style="text-align:right">
              <div style="font-family:var(--font-sans);font-size:9px;opacity:0.5">VENCE</div>
              <div style="font-family:var(--font-mono);font-size:12px;color:rgba(255,255,255,0.9)">dia {c.due_day}</div>
            </div>
          </div>
        </div>""")

        st.markdown(
            f'<div class="k-wallet">{"".join(card_items)}</div>',
            unsafe_allow_html=True,
        )

        # Card detail
        card_names = {c.name: c for c in cartoes}
        sel_name   = st.selectbox("Ver detalhes do cartão", list(card_names.keys()),
                                   label_visibility="collapsed")
        sel_card   = card_names[sel_name]
        card_txs   = [t for t in txs_mes if t.card_id == sel_card.id]
        fatura     = sel_card.fatura_atual(card_txs)
        uso_pct    = (fatura / sel_card.limit_total * 100) if sel_card.limit_total > 0 else 0
        disponivel = max(sel_card.limit_total - fatura, 0)

        st.markdown(
            section_header(f"{sel_card.bank} · {sel_card.name}", "detalhes · lançamentos do mês"),
            unsafe_allow_html=True,
        )

        col_detail, col_feed = st.columns([1, 2], gap="large")

        with col_detail:
            # Gauge Plotly de uso do limite
            _gauge = preparar_dados_gauge_limite(fatura, sel_card.limit_total)
            _gauge_color = (
                "#EF4444" if _gauge["status"] == "estouro"
                else "#F59E0B" if _gauge["status"] == "alerta"
                else "#00C896"
            )
            _fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=_gauge["pct_uso"],
                number=dict(suffix="%", font=dict(size=28, color="#F2EAD3")),
                delta=dict(
                    reference=80,
                    increasing=dict(color="#EF4444"),
                    decreasing=dict(color="#00C896"),
                    font=dict(size=12),
                ),
                gauge=dict(
                    axis=dict(
                        range=[0, 100],
                        tickwidth=1,
                        tickcolor="#3A3A3A",
                        tickfont=dict(size=10, color="#5C5746"),
                    ),
                    bar=dict(color=_gauge_color, thickness=0.25),
                    bgcolor="rgba(0,0,0,0)",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 50],  color="rgba(0,200,150,0.06)"),
                        dict(range=[50, 80], color="rgba(245,158,11,0.06)"),
                        dict(range=[80, 100], color="rgba(239,68,68,0.06)"),
                    ],
                    threshold=dict(
                        line=dict(color="#EF4444", width=2),
                        thickness=0.75,
                        value=80,
                    ),
                ),
                title=dict(
                    text=f"Uso do limite<br><span style='font-size:11px;color:#5C5746'>"
                         f"{fmt_brl(_gauge['usado'], compact=True)} de {fmt_brl(_gauge['limite'], compact=True)}</span>",
                    font=dict(size=13, color="#8F8770"),
                ),
            ))
            _fig_gauge.update_layout(
                height=220,
                margin=dict(l=20, r=20, t=20, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Geist Mono, monospace"),
            )
            st.plotly_chart(_fig_gauge, use_container_width=True)
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'font-family:var(--font-mono);font-size:10px;color:var(--ink-3);'
                f'margin:-8px 0 12px">'
                f'<span>fecha dia {sel_card.closing_day}</span>'
                f'<span>{fmt_brl(_gauge["disponivel"], compact=True)} disponível</span>'
                f'<span>vence dia {sel_card.due_day}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # Health card
            by_cat: dict[str, Decimal] = defaultdict(lambda: Decimal(0))
            for t in card_txs:
                by_cat[t.category.value] += t.amount
            top_cat = max(by_cat, key=by_cat.get) if by_cat else "—"
            top_pct = (by_cat[top_cat] / fatura * 100) if fatura > 0 else 0
            maior   = max((t.amount for t in card_txs), default=0)
            maior_tx = next(
                (t for t in card_txs if t.amount == maior), None
            )
            recorrentes = len([t for t in card_txs if t.installment_id])

            saude_rows = [
                ("Categoria dominante", f"{top_cat} · {top_pct:.0f}%"),
                ("Lançamentos no mês", str(len(card_txs))),
                ("Maior compra", f"{fmt_brl(maior, compact=True)} · {(maior_tx.notes or maior_tx.category.value) if maior_tx else '—'}"),
                ("Recorrentes", f"{recorrentes} ativas"),
            ]
            rows_html = "".join(
                f"""<div style="display:flex;justify-content:space-between;
              font-family:var(--font-sans);font-size:12px;padding:6px 0;
              border-top:1px solid var(--rule)">
              <span style="color:var(--ink-3)">{l}</span>
              <span class="mono" style="color:var(--ink)">{v}</span>
            </div>"""
                for l, v in saude_rows
            )
            st.markdown(k_card_with_header("Saúde do uso", rows_html, "comportamento"), unsafe_allow_html=True)

        with col_feed:
            if card_txs:
                feed_rows = []
                for t in sorted(card_txs, key=lambda x: x.date, reverse=True):
                    icon = _CAT_ICON.get(t.category.value, "○")
                    title = html.escape(t.notes) if t.notes else t.category.value
                    meta  = f"{t.category.value} · {t.date.strftime('%d/%m')}"
                    feed_rows.append(f"""<div class="k-feed-row">
  <div class="k-feed-icon out">{icon}</div>
  <div class="k-feed-body">
<div class="k-feed-title">{title}</div>
<div class="k-feed-meta">{meta}</div>
  </div>
  <div class="k-feed-val">−{fmt_brl(t.amount, compact=True)}</div>
</div>""")
                feed_html = f'<div style="display:flex;flex-direction:column;gap:6px;padding:4px 0">{"".join(feed_rows)}</div>'
            else:
                feed_html = '<div style="padding:40px 0;text-align:center;color:var(--ink-4)">sem lançamentos neste cartão no mês</div>'

            st.markdown(
                k_card_with_header("Lançamentos · 30d", feed_html, sel_card.bank),
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — Parcelas
# ══════════════════════════════════════════════════════════════════════════
with tab_parc:
    if not insts:
        st.markdown(
            '<div style="padding:64px 0;text-align:center;color:var(--ink-4)">nenhum parcelamento ativo</div>',
            unsafe_allow_html=True,
        )
    else:
        comp           = calcular_comprometimento_mensal(insts)
        mensal_total   = sum(i.installment_amount for i in insts)
        restante_total = sum(i.total_remaining for i in insts)
        principal      = sum(i.total_amount for i in insts)
        pago           = sum(i.n_paid * i.installment_amount for i in insts)
        pct_quitado    = (pago / principal * 100) if principal > 0 else 0
        n_restantes    = sum(i.n_remaining for i in insts)

        st.markdown(f"""
<div class="k-grid k-cols-4" style="margin-bottom:20px">
  {stat_card("Parcela mensal · total", fmt_brl(mensal_total),
         f"{len(insts)} ativas", "brass")}
  {stat_card("Saldo a pagar", fmt_brl(restante_total, compact=True),
         f"{n_restantes} parcelas restantes")}
  {stat_card("Principal contratado", fmt_brl(principal, compact=True),
         f"{pct_quitado:.0f}% quitado · {fmt_brl(pago, compact=True)}", "pos")}
  {stat_card("% da renda mensal", "—",
         "configure renda no Dashboard")}
</div>
""", unsafe_allow_html=True)

        st.markdown(section_header("Compromissos parcelados", "timeline visual"), unsafe_allow_html=True)

        # Card name lookup
        card_map_id = {}
        try:
            for c in card_repo.list_active():
                card_map_id[c.id] = c.name
        except Exception:
            pass

        for inst in insts:
            card_name = card_map_id.get(inst.card_id or "", "")
            prox_str  = inst.next_due_date.strftime("%d/%m/%Y") if inst.next_due_date else "—"
            start_str = inst.start_date.strftime("%b/%Y")
            end_date  = inst.next_due_date  # approximate
            end_str   = (
                inst.start_date.replace(
                    year=inst.start_date.year + (inst.start_date.month + inst.n_total - 2) // 12,
                    month=(inst.start_date.month + inst.n_total - 2) % 12 + 1,
                ).strftime("%b/%Y")
                if inst.n_total > 0 else "—"
            )

            # Dot timeline
            dots = "".join(
                f'<div style="height:8px;border-radius:2px;'
                f'background:{"var(--brass)" if i < inst.n_paid else "var(--surface-2)"};'
                f'border:1px solid {"transparent" if i < inst.n_paid else "var(--rule)"};'
                f'box-shadow:{"0 0 8px var(--brass-glow)" if i == inst.n_paid else "none"};'
                f'opacity:{1 if i < inst.n_paid else 0.7}'
                f'"></div>'
                for i in range(inst.n_total)
            )
            dot_grid = (
                f'<div style="display:grid;grid-template-columns:repeat({inst.n_total},1fr);'
                f'gap:2px;margin-top:14px">{dots}</div>'
            )
            foot = (
                f'<div style="display:flex;justify-content:space-between;margin-top:8px;'
                f'font-family:var(--font-mono);font-size:10px;color:var(--ink-4)">'
                f'<span>total: <span style="color:var(--ink-3)">{fmt_brl(inst.total_amount, compact=True)}</span></span>'
                f'<span>pago: <span class="pos">{fmt_brl(pago, compact=True)}</span></span>'
                f'<span>restante: <span style="color:var(--ink-2)">{fmt_brl(inst.total_remaining, compact=True)}</span></span>'
                f'</div>'
            )

            head = f"""<div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px">
  <div>
<div style="font-family:var(--font-sans);font-size:14px;color:var(--ink);font-weight:500">{inst.description}</div>
<div style="font-family:var(--font-sans);font-size:11px;color:var(--ink-3);margin-top:3px">
  {inst.category} · <span class="mono">{start_str} → {end_str}</span>{"· " + card_name if card_name else ""}
</div>
  </div>
  <div style="text-align:right;flex-shrink:0">
<div class="mono" style="font-size:18px;color:var(--brass);font-variant-numeric:tabular-nums">
  {fmt_brl(inst.installment_amount)}<span class="muted" style="font-size:11px"> /mês</span>
</div>
<div class="mono muted" style="font-size:11px">{inst.n_paid}/{inst.n_total} pagas · faltam {fmt_brl(inst.total_remaining, compact=True)}</div>
  </div>
</div>"""

            st.markdown(
                f'<div class="k-parcela">{head}{dot_grid}{foot}</div>',
                unsafe_allow_html=True,
            )

        # Mark paid action
        with st.expander("Marcar parcela como paga"):
            opts = {f"{i.description} ({i.n_paid}/{i.n_total})": i for i in insts}
            sel_p = st.selectbox("Parcelamento", list(opts.keys()), key="mark_paid_sel",
                                  label_visibility="collapsed")
            if st.button("Marcar paga", key="btn_mark_paid"):
                try:
                    inst = opts[sel_p]
                    # 1. Atualizar a Transaction PENDENTE mais próxima para PAGO
                    pending_txs = tx_repo.list_pending_by_installment(inst.id)
                    if pending_txs:
                        tx_to_pay = pending_txs[0]
                        from models.transaction import Transaction
                        paid_tx = Transaction(**{
                            **tx_to_pay.model_dump(),
                            "status": TransactionStatus.PAGO,
                        })
                        tx_repo.update(paid_tx)
                        # 2. Ajustar saldo da conta
                        if paid_tx.account_id:
                            acc_repo.adjust_balance(
                                paid_tx.account_id,
                                tx_balance_delta(float(paid_tx.amount), paid_tx.type),
                            )
                    # 3. Incrementar contador
                    inst_repo.mark_paid(inst.id)
                    st.success("Parcela marcada como paga.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # Horizon chart
        if comp:
            st.markdown(section_header("Horizonte de pagamentos", "próximos 12 meses"), unsafe_allow_html=True)
            meses = sorted(comp.keys())[:12]
            hoje_str = f"{hoje.year}-{hoje.month:02d}"
            labels   = [m[5:] for m in meses]
            values   = [comp[m] for m in meses]
            colors   = [
                "rgba(217, 178, 111, 0.85)" if m == hoje_str else "rgba(255, 255, 255, 0.10)"
                for m in meses
            ]
            fig = go.Figure(go.Bar(
                x=labels, y=values,
                marker_color=colors,
                marker_line_width=0,
                text=[fmt_brl(v, compact=True) for v in values],
                textposition="outside",
                textfont=dict(family="Geist Mono, monospace", size=10, color="#8F8770"),
            ))
            fig.update_layout(
                height=220,
                margin=dict(l=0, r=0, t=32, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, showline=False, zeroline=False,
                           tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                yaxis=dict(showgrid=False, showline=False, zeroline=False, tickformat=",.0f",
                           tickfont=dict(family="Geist Mono, monospace", color="#5C5746", size=10)),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — Contas Bancárias
# ══════════════════════════════════════════════════════════════════════════
with tab_contas:
    st.markdown(section_header("Contas bancárias", "saldos e movimentação"), unsafe_allow_html=True)

    if contas:
        saldo_total = sum(c.balance for c in contas)
        st.markdown(
            f'<div class="k-grid k-cols-4" style="margin-bottom:20px">'
            f'{stat_card("Saldo total", fmt_brl(saldo_total, compact=True), f"{len(contas)} contas ativas", "pos")}'
            f'</div>',
            unsafe_allow_html=True,
        )

        account_cards = []
        tipo_labels = {"CORRENTE": "Corrente", "POUPANCA": "Poupança", "INVESTIMENTO": "Investimento"}
        for c in contas:
            tipo      = tipo_labels.get(c.type.value, c.type.value)
            color     = "var(--moss)" if c.balance >= 0 else "var(--rust)"
            safe_col  = _safe_color(c.color)
            account_cards.append(f"""<div class="k-stat-card" style="border-left:3px solid {safe_col}">
  <div style="display:flex;align-items:baseline;justify-content:space-between;gap:8px">
<div>
  <div style="font-family:var(--font-sans);font-size:14px;color:var(--ink);font-weight:500">{html.escape(c.name)}</div>
  <div style="font-family:var(--font-sans);font-size:11px;color:var(--ink-3);margin-top:2px">{html.escape(c.bank or "")} · {tipo}</div>
</div>
<div class="mono" style="font-size:22px;color:{color};font-variant-numeric:tabular-nums;flex-shrink:0">
  {fmt_brl(c.balance, compact=True)}
</div>
  </div>
</div>""")

        cols = st.columns(min(len(contas), 3))
        for i, html_card in enumerate(account_cards):
            with cols[i % 3]:
                st.markdown(html_card, unsafe_allow_html=True)

        # Update balance
        with st.expander("Atualizar saldo"):
            conta_opts = {c.name: c.id for c in contas}
            sel_c = st.selectbox("Conta", list(conta_opts.keys()), key="upd_acc",
                                  label_visibility="collapsed")
            novo_saldo = st.number_input("Novo saldo (R$)", step=0.01, format="%.2f", key="upd_bal")
            if st.button("Atualizar", key="btn_upd_acc"):
                try:
                    acc_repo.update_balance(conta_opts[sel_c], novo_saldo)
                    st.success("Saldo atualizado.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    else:
        st.markdown(
            '<div style="padding:64px 0;text-align:center;color:var(--ink-4)">nenhuma conta cadastrada · use o formulário acima</div>',
            unsafe_allow_html=True,
        )
