from __future__ import annotations

import calendar
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.transaction import Category, Transaction

_MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


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


def preparar_dados_donut_categorias(
    transacoes: list[Transaction],
) -> list[dict]:
    """Agrega gastos por categoria para chart de donut.

    Retorna lista de {"categoria": str, "total": float} ordenada decrescente.
    Exclui transações GANHO e a categoria Investimento.
    Limitado a 8 categorias (top por valor).
    """
    from models.transaction import TransactionType, Category as Cat

    por_cat: dict[str, Decimal] = {}
    for t in transacoes:
        if t.type != TransactionType.GASTO:
            continue
        if t.category == Cat.INVESTIMENTO:
            continue
        por_cat[t.category.value] = por_cat.get(t.category.value, Decimal(0)) + t.amount

    resultado = sorted(
        [{"categoria": cat, "total": float(total)} for cat, total in por_cat.items()],
        key=lambda x: x["total"],
        reverse=True,
    )
    return resultado[:8]


def preparar_dados_barras_mensais(
    registros: list[tuple[int, int, Decimal, Decimal]],
) -> list[dict]:
    """Prepara dados para bar chart de entradas × saídas mensais.

    Args:
        registros: lista de (ano, mes, total_ganhos, total_gastos)

    Returns:
        Lista de {"mes": "Jan/26", "Entradas": float, "Saídas": float}
        ordenada cronologicamente.
    """
    ordenados = sorted(registros, key=lambda r: (r[0], r[1]))
    return [
        {
            "mes": f"{_MESES_PT[mes - 1]}/{str(ano)[-2:]}",
            "Entradas": float(ganhos),
            "Saídas": float(gastos),
        }
        for ano, mes, ganhos, gastos in ordenados
    ]
