"""TDD — parser de prints do BTG Pactual (screenshots do app mobile)."""

from __future__ import annotations

from datetime import date

import pytest

from models.transaction import TransactionType


class TestParseBtgDateLine:
    """_parse_btg_date_line() — extrai data de cabeçalhos de data do BTG."""

    def test_weekday_long_date(self):
        from core.statement_reader import _parse_btg_date_line
        d = _parse_btg_date_line("quarta-feira 20/mai")
        assert d == date(2026, 5, 20)

    def test_weekday_short_date(self):
        from core.statement_reader import _parse_btg_date_line
        d = _parse_btg_date_line("15/mai")
        assert d == date(2026, 5, 15)

    def test_short_date_eleven(self):
        from core.statement_reader import _parse_btg_date_line
        d = _parse_btg_date_line("11/mai")
        assert d == date(2026, 5, 11)

    def test_description_line_returns_none(self):
        from core.statement_reader import _parse_btg_date_line
        assert _parse_btg_date_line("Rendimentos - CPTS11") is None

    def test_amount_line_returns_none(self):
        from core.statement_reader import _parse_btg_date_line
        assert _parse_btg_date_line("+ R$ 14,40") is None

    def test_header_line_returns_none(self):
        from core.statement_reader import _parse_btg_date_line
        assert _parse_btg_date_line("Atividade") is None

    def test_all_months_parsed(self):
        from core.statement_reader import _parse_btg_date_line
        cases = [
            ("01/jan", date(2026, 1, 1)),
            ("15/fev", date(2026, 2, 15)),
            ("20/mar", date(2026, 3, 20)),
            ("30/abr", date(2026, 4, 30)),
            ("01/jun", date(2026, 6, 1)),
            ("15/jul", date(2026, 7, 15)),
            ("20/ago", date(2026, 8, 20)),
            ("01/set", date(2026, 9, 1)),
            ("15/out", date(2026, 10, 15)),
            ("20/nov", date(2026, 11, 20)),
            ("31/dez", date(2026, 12, 31)),
        ]
        for line, expected in cases:
            assert _parse_btg_date_line(line) == expected, f"falhou para: {line}"


class TestParseBtgAmountLine:
    """_parse_btg_amount_line() — extrai valor e tipo de linhas de valor do BTG."""

    def test_credit_with_plus(self):
        from core.statement_reader import _parse_btg_amount_line
        result = _parse_btg_amount_line("+ R$ 14,40")
        assert result is not None
        amount, tx_type = result
        assert amount == pytest.approx(14.40)
        assert tx_type == TransactionType.GANHO

    def test_debit_with_minus(self):
        from core.statement_reader import _parse_btg_amount_line
        result = _parse_btg_amount_line("- R$ 50,00")
        assert result is not None
        amount, tx_type = result
        assert amount == pytest.approx(50.0)
        assert tx_type == TransactionType.GASTO

    def test_unsigned_is_credit(self):
        from core.statement_reader import _parse_btg_amount_line
        result = _parse_btg_amount_line("R$ 318,62")
        assert result is not None
        amount, tx_type = result
        assert amount == pytest.approx(318.62)
        assert tx_type == TransactionType.GANHO

    def test_large_amount_with_thousand_separator(self):
        from core.statement_reader import _parse_btg_amount_line
        result = _parse_btg_amount_line("R$ 1.234,56")
        assert result is not None
        amount, _ = result
        assert amount == pytest.approx(1234.56)

    def test_description_line_returns_none(self):
        from core.statement_reader import _parse_btg_amount_line
        assert _parse_btg_amount_line("Rendimentos - CPTS11") is None

    def test_date_line_returns_none(self):
        from core.statement_reader import _parse_btg_amount_line
        assert _parse_btg_amount_line("quarta-feira 20/mai") is None

    def test_plus_with_space_variants(self):
        from core.statement_reader import _parse_btg_amount_line
        result = _parse_btg_amount_line("+R$6,60")
        assert result is not None
        assert result[0] == pytest.approx(6.60)
        assert result[1] == TransactionType.GANHO


class TestParseBtgStatement:
    """parse_btg_statement() — bloco real do print do BTG."""

    def test_parses_three_fii_rendimentos(self):
        from core.statement_reader import parse_btg_statement
        text = (
            "quarta-feira 20/mai\n"
            "Rendimentos - À Vista S/ Fii Capi Secci Er - CPTS11\n"
            "+ R$ 14,40\n"
            "Conta corrente\n"
            "15/mai\n"
            "Rendimentos - À Vista S/ Fii Cshg Logci - HGLG11\n"
            "+ R$ 6,60\n"
            "Conta corrente\n"
            "Rendimentos - À Vista S/ Fii Xp Log Ci - XPLG11\n"
            "+ R$ 5,74\n"
            "Conta corrente\n"
        )
        txs = parse_btg_statement(text)
        assert len(txs) == 3
        assert txs[0].date == date(2026, 5, 20)
        assert txs[0].amount == pytest.approx(14.40)
        assert txs[0].tx_type == TransactionType.GANHO
        assert txs[1].date == date(2026, 5, 15)
        assert txs[1].amount == pytest.approx(6.60)
        assert txs[2].date == date(2026, 5, 15)
        assert txs[2].amount == pytest.approx(5.74)

    def test_pix_credit_is_ganho(self):
        from core.statement_reader import parse_btg_statement
        text = (
            "11/mai\n"
            "Transferência A Crédito Via Pix - Roberto Wagner\n"
            "R$ 318,62\n"
            "Conta corrente\n"
        )
        txs = parse_btg_statement(text)
        assert len(txs) == 1
        assert txs[0].amount == pytest.approx(318.62)
        assert txs[0].tx_type == TransactionType.GANHO
        assert txs[0].date == date(2026, 5, 11)

    def test_skips_header_lines(self):
        from core.statement_reader import parse_btg_statement
        text = (
            "Atividade\n"
            "Lançamentos Futuros\n"
            "0 operações agendadas\n"
            "20/mai\n"
            "Rendimentos - CPTS11\n"
            "+ R$ 14,40\n"
            "Conta corrente\n"
        )
        txs = parse_btg_statement(text)
        assert len(txs) == 1
        assert txs[0].amount == pytest.approx(14.40)

    def test_empty_text_returns_empty(self):
        from core.statement_reader import parse_btg_statement
        assert parse_btg_statement("") == []
        assert parse_btg_statement("Atividade\nLançamentos Futuros\n") == []

    def test_rendimento_categorized_as_renda(self):
        from core.statement_reader import parse_btg_statement
        from models.transaction import Category
        text = (
            "20/mai\n"
            "Rendimentos - CPTS11\n"
            "+ R$ 14,40\n"
        )
        txs = parse_btg_statement(text)
        assert txs[0].category == Category.RENDA

    def test_mixed_debits_and_credits(self):
        from core.statement_reader import parse_btg_statement
        text = (
            "20/mai\n"
            "Rendimentos - HGLG11\n"
            "+ R$ 10,00\n"
            "Conta corrente\n"
            "TED Enviada - Banco XYZ\n"
            "- R$ 500,00\n"
            "Conta corrente\n"
        )
        txs = parse_btg_statement(text)
        assert len(txs) == 2
        ganhos = [t for t in txs if t.tx_type == TransactionType.GANHO]
        gastos = [t for t in txs if t.tx_type == TransactionType.GASTO]
        assert len(ganhos) == 1
        assert len(gastos) == 1
        assert ganhos[0].amount == pytest.approx(10.0)
        assert gastos[0].amount == pytest.approx(500.0)


class TestIsBtgFormat:
    """_is_btg_format() — detecta formato BTG vs outros bancos."""

    def test_btg_text_detected(self):
        from core.statement_reader import _is_btg_format
        assert _is_btg_format("Atividade\nLançamentos Futuros\n")

    def test_conta_corrente_detected(self):
        from core.statement_reader import _is_btg_format
        assert _is_btg_format("+ R$ 14,40\nConta corrente\n")

    def test_itau_text_not_btg(self):
        from core.statement_reader import _is_btg_format
        assert not _is_btg_format("20/05/2026 PIX QRS VALDENYO -17,98")
