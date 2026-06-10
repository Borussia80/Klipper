"""core/modals.py — Todos os modais (@st.dialog) do Klipper.

Responsabilidade única: renderizar formulários modais e delegar
persistência aos repositórios. Não contém lógica de negócio.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal

import streamlit as st

from core.styles import CAT_COLORS, fmt_brl
from core.repositories import (
    TransactionRepository,
    BankAccountRepository,
    InvestmentRepository,
)
from models.transaction import Transaction, TransactionType, TransactionStatus
from models.investment import Investment

_log = logging.getLogger(__name__)

# ── Helpers ───────────────────────────────────────────────────────────────────

_CATEGORIES = list(CAT_COLORS.keys())

_STATUS_LABELS = {
    TransactionStatus.CONFIRMADO: "✅ Confirmado",
    TransactionStatus.PENDENTE:   "⏳ Pendente",
    TransactionStatus.AGENDADO:   "📅 Agendado",
}

_TYPE_LABELS = {
    TransactionType.GANHO: "⬆ Ganho / Receita",
    TransactionType.GASTO: "⬇ Gasto / Despesa",
}


def _account_options() -> dict[str, str]:
    """Retorna {display_label: account_id} para o selectbox de contas."""
    try:
        contas = BankAccountRepository().list_active()
        return {f"{c.name} · {fmt_brl(c.balance, compact=True)}": str(c.id) for c in contas}
    except Exception as e:
        _log.warning("Contas indisponíveis: %s", e)
        return {}


def _balance_delta(tx_type: TransactionType, amount: Decimal) -> Decimal:
    """Calcula o delta de saldo para adjust_balance."""
    return amount if tx_type == TransactionType.GANHO else -amount


# ── Modal: Confirm Delete (genérico) ─────────────────────────────────────────

@st.dialog("Confirmar exclusão", width="small")
def modal_confirm_delete(label: str, on_confirm) -> None:  # type: ignore[type-arg]
    """Modal de confirmação genérico.

    Args:
        label:      Descrição do item a excluir (ex: nome da transação).
        on_confirm: Callable executado ao confirmar — deve fazer a exclusão.
    """
    st.markdown(
        f'<p style="color:var(--ink-3);font-size:14px;margin-bottom:16px">'
        f'Você está prestes a excluir <strong style="color:var(--rust)">'
        f'{label}</strong>. Esta ação não pode ser desfeita.</p>',
        unsafe_allow_html=True,
    )
    col_cancel, col_confirm = st.columns(2)
    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col_confirm:
        if st.button("Excluir", type="primary", use_container_width=True):
            try:
                on_confirm()
                st.toast("Item excluído.", icon="🗑️")
                st.rerun()
            except Exception as e:
                st.error(str(e))


# ── Modal: Add Transaction ────────────────────────────────────────────────────

@st.dialog("Lançar transação", width="large")
def modal_add_transaction() -> None:
    """Form de nova transação. Persiste via TransactionRepository."""
    repo   = TransactionRepository()
    contas = _account_options()

    with st.container():
        # Linha 1: data + tipo
        col_date, col_type = st.columns([1, 1])
        with col_date:
            tx_date = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        with col_type:
            tipo_label = st.selectbox(
                "Tipo",
                options=list(_TYPE_LABELS.values()),
                index=1,
            )
            tipo = next(k for k, v in _TYPE_LABELS.items() if v == tipo_label)

        # Linha 2: valor + categoria
        col_amt, col_cat = st.columns([1, 1])
        with col_amt:
            valor_str = st.text_input(
                "Valor (R$)", placeholder="0,00",
                help="Use vírgula como separador decimal."
            )
        with col_cat:
            categoria = st.selectbox("Categoria", options=_CATEGORIES)

        # Linha 3: descrição
        descricao = st.text_input("Descrição", placeholder="Ex: Mercado, Salário…")

        # Linha 4: conta + status
        col_acc, col_status = st.columns([1, 1])
        with col_acc:
            if contas:
                conta_label = st.selectbox("Conta", options=list(contas.keys()))
                account_id  = contas[conta_label]
            else:
                st.warning("Nenhuma conta ativa encontrada.")
                account_id = None
        with col_status:
            status_label = st.selectbox(
                "Status",
                options=list(_STATUS_LABELS.values()),
                index=0,
            )
            status = next(k for k, v in _STATUS_LABELS.items() if v == status_label)

        # Notas (opcional)
        notas = st.text_area("Notas (opcional)", height=68, placeholder="Observações…")

        st.divider()

        col_cancel, col_save = st.columns([1, 2])
        with col_cancel:
            if st.button("Cancelar", use_container_width=True):
                st.rerun()
        with col_save:
            if st.button("Salvar transação", type="primary", use_container_width=True):
                # Validação
                try:
                    valor_dec = Decimal(valor_str.replace(",", ".").replace("R$", "").strip())
                    if valor_dec <= 0:
                        raise ValueError("Valor deve ser positivo.")
                except Exception:
                    st.error("Valor inválido. Use o formato: 1234,56")
                    return

                if not descricao.strip():
                    st.error("Descrição obrigatória.")
                    return

                if not account_id:
                    st.error("Selecione uma conta.")
                    return

                try:
                    tx = Transaction(
                        date=tx_date,
                        amount=valor_dec,
                        type=tipo,
                        category=categoria,
                        description=descricao.strip(),
                        account_id=account_id,
                        status=status,
                        notes=notas.strip() or None,
                    )
                    repo.create(tx)
                    BankAccountRepository().adjust_balance(
                        account_id, _balance_delta(tipo, valor_dec)
                    )
                    st.toast(f"Transação salva: {descricao}", icon="✅")
                    st.rerun()
                except Exception as e:
                    _log.error("Erro ao salvar transação: %s", e)
                    st.error(f"Erro ao salvar: {e}")


# ── Modal: Edit Transaction ───────────────────────────────────────────────────

@st.dialog("Editar transação", width="large")
def modal_edit_transaction(tx_id: str) -> None:
    """Form de edição de transação existente, pre-filled."""
    repo = TransactionRepository()
    contas = _account_options()

    try:
        tx = repo.get_by_id(tx_id)
    except Exception as e:
        st.error(f"Transação não encontrada: {e}")
        return

    with st.container():
        col_date, col_type = st.columns([1, 1])
        with col_date:
            tx_date = st.date_input(
                "Data", value=tx.date, format="DD/MM/YYYY"
            )
        with col_type:
            tipo_label = st.selectbox(
                "Tipo",
                options=list(_TYPE_LABELS.values()),
                index=list(_TYPE_LABELS.keys()).index(tx.type),
            )
            tipo = next(k for k, v in _TYPE_LABELS.items() if v == tipo_label)

        col_amt, col_cat = st.columns([1, 1])
        with col_amt:
            valor_str = st.text_input(
                "Valor (R$)",
                value=str(tx.amount).replace(".", ","),
            )
        with col_cat:
            cat_idx = _CATEGORIES.index(tx.category) if tx.category in _CATEGORIES else 0
            categoria = st.selectbox("Categoria", options=_CATEGORIES, index=cat_idx)

        descricao = st.text_input("Descrição", value=tx.description)

        col_acc, col_status = st.columns([1, 1])
        with col_acc:
            if contas:
                acc_labels = list(contas.keys())
                acc_ids    = list(contas.values())
                acc_idx    = acc_ids.index(str(tx.account_id)) if str(tx.account_id) in acc_ids else 0
                conta_label = st.selectbox("Conta", options=acc_labels, index=acc_idx)
                account_id  = contas[conta_label]
            else:
                account_id = str(tx.account_id)

        with col_status:
            status_label = st.selectbox(
                "Status",
                options=list(_STATUS_LABELS.values()),
                index=list(_STATUS_LABELS.keys()).index(tx.status),
            )
            status = next(k for k, v in _STATUS_LABELS.items() if v == status_label)

        notas = st.text_area(
            "Notas (opcional)", value=tx.notes or "", height=68
        )

        st.divider()
        col_del, col_cancel, col_save = st.columns([1, 1, 2])
        with col_del:
            if st.button("🗑 Excluir", use_container_width=True):
                modal_confirm_delete(
                    tx.description,
                    on_confirm=lambda: (
                        BankAccountRepository().adjust_balance(
                            str(tx.account_id), -_balance_delta(tx.type, tx.amount)
                        ),
                        repo.delete(tx_id),
                    ),
                )
        with col_cancel:
            if st.button("Cancelar", use_container_width=True):
                st.rerun()
        with col_save:
            if st.button("Atualizar", type="primary", use_container_width=True):
                try:
                    novo_valor = Decimal(valor_str.replace(",", ".").replace("R$", "").strip())
                    if novo_valor <= 0:
                        raise ValueError()
                except Exception:
                    st.error("Valor inválido.")
                    return

                try:
                    # Reverte saldo antigo e aplica novo
                    acc_repo = BankAccountRepository()
                    acc_repo.adjust_balance(
                        str(tx.account_id), -_balance_delta(tx.type, tx.amount)
                    )
                    tx.date        = tx_date
                    tx.amount      = novo_valor
                    tx.type        = tipo
                    tx.category    = categoria
                    tx.description = descricao.strip()
                    tx.account_id  = account_id
                    tx.status      = status
                    tx.notes       = notas.strip() or None
                    repo.update(tx)
                    acc_repo.adjust_balance(
                        account_id, _balance_delta(tipo, novo_valor)
                    )
                    st.toast(f"Atualizado: {descricao}", icon="✅")
                    st.rerun()
                except Exception as e:
                    _log.error("Erro ao editar transação: %s", e)
                    st.error(str(e))


# ── Modal: Transfer ───────────────────────────────────────────────────────────

@st.dialog("Transferência entre contas", width="small")
def modal_transfer() -> None:
    """Transfere saldo entre contas bancárias."""
    contas = _account_options()
    if len(contas) < 2:
        st.warning("É necessário ter pelo menos 2 contas ativas para transferir.")
        return

    labels = list(contas.keys())

    origem_label  = st.selectbox("Conta origem",  options=labels, index=0)
    destino_label = st.selectbox("Conta destino", options=labels, index=1)

    valor_str = st.text_input("Valor (R$)", placeholder="0,00")
    tx_date   = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
    descricao = st.text_input("Descrição", value="Transferência")

    st.divider()
    col_cancel, col_save = st.columns([1, 2])
    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col_save:
        if st.button("Transferir", type="primary", use_container_width=True):
            if origem_label == destino_label:
                st.error("Origem e destino não podem ser iguais.")
                return
            try:
                valor = Decimal(valor_str.replace(",", ".").strip())
                if valor <= 0:
                    raise ValueError()
            except Exception:
                st.error("Valor inválido.")
                return

            try:
                origem_id  = contas[origem_label]
                destino_id = contas[destino_label]
                repo       = TransactionRepository()
                acc_repo   = BankAccountRepository()

                # Gasto na origem
                tx_saida = Transaction(
                    date=tx_date, amount=valor,
                    type=TransactionType.GASTO,
                    category="Outros",
                    description=f"{descricao} → {destino_label.split('·')[0].strip()}",
                    account_id=origem_id,
                    status=TransactionStatus.CONFIRMADO,
                )
                repo.create(tx_saida)
                acc_repo.adjust_balance(origem_id, -valor)

                # Ganho no destino
                tx_entrada = Transaction(
                    date=tx_date, amount=valor,
                    type=TransactionType.GANHO,
                    category="Outros",
                    description=f"{descricao} ← {origem_label.split('·')[0].strip()}",
                    account_id=destino_id,
                    status=TransactionStatus.CONFIRMADO,
                )
                repo.create(tx_entrada)
                acc_repo.adjust_balance(destino_id, valor)

                st.toast(f"Transferência de {fmt_brl(valor)} realizada ✓", icon="⇄")
                st.rerun()
            except Exception as e:
                _log.error("Erro na transferência: %s", e)
                st.error(str(e))


# ── Modal: Add Investment ─────────────────────────────────────────────────────

@st.dialog("Nova posição", width="large")
def modal_add_investment() -> None:
    """Form de novo investimento com lookup de cotação."""
    inv_repo = InvestmentRepository()
    contas   = _account_options()

    # ── Lookup de ticker ──
    col_ticker, col_search = st.columns([3, 1])
    with col_ticker:
        ticker = st.text_input(
            "Ticker", placeholder="Ex: MXRF11, PETR4, TESOURO-2029",
            key="inv_ticker_input",
        ).upper().strip()
    with col_search:
        st.write("")  # alinha verticalmente
        buscar = st.button("🔍 Buscar", use_container_width=True)

    # Dados auto-preenchidos pelo lookup
    preco_atual = st.session_state.get("inv_preco_lookup", "")
    dy_lookup   = st.session_state.get("inv_dy_lookup", "")
    pvp_lookup  = st.session_state.get("inv_pvp_lookup", "")

    if buscar and ticker:
        try:
            from core.market_data import get_quote
            quote = get_quote(ticker)
            st.session_state["inv_preco_lookup"] = str(quote.price).replace(".", ",")
            st.session_state["inv_dy_lookup"]    = str(round(quote.dy or 0, 2)).replace(".", ",")
            st.session_state["inv_pvp_lookup"]   = str(round(quote.pvp or 0, 2)).replace(".", ",")
            st.toast(f"{ticker}: R$ {quote.price:.2f}", icon="📊")
            st.rerun()
        except Exception as e:
            st.warning(f"Cotação indisponível: {e}. Preencha manualmente.")

    # ── Campos principais ──
    col_qty, col_price = st.columns(2)
    with col_qty:
        quantidade_str = st.text_input("Quantidade", placeholder="100")
    with col_price:
        preco_medio_str = st.text_input(
            "Preço médio (R$)",
            value=preco_atual,
            placeholder="0,00",
        )

    col_dy, col_pvp = st.columns(2)
    with col_dy:
        dy_str  = st.text_input("DY (%)", value=dy_lookup, placeholder="0,00")
    with col_pvp:
        pvp_str = st.text_input("P/VP", value=pvp_lookup, placeholder="1,00")

    setor = st.selectbox(
        "Classe de ativo",
        options=["FII", "Ação", "ETF", "Renda Fixa", "Caixa", "Exterior", "Cripto"],
    )

    if contas:
        custódia_label = st.selectbox("Conta custódia", options=list(contas.keys()))
        custódia_id    = contas[custódia_label]
    else:
        custódia_id = None

    notas = st.text_input("Notas (opcional)", placeholder="Estratégia, motivo…")

    st.divider()
    col_cancel, col_save = st.columns([1, 2])
    with col_cancel:
        if st.button("Cancelar", use_container_width=True, key="inv_add_cancel"):
            for k in ["inv_preco_lookup", "inv_dy_lookup", "inv_pvp_lookup"]:
                st.session_state.pop(k, None)
            st.rerun()
    with col_save:
        if st.button("Salvar posição", type="primary", use_container_width=True):
            if not ticker:
                st.error("Ticker obrigatório.")
                return
            try:
                qty   = Decimal(quantidade_str.replace(",", ".").strip())
                preco = Decimal(preco_medio_str.replace(",", ".").replace("R$", "").strip())
                dy    = Decimal(dy_str.replace(",", ".").strip() or "0")
                pvp   = Decimal(pvp_str.replace(",", ".").strip() or "0")
                if qty <= 0 or preco <= 0:
                    raise ValueError()
            except Exception:
                st.error("Quantidade ou preço inválido.")
                return

            try:
                inv = Investment(
                    ticker=ticker,
                    quantity=qty,
                    avg_price=preco,
                    dy=dy,
                    pvp=pvp,
                    sector=setor,
                    account_id=custódia_id,
                    notes=notas.strip() or None,
                )
                inv_repo.create(inv)
                for k in ["inv_preco_lookup", "inv_dy_lookup", "inv_pvp_lookup"]:
                    st.session_state.pop(k, None)
                st.toast(f"Posição adicionada: {ticker}", icon="▲")
                st.rerun()
            except Exception as e:
                _log.error("Erro ao salvar investimento: %s", e)
                st.error(str(e))


# ── Modal: Edit Investment ────────────────────────────────────────────────────

@st.dialog("Editar posição", width="large")
def modal_edit_investment(inv_id: str) -> None:
    """Form de edição de posição existente, pre-filled."""
    inv_repo = InvestmentRepository()
    contas   = _account_options()

    try:
        inv = inv_repo.get_by_id(inv_id)
    except Exception as e:
        st.error(f"Posição não encontrada: {e}")
        return

    ticker = st.text_input("Ticker", value=inv.ticker).upper().strip()

    col_qty, col_price = st.columns(2)
    with col_qty:
        quantidade_str = st.text_input(
            "Quantidade", value=str(inv.quantity).replace(".", ",")
        )
    with col_price:
        preco_str = st.text_input(
            "Preço médio (R$)", value=str(inv.avg_price).replace(".", ",")
        )

    col_dy, col_pvp = st.columns(2)
    with col_dy:
        dy_str  = st.text_input("DY (%)", value=str(inv.dy or 0).replace(".", ","))
    with col_pvp:
        pvp_str = st.text_input("P/VP", value=str(inv.pvp or 0).replace(".", ","))

    setores = ["FII", "Ação", "ETF", "Renda Fixa", "Caixa", "Exterior", "Cripto"]
    setor_idx = setores.index(inv.sector) if inv.sector in setores else 0
    setor = st.selectbox("Classe de ativo", options=setores, index=setor_idx)

    if contas:
        acc_labels = list(contas.keys())
        acc_ids    = list(contas.values())
        acc_idx    = acc_ids.index(str(inv.account_id)) if str(inv.account_id) in acc_ids else 0
        custódia_label = st.selectbox("Conta custódia", options=acc_labels, index=acc_idx)
        custódia_id    = contas[custódia_label]
    else:
        custódia_id = str(inv.account_id)

    notas = st.text_input("Notas", value=inv.notes or "")

    st.divider()
    col_del, col_cancel, col_save = st.columns([1, 1, 2])
    with col_del:
        if st.button("🗑 Excluir", use_container_width=True):
            modal_confirm_delete(
                inv.ticker,
                on_confirm=lambda: inv_repo.delete(inv_id),
            )
    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col_save:
        if st.button("Atualizar", type="primary", use_container_width=True):
            try:
                inv.ticker     = ticker
                inv.quantity   = Decimal(quantidade_str.replace(",", ".").strip())
                inv.avg_price  = Decimal(preco_str.replace(",", ".").replace("R$", "").strip())
                inv.dy         = Decimal(dy_str.replace(",", ".").strip() or "0")
                inv.pvp        = Decimal(pvp_str.replace(",", ".").strip() or "0")
                inv.sector     = setor
                inv.account_id = custódia_id
                inv.notes      = notas.strip() or None
                inv_repo.update(inv)
                st.toast(f"Posição atualizada: {ticker}", icon="✅")
                st.rerun()
            except Exception as e:
                _log.error("Erro ao editar investimento: %s", e)
                st.error(str(e))
