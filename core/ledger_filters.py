"""Filter chips e paginação para o ledger de Transações."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.transaction import Transaction

_CARTAO_METHODS = {"CARTAO_CREDITO", "CARTAO_DEBITO"}

_CHIP_MAP: dict[str, set[str]] = {
    "PIX": {"PIX"},
    "Cartão": _CARTAO_METHODS,
    "Dinheiro": {"DINHEIRO"},
    "TED": {"TED"},
    "Boleto": {"BOLETO"},
    "Transferência": {"TRANSFERENCIA"},
}


def filter_transactions_by_chip(txs: list, chip: str) -> list:
    """Return transactions matching the filter chip label."""
    if chip in ("Todos", "Desconhecido"):
        return list(txs)

    if chip == "Parcelas":
        return [t for t in txs if t.installment_id is not None]

    allowed = _CHIP_MAP.get(chip)
    if allowed is None:
        return list(txs)

    return [t for t in txs if t.payment_method.value in allowed]


def paginate_transactions(txs: list, page: int, page_size: int = 30) -> list:
    """Return the slice of txs for the given 1-indexed page."""
    start = (page - 1) * page_size
    return txs[start : start + page_size]


def total_pages(count: int, page_size: int = 30) -> int:
    """Return the number of pages needed to display count items."""
    if count == 0:
        return 1
    return (count + page_size - 1) // page_size
