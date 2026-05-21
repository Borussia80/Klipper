from __future__ import annotations

from datetime import date


def formatar_moeda_brl(valor: float) -> str:
    """Formata valor como moeda brasileira: R$ 1.234,56"""
    formatted = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def formatar_percentual(valor: float, casas: int = 2) -> str:
    """Formata valor como percentual: 12,34%"""
    return f"{valor:.{casas}f}%".replace(".", ",")


def formatar_data_br(d: date) -> str:
    """Formata data no padrão brasileiro: 21/05/2026"""
    return d.strftime("%d/%m/%Y")


def formatar_numero_compacto(valor: float) -> str:
    """Formata número grande de forma compacta: 1.2M, 350K"""
    if abs(valor) >= 1_000_000:
        return f"{valor / 1_000_000:.1f}M".replace(".", ",")
    if abs(valor) >= 1_000:
        return f"{valor / 1_000:.1f}K".replace(".", ",")
    return formatar_moeda_brl(valor)
