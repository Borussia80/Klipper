"""TDD — statement_reader: parser de extratos Itaú."""

from __future__ import annotations

from datetime import date

import pytest

from models.transaction import TransactionType


class TestParseItauLine:
    """_parse_line() com linhas reais do extrato Itaú."""

    def test_debit_pix_qrs(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("20/05/2026 PIX QRS VALDENYO CA20/05 -17,98")
        assert tx is not None
        assert tx.amount == pytest.approx(17.98)
        assert tx.tx_type == TransactionType.GASTO
        assert tx.date == date(2026, 5, 20)

    def test_debit_pix_transf(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("20/05/2026 PIX TRANSF LARA ES20/05 -60,00")
        assert tx is not None
        assert tx.amount == pytest.approx(60.0)
        assert tx.tx_type == TransactionType.GASTO

    def test_credit_pix_received(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("11/05/2026 PIX TRANSF ROBERTO11/05 5.000,00")
        assert tx is not None
        assert tx.amount == pytest.approx(5000.0)
        assert tx.tx_type == TransactionType.GANHO

    def test_credit_ted(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("15/05/2026 TED 237.0001.BRADESCO S 800,00")
        assert tx is not None
        assert tx.amount == pytest.approx(800.0)
        assert tx.tx_type == TransactionType.GANHO

    def test_credit_rend_pago(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("20/05/2026 REND PAGO APLIC AUT MAIS 0,02")
        assert tx is not None
        assert tx.amount == pytest.approx(0.02)
        assert tx.tx_type == TransactionType.GANHO

    def test_skip_saldo_do_dia(self):
        from core.statement_reader import _parse_line
        assert _parse_line("22/05/2026 SALDO DO DIA 1.508,59") is None

    def test_skip_periodo_visualizacao(self):
        from core.statement_reader import _parse_line
        assert _parse_line("período de visualização: 01/01/2026 até 30/06/2026") is None

    def test_skip_data_header(self):
        from core.statement_reader import _parse_line
        assert _parse_line("data lançamentos valor (R$) saldo (R$)") is None

    def test_debit_fatura_paga(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("11/05/2026 FATURA PAGA PERSONNALITE -5.413,78")
        assert tx is not None
        assert tx.amount == pytest.approx(5413.78)
        assert tx.tx_type == TransactionType.GASTO

    def test_debit_da_mei(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("20/05/2026 DA DAS MEI DMEI00263310 -86,05")
        assert tx is not None
        assert tx.amount == pytest.approx(86.05)
        assert tx.tx_type == TransactionType.GASTO

    def test_debit_seguro_cartao(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("06/05/2026 SEGURO CARTAO -25,00")
        assert tx is not None
        assert tx.amount == pytest.approx(25.0)
        assert tx.tx_type == TransactionType.GASTO

    def test_debit_pag_boleto(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("06/05/2026 PAG BOLETO SANTANDER FREE VISA - 2484 -1.096,06")
        assert tx is not None
        assert tx.amount == pytest.approx(1096.06)
        assert tx.tx_type == TransactionType.GASTO

    def test_credit_large_ted(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("28/04/2026 TED 001.1769.OT G N S 12.603,88")
        assert tx is not None
        assert tx.amount == pytest.approx(12603.88)
        assert tx.tx_type == TransactionType.GANHO

    def test_debit_int_pm(self):
        from core.statement_reader import _parse_line
        tx = _parse_line("08/05/2026 INT PM ARACAJ 000000 -148,30")
        assert tx is not None
        assert tx.amount == pytest.approx(148.30)
        assert tx.tx_type == TransactionType.GASTO


class TestParseAmountAndType:
    """_parse_amount_and_type() — lógica de sinal Itaú."""

    def test_negative_is_gasto(self):
        from core.statement_reader import _parse_amount_and_type
        amount, t = _parse_amount_and_type("-17,98", "qualquer linha")
        assert amount == pytest.approx(17.98)
        assert t == TransactionType.GASTO

    def test_large_negative_is_gasto(self):
        from core.statement_reader import _parse_amount_and_type
        amount, t = _parse_amount_and_type("-5.413,78", "FATURA PAGA -5.413,78")
        assert amount == pytest.approx(5413.78)
        assert t == TransactionType.GASTO

    def test_unsigned_positive_is_ganho(self):
        from core.statement_reader import _parse_amount_and_type
        amount, t = _parse_amount_and_type("5.000,00", "PIX TRANSF ROBERTO 5.000,00")
        assert amount == pytest.approx(5000.0)
        assert t == TransactionType.GANHO

    def test_small_positive_rend_is_ganho(self):
        from core.statement_reader import _parse_amount_and_type
        amount, t = _parse_amount_and_type("0,02", "REND PAGO APLIC AUT MAIS 0,02")
        assert amount == pytest.approx(0.02)
        assert t == TransactionType.GANHO


class TestParseTransactions:
    """_parse_transactions() — bloco real do extrato Itaú."""

    def test_itau_block_count_and_filter(self):
        from core.statement_reader import _parse_transactions
        text = (
            "22/05/2026 SALDO DO DIA 1.508,59\n"
            "20/05/2026 PIX QRS VALDENYO CA20/05 -17,98\n"
            "20/05/2026 PIX TRANSF LARA ES20/05 -60,00\n"
            "20/05/2026 REND PAGO APLIC AUT MAIS 0,02\n"
            "20/05/2026 DA DAS MEI DMEI00263310 -86,05\n"
            "20/05/2026 SALDO DO DIA 1.508,49\n"
            "15/05/2026 TED 237.0001.BRADESCO S 800,00\n"
        )
        txs = _parse_transactions(text)
        assert len(txs) == 5  # 2 SALDO DO DIA filtrados

    def test_itau_block_types(self):
        from core.statement_reader import _parse_transactions
        text = (
            "11/05/2026 PIX TRANSF ROBERTO11/05 5.000,00\n"
            "11/05/2026 FATURA PAGA PERSONNALITE -5.413,78\n"
        )
        txs = _parse_transactions(text)
        assert len(txs) == 2
        ganhos = [t for t in txs if t.tx_type == TransactionType.GANHO]
        gastos = [t for t in txs if t.tx_type == TransactionType.GASTO]
        assert len(ganhos) == 1
        assert len(gastos) == 1
        assert ganhos[0].amount == pytest.approx(5000.0)
        assert gastos[0].amount == pytest.approx(5413.78)
