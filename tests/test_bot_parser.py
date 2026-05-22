from __future__ import annotations

import pytest

from bot.parser import ParsedCapture, parse_message
from models.transaction import Category, TransactionType


class TestParseMessage:
    def test_gasto_simples(self):
        r = parse_message("gastei 50 no mercado")
        assert r is not None
        assert r.amount == pytest.approx(50.0)
        assert r.type == TransactionType.GASTO
        assert r.category == Category.ALIMENTACAO

    def test_gasto_com_centavos(self):
        r = parse_message("paguei 45,90 ifood")
        assert r is not None
        assert r.amount == pytest.approx(45.90)

    def test_gasto_valor_brl_com_ponto_milhar(self):
        r = parse_message("paguei R$ 1.500,00 aluguel")
        assert r is not None
        assert r.amount == pytest.approx(1500.0)
        assert r.category == Category.MORADIA

    def test_ganho_detectado(self):
        r = parse_message("recebi 5000 salario")
        assert r is not None
        assert r.type == TransactionType.GANHO
        assert r.category == Category.RENDA

    def test_sem_valor_retorna_none(self):
        assert parse_message("oi tudo bem?") is None

    def test_valor_zero_retorna_none(self):
        assert parse_message("gastei zero reais") is None

    def test_categoria_outros_quando_sem_keyword(self):
        r = parse_message("gastei 100 xpto")
        assert r is not None
        assert r.category == Category.OUTROS
        assert r.confidence < 0.80

    def test_confianca_alta_com_categoria(self):
        r = parse_message("uber 32")
        assert r is not None
        assert r.category == Category.TRANSPORTE
        assert r.confidence >= 0.85

    def test_saude_detectada(self):
        r = parse_message("paguei 250 fono")
        assert r is not None
        assert r.category == Category.SAUDE

    def test_freelance_detectado(self):
        r = parse_message("recebi 800 freela site")
        assert r is not None
        assert r.type == TransactionType.GANHO
        assert r.category == Category.FREELANCE

    def test_descricao_limpa(self):
        r = parse_message("gastei 50 no ifood lanche")
        assert r is not None
        assert "gastei" not in r.description.lower()
        assert "50" not in r.description


class TestStatementReader:
    def test_parse_line_com_data_valor_descricao(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("14/05/2026  PIX ENVIADO - JOAO SILVA    -150,00")
        assert tx is not None
        assert tx.amount == pytest.approx(150.0)
        assert tx.tx_type == TransactionType.GASTO

    def test_parse_line_credito(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("15/05/2026  TED RECEBIDA - EMPRESA SA   +5.000,00")
        assert tx is not None
        assert tx.amount == pytest.approx(5000.0)
        assert tx.tx_type == TransactionType.GANHO

    def test_parse_line_sem_data_retorna_none(self):
        from core.statement_reader import _parse_line
        assert _parse_line("sem data aqui") is None

    def test_parse_line_sem_valor_retorna_none(self):
        from core.statement_reader import _parse_line
        assert _parse_line("14/05/2026  texto sem valor monetário") is None

    def test_extract_date_formatos(self):
        from core.statement_reader import _extract_date
        assert _extract_date("14/05/2026 compra")  is not None
        assert _extract_date("14/05 compra")       is not None
        assert _extract_date("14 mai compra")       is not None
        assert _extract_date("sem data nenhuma")    is None

    def test_categorize_mercado(self):
        from core.statement_reader import _categorize
        assert _categorize("COMPRA SUPERMERCADO EXTRA") == Category.ALIMENTACAO

    def test_categorize_uber(self):
        from core.statement_reader import _categorize
        assert _categorize("UBER *TRIP 15MAI") == Category.TRANSPORTE

    def test_categorize_outros(self):
        from core.statement_reader import _categorize
        assert _categorize("XPTO LTDA 12345") == Category.OUTROS
