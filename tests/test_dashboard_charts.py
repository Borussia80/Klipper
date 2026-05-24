"""Sprint 1 — Dashboard charts: testes TDD para funções de preparação de dados."""

from __future__ import annotations

from decimal import Decimal
from datetime import date

import pytest

from core.analytics import preparar_dados_donut_categorias, preparar_dados_barras_mensais
from models.transaction import Category, PaymentMethod, Transaction, TransactionType


def _tx(
    tipo: TransactionType,
    categoria: Category,
    valor: float,
    d: date = date(2030, 1, 15),
) -> Transaction:
    return Transaction(
        date=d,
        amount=Decimal(str(valor)),
        type=tipo,
        category=categoria,
        payment_method=PaymentMethod.PIX,
    )


# ── preparar_dados_donut_categorias ───────────────────────────────────────────

class TestPrepararDadosDonutCategorias:
    def test_lista_vazia_retorna_vazio(self):
        assert preparar_dados_donut_categorias([]) == []

    def test_somente_gastos_incluidos(self):
        txs = [
            _tx(TransactionType.GANHO, Category.RENDA, 1000),
            _tx(TransactionType.GASTO, Category.ALIMENTACAO, 200),
        ]
        resultado = preparar_dados_donut_categorias(txs)
        assert len(resultado) == 1
        assert resultado[0]["categoria"] == "Alimentação"

    def test_exclui_categoria_investimento(self):
        txs = [
            _tx(TransactionType.GASTO, Category.INVESTIMENTO, 500),
            _tx(TransactionType.GASTO, Category.LAZER, 100),
        ]
        resultado = preparar_dados_donut_categorias(txs)
        cats = [r["categoria"] for r in resultado]
        assert "Investimento" not in cats
        assert "Lazer" in cats

    def test_agrega_multiplas_transacoes_mesma_categoria(self):
        txs = [
            _tx(TransactionType.GASTO, Category.ALIMENTACAO, 100),
            _tx(TransactionType.GASTO, Category.ALIMENTACAO, 50),
            _tx(TransactionType.GASTO, Category.LAZER, 200),
        ]
        resultado = preparar_dados_donut_categorias(txs)
        alim = next(r for r in resultado if r["categoria"] == "Alimentação")
        assert alim["total"] == pytest.approx(150.0)

    def test_ordena_por_total_decrescente(self):
        txs = [
            _tx(TransactionType.GASTO, Category.LAZER, 50),
            _tx(TransactionType.GASTO, Category.ALIMENTACAO, 300),
            _tx(TransactionType.GASTO, Category.TRANSPORTE, 100),
        ]
        resultado = preparar_dados_donut_categorias(txs)
        totais = [r["total"] for r in resultado]
        assert totais == sorted(totais, reverse=True)

    def test_total_e_float(self):
        txs = [_tx(TransactionType.GASTO, Category.LAZER, 99.99)]
        resultado = preparar_dados_donut_categorias(txs)
        assert isinstance(resultado[0]["total"], float)

    def test_resultado_contem_chaves_categoria_e_total(self):
        txs = [_tx(TransactionType.GASTO, Category.SAUDE, 150)]
        resultado = preparar_dados_donut_categorias(txs)
        assert "categoria" in resultado[0]
        assert "total" in resultado[0]

    def test_max_8_categorias(self):
        cats_distintas = [
            Category.ALIMENTACAO, Category.TRANSPORTE, Category.SAUDE,
            Category.LAZER, Category.MORADIA, Category.EDUCACAO,
            Category.FREELANCE, Category.OUTROS, Category.RENDA,
        ]
        txs = [_tx(TransactionType.GASTO, c, 10 + i * 5) for i, c in enumerate(cats_distintas)]
        resultado = preparar_dados_donut_categorias(txs)
        assert len(resultado) <= 8

    def test_apenas_ganhos_retorna_vazio(self):
        txs = [
            _tx(TransactionType.GANHO, Category.RENDA, 5000),
            _tx(TransactionType.GANHO, Category.FREELANCE, 1000),
        ]
        assert preparar_dados_donut_categorias(txs) == []


# ── preparar_dados_barras_mensais ─────────────────────────────────────────────

class TestPrepararDadosBarrasMensais:
    def test_lista_vazia_retorna_vazio(self):
        assert preparar_dados_barras_mensais([]) == []

    def test_retorna_um_registro_por_entrada(self):
        registros = [
            (2030, 1, Decimal("1000"), Decimal("600")),
            (2030, 2, Decimal("1100"), Decimal("700")),
            (2030, 3, Decimal("900"), Decimal("500")),
        ]
        assert len(preparar_dados_barras_mensais(registros)) == 3

    def test_label_mes_janeiro(self):
        registros = [(2030, 1, Decimal("1000"), Decimal("600"))]
        resultado = preparar_dados_barras_mensais(registros)
        assert resultado[0]["mes"] == "Jan/30"

    def test_label_mes_dezembro(self):
        registros = [(2029, 12, Decimal("5000"), Decimal("3000"))]
        resultado = preparar_dados_barras_mensais(registros)
        assert resultado[0]["mes"] == "Dez/29"

    def test_label_todos_os_meses(self):
        esperados = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                     "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        for i, abrev in enumerate(esperados, start=1):
            registros = [(2030, i, Decimal("0"), Decimal("0"))]
            resultado = preparar_dados_barras_mensais(registros)
            assert resultado[0]["mes"].startswith(abrev), f"Mês {i} deve começar com {abrev}"

    def test_valores_convertidos_para_float(self):
        registros = [(2030, 5, Decimal("2500.50"), Decimal("1800.75"))]
        resultado = preparar_dados_barras_mensais(registros)
        assert isinstance(resultado[0]["Entradas"], float)
        assert isinstance(resultado[0]["Saídas"], float)
        assert resultado[0]["Entradas"] == pytest.approx(2500.50)
        assert resultado[0]["Saídas"] == pytest.approx(1800.75)

    def test_ordena_cronologicamente(self):
        registros = [
            (2030, 3, Decimal("900"), Decimal("500")),
            (2030, 1, Decimal("1000"), Decimal("600")),
            (2030, 2, Decimal("1100"), Decimal("700")),
        ]
        resultado = preparar_dados_barras_mensais(registros)
        assert resultado[0]["mes"] == "Jan/30"
        assert resultado[1]["mes"] == "Fev/30"
        assert resultado[2]["mes"] == "Mar/30"

    def test_ordena_atravessando_virada_de_ano(self):
        registros = [
            (2030, 1, Decimal("1000"), Decimal("600")),
            (2029, 12, Decimal("2000"), Decimal("1500")),
            (2029, 11, Decimal("1800"), Decimal("1200")),
        ]
        resultado = preparar_dados_barras_mensais(registros)
        assert resultado[0]["mes"] == "Nov/29"
        assert resultado[1]["mes"] == "Dez/29"
        assert resultado[2]["mes"] == "Jan/30"

    def test_resultado_contem_chaves_obrigatorias(self):
        registros = [(2030, 6, Decimal("3000"), Decimal("2000"))]
        resultado = preparar_dados_barras_mensais(registros)
        assert "mes" in resultado[0]
        assert "Entradas" in resultado[0]
        assert "Saídas" in resultado[0]
