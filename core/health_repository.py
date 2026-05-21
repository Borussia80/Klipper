from __future__ import annotations

import logging
from datetime import date

from models.health import HealthProfessional, HealthSession, ReimbursementRequest, ReimbursementStatus

from .database import get_client

log = logging.getLogger(__name__)


class HealthProfessionalRepository:
    TABLE = "health_professionals"

    def create(self, prof: HealthProfessional) -> HealthProfessional:
        data = prof.model_dump()
        data["specialty"] = data["specialty"].value
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar profissional %s: %s", prof.id, e)
            raise
        return prof

    def list_active(self) -> list[HealthProfessional]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .eq("is_active", True)
                .order("name")
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar profissionais: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def deactivate(self, prof_id: str) -> None:
        try:
            get_client().table(self.TABLE).update({"is_active": False}).eq("id", prof_id).execute()
        except Exception as e:
            log.error("Erro ao desativar profissional %s: %s", prof_id, e)
            raise

    @staticmethod
    def _from_row(r: dict) -> HealthProfessional:
        return HealthProfessional(
            id=r["id"],
            name=r["name"],
            specialty=r["specialty"],
            council_number=r.get("council_number"),
            is_active=r.get("is_active", True),
        )


class HealthSessionRepository:
    TABLE = "health_sessions"

    def create(self, session: HealthSession) -> HealthSession:
        data = session.model_dump()
        data["session_date"] = data["session_date"].isoformat()
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar sessão %s: %s", session.id, e)
            raise
        return session

    def list_by_year(self, year: int) -> list[HealthSession]:
        start = date(year, 1, 1).isoformat()
        end   = date(year + 1, 1, 1).isoformat()
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .gte("session_date", start)
                .lt("session_date", end)
                .order("session_date", desc=True)
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar sessões do ano %d: %s", year, e)
            raise
        return [self._from_row(r) for r in res.data]

    def list_pending(self) -> list[HealthSession]:
        """Sessões sem solicitação de reembolso vinculada."""
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .is_("reimbursement_request_id", "null")
                .order("session_date", desc=True)
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar sessões pendentes: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def attach_to_request(self, session_ids: list[str], request_id: str) -> None:
        try:
            get_client().table(self.TABLE).update(
                {"reimbursement_request_id": request_id}
            ).in_("id", session_ids).execute()
        except Exception as e:
            log.error("Erro ao vincular sessões à solicitação %s: %s", request_id, e)
            raise

    @staticmethod
    def _from_row(r: dict) -> HealthSession:
        return HealthSession(
            id=r["id"],
            professional_id=r["professional_id"],
            session_date=date.fromisoformat(r["session_date"]),
            amount_paid=float(r["amount_paid"]),
            nf_number=r.get("nf_number"),
            notes=r.get("notes"),
            reimbursement_request_id=r.get("reimbursement_request_id"),
        )


class ReimbursementRequestRepository:
    TABLE = "reimbursement_requests"

    def create(self, req: ReimbursementRequest) -> ReimbursementRequest:
        data = req.model_dump()
        data["request_date"] = data["request_date"].isoformat()
        data["status"]       = data["status"].value
        try:
            get_client().table(self.TABLE).insert(data).execute()
        except Exception as e:
            log.error("Erro ao criar solicitação %s: %s", req.id, e)
            raise
        return req

    def list_all(self) -> list[ReimbursementRequest]:
        try:
            res = (
                get_client()
                .table(self.TABLE)
                .select("*")
                .order("request_date", desc=True)
                .execute()
            )
        except Exception as e:
            log.error("Erro ao listar solicitações: %s", e)
            raise
        return [self._from_row(r) for r in res.data]

    def update_status(
        self,
        req_id: str,
        status: ReimbursementStatus,
        protocol_number: str | None = None,
        amount_received: float | None = None,
        notes: str | None = None,
    ) -> None:
        patch: dict = {"status": status.value}
        if protocol_number is not None:
            patch["protocol_number"] = protocol_number
        if amount_received is not None:
            patch["amount_received"] = amount_received
        if notes is not None:
            patch["notes"] = notes
        try:
            get_client().table(self.TABLE).update(patch).eq("id", req_id).execute()
        except Exception as e:
            log.error("Erro ao atualizar solicitação %s: %s", req_id, e)
            raise

    @staticmethod
    def _from_row(r: dict) -> ReimbursementRequest:
        return ReimbursementRequest(
            id=r["id"],
            professional_id=r["professional_id"],
            request_date=date.fromisoformat(r["request_date"]),
            protocol_number=r.get("protocol_number"),
            amount_requested=float(r["amount_requested"]),
            amount_received=float(r["amount_received"]) if r.get("amount_received") is not None else None,
            status=ReimbursementStatus(r["status"]),
            notes=r.get("notes"),
        )
