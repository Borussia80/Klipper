from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.transaction import Category, Transaction


@dataclass
class SaldoMensal:
    ano: int
    mes: int
    total_ganhos: Decimal
    total_gastos: Decimal

    @property
    def saldo(self) -> Decimal:
        return self.total_ganhos - self.total_gastos

    @property
    def taxa_poupanca(self) -> float:
        if self.total_ganhos == 0:
            return 0.0
        return float(round(self.saldo / self.total_ganhos * 100, 1))


@dataclass
class CategoriaResumo:
    category: str
    total: Decimal
    percentual: float


def calcular_saldo_mensal(transacoes: list[Transaction], ano: int, mes: int) -> SaldoMensal:
    from models.transaction import TransactionType
    txs_mes = [t for t in transacoes if t.date.year == ano and t.date.month == mes]
    ganhos = sum((t.amount for t in txs_mes if t.type == TransactionType.GANHO), Decimal(0))
    gastos = sum((t.amount for t in txs_mes if t.type == TransactionType.GASTO), Decimal(0))
    return SaldoMensal(ano=ano, mes=mes, total_ganhos=ganhos, total_gastos=gastos)


def calcular_top_categorias(
    transacoes: list[Transaction], n: int = 5
) -> list[CategoriaResumo]:
    from models.transaction import TransactionType
    gastos = [t for t in transacoes if t.type == TransactionType.GASTO]
    total_geral = sum((t.amount for t in gastos), Decimal(0)) or Decimal("1")

    por_categoria: dict[str, Decimal] = {}
    for t in gastos:
        por_categoria[t.category.value] = por_categoria.get(t.category.value, Decimal(0)) + t.amount

    return sorted(
        [
            CategoriaResumo(
                category=cat,
                total=round(total, 2),
                percentual=float(round(total / total_geral * 100, 1)),
            )
            for cat, total in por_categoria.items()
        ],
        key=lambda x: x.total,
        reverse=True,
    )[:n]
