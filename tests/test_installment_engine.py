from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

from models.installment import Installment
from models.transaction import TransactionStatus, TransactionType
from core.installment_engine import gerar_parcelas, calcular_comprometimento_mensal

# Datas fixas: nunca dependem do dia em que o teste roda.
_PAST_START   = date(2025, 1, 1)   # passado — todas as parcelas serão PAGO
_FIXED_START  = date(2026, 1, 1)   # início de 2026 — parcelas já vencidas em relação a 2026-05
_FUTURE_START = date(2030, 1, 1)   # 2030 — todas as parcelas no futuro


def _inst(
    n_total: int = 12,
    n_paid: int = 0,
    start: date = _FUTURE_START,
    valor: float = 1200.0,
    card_id: str | None = None,
) -> Installment:
    return Installment(
        description="Notebook",
        total_amount=valor,
        n_total=n_total,
        n_paid=n_paid,
        start_date=start,
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
            assert p.amount == Decimal("100")

    def test_centavos_sao_preservados_no_total_contratado(self):
        inst = _inst(n_total=3, valor=100.0)
        parcelas = gerar_parcelas(inst)
        assert [p.amount for p in parcelas] == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]
        assert sum((p.amount for p in parcelas), Decimal(0)) == Decimal("100")

    def test_parcelas_passadas_sao_pagas(self):
        inst = _inst(n_total=4, start=_PAST_START)
        parcelas = gerar_parcelas(inst)
        pagas = [p for p in parcelas if p.status == TransactionStatus.PAGO]
        assert len(pagas) == 4   # jan–abr 2025, todos no passado em 2026

    def test_parcelas_futuras_sao_pendentes(self):
        inst = _inst(n_total=3, start=_FUTURE_START)
        parcelas = gerar_parcelas(inst)
        pendentes = [p for p in parcelas if p.status == TransactionStatus.PENDENTE]
        assert len(pendentes) == 3

    def test_datas_incrementadas_mensalmente(self):
        inst = _inst(n_total=3, start=_FIXED_START)
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
        inst = Installment(
            description="Test", total_amount=600.0, n_total=3,
            start_date=_FUTURE_START,
        )
        result = calcular_comprometimento_mensal([inst])
        assert len(result) == 3
        for v in result.values():
            assert v == Decimal("200")

    def test_installment_inativo_ignorado(self):
        inst = Installment(
            description="Inativo", total_amount=600.0, n_total=3,
            start_date=_FUTURE_START, is_active=False,
        )
        result = calcular_comprometimento_mensal([inst])
        assert result == {}

    def test_chaves_ordenadas_por_data(self):
        inst = _inst(n_total=3, start=_FUTURE_START)
        result = calcular_comprometimento_mensal([inst])
        chaves = list(result.keys())
        assert chaves == sorted(chaves)

    def test_parcelas_passadas_excluidas(self):
        inst = _inst(n_total=3, start=_PAST_START)
        result = calcular_comprometimento_mensal([inst])
        assert result == {}   # jan–mar 2025 são passado em 2026-05

    def test_comprometimento_preserva_centavos_por_mes(self):
        inst = _inst(n_total=3, start=_FUTURE_START, valor=100.0)
        result = calcular_comprometimento_mensal([inst])
        assert list(result.values()) == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]

    def test_comprometimento_mensal_soma_correta(self):
        """Todos os 12 meses de 2030 são futuros — comprometimento uniforme."""
        inst = Installment(
            description="Teste fixo",
            total_amount=1200.0,
            n_total=12,
            start_date=_FUTURE_START,
        )
        comp = calcular_comprometimento_mensal([inst])
        assert len(comp) == 12
        for v in comp.values():
            assert v == Decimal("100")
