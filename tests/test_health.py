from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from models.health import (
    HealthProfessional,
    HealthSession,
    ReimbursementRequest,
    ReimbursementStatus,
    Specialty,
)


class TestHealthProfessional:
    def test_criacao_valida(self):
        p = HealthProfessional(name="Dra. Ana", specialty=Specialty.FONOAUDIOLOGIA)
        assert p.name == "Dra. Ana"
        assert p.specialty == Specialty.FONOAUDIOLOGIA
        assert p.is_active is True
        assert p.council_number is None

    def test_com_numero_conselho(self):
        p = HealthProfessional(
            name="Dr. Carlos", specialty=Specialty.PSICOLOGIA, council_number="CRP 06/12345"
        )
        assert p.council_number == "CRP 06/12345"

    def test_id_gerado_automaticamente(self):
        p1 = HealthProfessional(name="P1", specialty=Specialty.NEUROLOGIA)
        p2 = HealthProfessional(name="P2", specialty=Specialty.NEUROLOGIA)
        assert p1.id != p2.id


class TestHealthSession:
    def test_criacao_valida(self):
        s = HealthSession(
            professional_id="prof-001",
            session_date=date(2026, 5, 10),
            amount_paid=250.0,
        )
        assert s.amount_paid == 250.0
        assert s.is_pending is True
        assert s.reimbursement_request_id is None

    def test_sessao_vinculada_nao_e_pendente(self):
        s = HealthSession(
            professional_id="prof-001",
            session_date=date(2026, 5, 10),
            amount_paid=150.0,
            reimbursement_request_id="req-001",
        )
        assert s.is_pending is False

    def test_valor_zero_levanta_value_error(self):
        with pytest.raises(ValueError, match="positivo"):
            HealthSession(
                professional_id="prof-001",
                session_date=date(2026, 5, 10),
                amount_paid=0.0,
            )

    def test_valor_negativo_levanta_value_error(self):
        with pytest.raises(ValueError):
            HealthSession(
                professional_id="prof-001",
                session_date=date(2026, 5, 10),
                amount_paid=-100.0,
            )

    def test_campos_opcionais_none_por_padrao(self):
        s = HealthSession(
            professional_id="prof-001",
            session_date=date(2026, 5, 10),
            amount_paid=100.0,
        )
        assert s.nf_number is None
        assert s.notes is None


class TestReimbursementRequest:
    def _req(self, **kwargs) -> ReimbursementRequest:
        defaults = dict(
            professional_id="prof-001",
            request_date=date(2026, 5, 20),
            amount_requested=500.0,
        )
        return ReimbursementRequest(**{**defaults, **kwargs})

    def test_gap_pendente_e_valor_total(self):
        req = self._req(status=ReimbursementStatus.PENDENTE)
        assert req.gap == Decimal("500")

    def test_gap_parcial_e_diferenca(self):
        req = self._req(
            status=ReimbursementStatus.PARCIAL,
            amount_received=350.0,
        )
        assert req.gap == Decimal("150")

    def test_gap_reembolsado_e_zero(self):
        req = self._req(
            status=ReimbursementStatus.REEMBOLSADO,
            amount_received=500.0,
        )
        assert req.gap == Decimal("0")

    def test_gap_negado_e_valor_total(self):
        req = self._req(status=ReimbursementStatus.NEGADO)
        assert req.gap == Decimal("500")

    def test_status_padrao_e_pendente(self):
        req = self._req()
        assert req.status == ReimbursementStatus.PENDENTE

    def test_amount_requested_zero_levanta_value_error(self):
        with pytest.raises(ValueError, match="positivo"):
            self._req(amount_requested=0.0)

    def test_amount_requested_negativo_levanta_value_error(self):
        with pytest.raises(ValueError):
            self._req(amount_requested=-100.0)

    def test_gap_arredondamento_centavos(self):
        req = self._req(
            amount_requested=100.0,
            amount_received=33.33,
            status=ReimbursementStatus.PARCIAL,
        )
        assert req.gap == Decimal("66.67")
