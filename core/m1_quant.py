from __future__ import annotations

from enum import Enum
from typing import Literal


class Decisao(str, Enum):
    COMPRAR = "COMPRAR"
    MANTER = "MANTER"
    REDUZIR = "REDUZIR"


def calcular_score_m1(
    dy: float,
    pvp: float,
    liquidez: float,
    volatilidade: float,
    spread_cdi: float,
) -> float:
    """
    Calcula score M1 normalizado entre 0 e 1.

    Pesos calibrados para FIIs conservadores:
    - DY (30%): yield acima da média é positivo
    - P/VP (25%): desconto patrimonial é positivo
    - Liquidez (20%): liquidez alta é positivo
    - Volatilidade (15%): volatilidade baixa é positivo
    - Spread vs CDI (10%): spread positivo é positivo

    DY alto exige validação de risco (Anti-BS).
    P/VP sozinho não valida ativo (M2).
    """
    score_dy = min(dy / 15.0, 1.0)                      # 15% DY = score máximo
    score_pvp = max(0.0, min(1.0, (1.2 - pvp) / 0.7))  # P/VP < 0.5 = máximo, > 1.2 = zero
    score_liq = min(liquidez / 1_000_000, 1.0)           # R$1M diário = máximo
    score_vol = max(0.0, 1.0 - volatilidade / 40.0)     # vol > 40% = zero
    score_spread = min(max(spread_cdi, 0) / 5.0, 1.0)   # +5 p.p. vs CDI = máximo

    score = (
        score_dy * 0.30
        + score_pvp * 0.25
        + score_liq * 0.20
        + score_vol * 0.15
        + score_spread * 0.10
    )
    return round(score, 4)


def classificar_score(score: float) -> Decisao:
    if score >= 0.60:
        return Decisao.COMPRAR
    if score >= 0.30:
        return Decisao.MANTER
    return Decisao.REDUZIR
