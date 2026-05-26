"""PATCH-6_Contas_dialogs.py
Funções @st.dialog para substituir os st.expander em 6_Contas.py.

INSTRUÇÕES PARA O CLAUDE CODE:
1. Adicione as duas funções abaixo ANTES da linha setup_sidebar() em 6_Contas.py
2. Substitua os dois blocos `with st.expander(...)` pelos botões abaixo
3. Remova os imports que só eram usados nos expanders se ficarem órfãos

ONDE INSERIR OS BOTÕES (após setup_sidebar()):
    col_nc, col_nb, _ = st.columns([1, 1, 4])
    with col_nc:
        if st.button("＋ Novo cartão", use_container_width=True):
            dialog_novo_cartao()
    with col_nb:
        if st.button("＋ Nova conta", use_container_width=True):
            dialog_nova_conta()
"""

import streamlit as st
from models.bank_account import AccountType, BankAccount
from models.credit_card import CreditCard


@st.dialog("Novo cartão de crédito", width="large")
def dialog_novo_cartao() -> None:
    """Cadastra novo cartão de crédito via modal."""
    from core.repositories import CreditCardRepository
    card_repo = CreditCardRepository()

    fc1, fc2 = st.columns(2)
    with fc1:
        nome_cart  = st.text_input("Nome do cartão*", placeholder="Ex: Nubank Platinum")
        banco_cart = st.text_input("Banco emissor", placeholder="Nubank, Itaú…")
        limite     = st.number_input(
            "Limite total (R$)", min_value=0.0, step=100.0, format="%.2f"
        )
    with fc2:
        fecha_dia = st.number_input("Fecha dia", min_value=1, max_value=28, value=1)
        vence_dia = st.number_input("Vence dia", min_value=1, max_value=28, value=10)
        cor_cart  = st.color_picker("Cor do cartão", "#1E3A5F")

    st.divider()
    col_cancel, col_save = st.columns([1, 2])
    with col_cancel:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col_save:
        if st.button("Criar cartão", type="primary", use_container_width=True):
            if not nome_cart.strip():
                st.error("Nome obrigatório.")
                return
            try:
                card_repo.create(CreditCard(
                    name=nome_cart.strip(),
                    bank=banco_cart.strip() or None,
                    limit_total=limite,
                    closing_day=int(fecha_dia),
                    due_day=int(vence_dia),
                    color=cor_cart,
                ))
                st.toast(f"Cartão '{nome_cart}' criado ✓", icon="💳")
                st.rerun()
            except Exception as e:
                st.error(str(e))


@st.dialog("Nova conta bancária", width="large")
def dialog_nova_conta() -> None:
    """Cadastra nova conta bancária via modal."""
    from core.repositories import BankAccountRepository
    acc_repo = BankAccountRepository()

    cc1, cc2 = st.columns(2)
    with cc1:
        nome_conta = st.text_input("Nome*", placeholder="Ex: Conta Corrente Itaú")
        banco_c    = st.text_input("Banco", placeholder="Itaú, BTG, XP…")
    with cc2:
        tipo_c    = st.selectbox("Tipo de conta", [t.value for t in AccountType])
        saldo_ini = st.number_input(
            "Saldo inicial (R$)", min_value=0.0, step=0.01, format="%.2f",
            help="Saldo atual da conta no momento do cadastro."
        )
        cor_conta = st.color_picker("Cor", "#0F766E")

    st.divider()
    col_cancel, col_save = st.columns([1, 2])
    with col_cancel:
        if st.button("Cancelar", use_container_width=True, key="nc_cancel"):
            st.rerun()
    with col_save:
        if st.button("Criar conta", type="primary", use_container_width=True):
            if not nome_conta.strip():
                st.error("Nome obrigatório.")
                return
            try:
                acc_repo.create(BankAccount(
                    name=nome_conta.strip(),
                    bank=banco_c.strip() or None,
                    type=AccountType(tipo_c),
                    balance=saldo_ini,
                    color=cor_conta,
                ))
                st.toast(f"Conta '{nome_conta}' criada ✓", icon="🏦")
                st.rerun()
            except Exception as e:
                st.error(str(e))
