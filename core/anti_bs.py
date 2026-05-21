from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.investment import Investment

DY_EXCESSIVO_THRESHOLD = 14.0     # DY acima disso exige investigação
LIQUIDEZ_MINIMA = 100_000.0       # R$100K diário mínimo
CONCENTRACAO_ALERTA = 8.0         # % do portfólio (aviso antes do hard fail M2)

PERGUNTA_OBRIGATORIA = "O mercado está barato ou precificando um problema real?"


@dataclass
class AntiBS_Alert:
    code: str
    message: str
    severity: str  # "WARNING" | "CRITICAL"


def verificar_alertas(inv: Investment, peso_portfolio_pct: float = 0.0) -> list[AntiBS_Alert]:
    """
    Verifica armadilhas Anti-BS para um ativo.
    peso_portfolio_pct: % que o ativo representa no portfólio total.
    """
    alertas: list[AntiBS_Alert] = []

    if inv.dy_12m > DY_EXCESSIVO_THRESHOLD:
        alertas.append(
            AntiBS_Alert(
                code="ABS_DY_EXCESSIVO",
                message=f"DY {inv.dy_12m:.1f}% acima de {DY_EXCESSIVO_THRESHOLD}%. "
                        "Valide sustentabilidade: distribuições podem ser retorno de capital.",
                severity="CRITICAL",
            )
        )

    if inv.pvp < 0.5 and inv.dy_12m < 6.0:
        alertas.append(
            AntiBS_Alert(
                code="ABS_DESCONTO_SEM_QUALIDADE",
                message=f"P/VP {inv.pvp:.2f} com DY baixo ({inv.dy_12m:.1f}%). "
                        "Desconto pode refletir problema estrutural, não oportunidade.",
                severity="CRITICAL",
            )
        )

    if inv.liquidity_daily < LIQUIDEZ_MINIMA:
        alertas.append(
            AntiBS_Alert(
                code="ABS_BAIXA_LIQUIDEZ",
                message=f"Liquidez diária R${inv.liquidity_daily:,.0f} < mínimo R${LIQUIDEZ_MINIMA:,.0f}. "
                        "Saída pode ser difícil em stress.",
                severity="WARNING",
            )
        )

    if peso_portfolio_pct >= CONCENTRACAO_ALERTA:
        alertas.append(
            AntiBS_Alert(
                code="ABS_CONCENTRACAO",
                message=f"Ativo representa {peso_portfolio_pct:.1f}% do portfólio. "
                        f"Próximo do limite M2 ({CONCENTRACAO_ALERTA}% alerta / 10% hard fail).",
                severity="WARNING",
            )
        )

    return alertas
