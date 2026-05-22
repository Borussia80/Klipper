"""TDD: categories_for_type() — separação de categorias por tipo de transação."""
from __future__ import annotations

import pytest
from models.transaction import Category, TransactionType, categories_for_type


class TestCategoriesForType:
    def test_ganho_inclui_renda(self):
        assert Category.RENDA in categories_for_type(TransactionType.GANHO)

    def test_ganho_inclui_freelance(self):
        assert Category.FREELANCE in categories_for_type(TransactionType.GANHO)

    def test_ganho_inclui_outros(self):
        assert Category.OUTROS in categories_for_type(TransactionType.GANHO)

    def test_ganho_exclui_moradia(self):
        assert Category.MORADIA not in categories_for_type(TransactionType.GANHO)

    def test_ganho_exclui_alimentacao(self):
        assert Category.ALIMENTACAO not in categories_for_type(TransactionType.GANHO)

    def test_ganho_exclui_lazer(self):
        assert Category.LAZER not in categories_for_type(TransactionType.GANHO)

    def test_ganho_exclui_investimento(self):
        assert Category.INVESTIMENTO not in categories_for_type(TransactionType.GANHO)

    def test_gasto_inclui_moradia(self):
        assert Category.MORADIA in categories_for_type(TransactionType.GASTO)

    def test_gasto_inclui_alimentacao(self):
        assert Category.ALIMENTACAO in categories_for_type(TransactionType.GASTO)

    def test_gasto_inclui_lazer(self):
        assert Category.LAZER in categories_for_type(TransactionType.GASTO)

    def test_gasto_inclui_investimento(self):
        assert Category.INVESTIMENTO in categories_for_type(TransactionType.GASTO)

    def test_gasto_inclui_outros(self):
        assert Category.OUTROS in categories_for_type(TransactionType.GASTO)

    def test_gasto_exclui_renda(self):
        assert Category.RENDA not in categories_for_type(TransactionType.GASTO)

    def test_gasto_exclui_freelance(self):
        assert Category.FREELANCE not in categories_for_type(TransactionType.GASTO)

    def test_retorna_lista_nao_vazia_ganho(self):
        assert len(categories_for_type(TransactionType.GANHO)) > 0

    def test_retorna_lista_nao_vazia_gasto(self):
        assert len(categories_for_type(TransactionType.GASTO)) > 0

    def test_retorna_lista_ganho(self):
        assert isinstance(categories_for_type(TransactionType.GANHO), list)

    def test_retorna_lista_gasto(self):
        assert isinstance(categories_for_type(TransactionType.GASTO), list)
