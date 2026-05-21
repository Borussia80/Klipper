from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.investment import Investment

MAX_ATIVO_PCT = 10.0    # máx por ativo (%)
MAX_TESE_PCT = 25.0     # máx por tese/setor (%)
CAIXA_MIN_PCT = 20.0    # caixa mínimo do portfólio (%)


@dataclass
class GovernanceAlert:
    code: str
    message: str
    is_hard_fail: bool = False


def verificar_limites(
    portfolio: list[Investment],
    caixa_disponivel: float,
    novo_ativo: Investment | None = None,
) -> list[GovernanceAlert]:
    """Verifica limites M2. Retorna lista de alertas, incluindo hard fails."""
    alertas: list[GovernanceAlert] = []

    ativos = list(portfolio)
    if novo_ativo:
        ativos.append(novo_ativo)

    total = sum(inv.current_value for inv in ativos) + caixa_disponivel
    if total == 0:
        return alertas

    # Caixa mínimo
    caixa_pct = (caixa_disponivel / total) * 100
    if caixa_pct < CAIXA_MIN_PCT:
        alertas.append(
            GovernanceAlert(
                code="M2_CAIXA",
                message=f"Caixa {caixa_pct:.1f}% < mínimo {CAIXA_MIN_PCT}%. Reforçar caixa antes de comprar.",
                is_hard_fail=True,
            )
        )

    # Max por ativo
    for inv in portfolio:
        ativo_pct = (inv.current_value / total) * 100
        if ativo_pct > MAX_ATIVO_PCT:
            alertas.append(
                GovernanceAlert(
                    code="M2_CONCENTRACAO_ATIVO",
                    message=f"{inv.ticker}: {ativo_pct:.1f}% > máx {MAX_ATIVO_PCT}% por ativo.",
                    is_hard_fail=True,
                )
            )

    # Max por setor/tese
    por_setor: dict[str, float] = {}
    for inv in ativos:
        if inv.sector:
            por_setor[inv.sector] = por_setor.get(inv.sector, 0) + inv.current_value

    for setor, valor in por_setor.items():
        setor_pct = (valor / total) * 100
        if setor_pct > MAX_TESE_PCT:
            alertas.append(
                GovernanceAlert(
                    code="M2_CONCENTRACAO_TESE",
                    message=f"Setor '{setor}': {setor_pct:.1f}% > máx {MAX_TESE_PCT}% por tese.",
                    is_hard_fail=True,
                )
            )

    return alertas


def hard_fail(alertas: list[GovernanceAlert]) -> tuple[bool, str]:
    """Retorna (True, motivo) se houver qualquer hard fail."""
    fails = [a for a in alertas if a.is_hard_fail]
    if not fails:
        return False, ""
    motivos = "; ".join(a.message for a in fails)
    return True, motivos
