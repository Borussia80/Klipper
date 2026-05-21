from __future__ import annotations

import pytest
from datetime import date

from models.installment import Installment
from models.transaction import TransactionStatus, TransactionType
from core.installment_engine import gerar_parcelas, calcular_comprometimento_mensal


def _inst(n_total: int = 12, n_paid: int = 0, start: date | None = None,
          valor: float = 1200.0, card_id: str | None = None) -> Installment:
    return Installment(
        description="Notebook",
        total_amount=valor,
        n_total=n_total,
        n_paid=n_paid,
        start_date=start or date.today(),
        card_id=card_id,
    )


class TestGerarParcelas:
    def test_quantidade_correta(self):
        inst = _inst(n_total=6)
        parcelas = gerar_parcelas(inst)
        assert len(parcelas) == 6

    def test_valores_corretos(self):
        inst = _inst(n_total=3, valor=300.0)
        parcelas = gerar_parcelas(inst)
        for p in parcelas:
            assert p.amount == pytest.approx(100.0)

    def test_parcelas_passadas_sao_pagas(self):
        start = date(2025, 1, 1)
        inst = _inst(n_total=4, start=start)
        parcelas = gerar_parcelas(inst)
        # All dates in 2025 are in the past as of 2026
        pagas = [p for p in parcelas if p.status == TransactionStatus.PAGO]
        assert len(pagas) == 4

    def test_parcelas_futuras_sao_pendentes(self):
        from dateutil.relativedelta import relativedelta
        start = date.today() + relativedelta(months=1)
        inst = _inst(n_total=3, start=start)
        parcelas = gerar_parcelas(inst)
        pendentes = [p for p in parcelas if p.status == TransactionStatus.PENDENTE]
        assert len(pendentes) == 3

    def test_datas_incrementadas_mensalmente(self):
        from dateutil.relativedelta import relativedelta
        start = date(2026, 1, 1)
        inst = _inst(n_total=3, start=start)
        parcelas = gerar_parcelas(inst)
        assert parcelas[0].date == date(2026, 1, 1)
        assert parcelas[1].date == date(2026, 2, 1)
        assert parcelas[2].date == date(2026, 3, 1)

    def test_installment_id_preenchido(self):
        inst = _inst()
        parcelas = gerar_parcelas(inst)
        assert all(p.installment_id == inst.id for p in parcelas)

    def test_card_id_preenchido_quando_informado(self):
        inst = _inst(card_id="card-uuid-123")
        parcelas = gerar_parcelas(inst)
        assert all(p.card_id == "card-uuid-123" for p in parcelas)

    def test_tipo_sempre_gasto(self):
        inst = _inst()
        parcelas = gerar_parcelas(inst)
        assert all(p.type == TransactionType.GASTO for p in parcelas)

    def test_notas_incluem_numero_da_parcela(self):
        inst = _inst(n_total=5)
        parcelas = gerar_parcelas(inst)
        assert "1/5" in parcelas[0].notes
        assert "5/5" in parcelas[4].notes


class TestCalcularComprometimentoMensal:
    def test_retorna_dict_vazio_sem_installments(self):
        result = calcular_comprometimento_mensal([])
        assert result == {}

    def test_comprometimento_mensal_correto(self):
        from dateutil.relativedelta import relativedelta
        start = date.today()
        inst = Installment(
            description="Test", total_amount=600.0, n_total=3,
            start_date=start,
        )
        result = calcular_comprometimento_mensal([inst])
        assert len(result) == 3
        for v in result.values():
            assert v == pytest.approx(200.0)

    def test_installment_inativo_ignorado(self):
        inst = Installment(
            description="Inativo", total_amount=600.0, n_total=3,
            start_date=date.today(), is_active=False,
        )
        result = calcular_comprometimento_mensal([inst])
        assert result == {}

    def test_chaves_ordenadas_por_data(self):
        from dateutil.relativedelta import relativedelta
        start = date.today()
        inst = _inst(n_total=3, start=start)
        result = calcular_comprometimento_mensal([inst])
        chaves = list(result.keys())
        assert chaves == sorted(chaves)

    def test_parcelas_passadas_excluidas(self):
        start = date(2025, 1, 1)  # all in the past
        inst = _inst(n_total=3, start=start)
        result = calcular_comprometimento_mensal([inst])
        # All dates in 2025 are past (today is 2026-05)
        assert result == {}
