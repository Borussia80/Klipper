from __future__ import annotations

from decimal import Decimal
from typing import Any


def distribuir_splits_proporcional(
    splits: list[dict[str, Any]],
    parcela_amount: Decimal,
    total_amount: Decimal,
) -> list[Decimal]:
    """Distribui o valor de uma parcela proporcionalmente entre os splits.

    Os splits descrevem o total da compra (não da parcela individual).
    O último split absorve o centavo residual, garantindo que
    sum(resultado) == parcela_amount exatamente.

    Args:
        splits: lista de {category, amount} onde amount se refere ao total da compra.
        parcela_amount: valor desta parcela específica.
        total_amount: valor total da compra (soma de todos os splits).

    Returns:
        Lista de Decimal com os valores proporcionais para cada split,
        na mesma ordem de entrada.
    """
    if not splits:
        return []

    parcela_cents = int(parcela_amount * 100)
    total_cents = int(total_amount * 100)

    result_cents: list[int] = []
    allocated = 0
    for split in splits[:-1]:
        split_cents = int(Decimal(str(split["amount"])) * 100)
        this_cents = int(split_cents * parcela_cents / total_cents)
        result_cents.append(this_cents)
        allocated += this_cents

    result_cents.append(parcela_cents - allocated)

    return [Decimal(c) / 100 for c in result_cents]
