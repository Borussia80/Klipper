"""
Builders de cenário puro para os testes da jornada do usuário.

Funções puras — sem estado, sem fixtures pytest, sem side effects.
Todas as datas são absolutas (F.I.R.S.T.-R).

Cenário base: Roberto · R$ 12.000/mês · histórico fev–abr 2026 + maio 2026
com estouro de Alimentação (R$1.850 vs limite R$1.200).
"""
from __future__ import annotations

from datetime import date

from models.transaction import Transaction, TransactionType, Category, PaymentMethod, TransactionStatus
from models.budget import Budget
from models.installment import Installment


def _tx(
    d: date,
    amount: float,
    type_: TransactionType,
    cat: Category,
    *,
    notes: str = "",
    method: PaymentMethod = PaymentMethod.PIX,
    status: TransactionStatus = TransactionStatus.PAGO,
) -> Transaction:
    return Transaction(
        date=d, amount=amount, type=type_, category=cat,
        notes=notes, payment_method=method, status=status,
    )


def _ganho(d: date, amount: float, cat: Category = Category.RENDA) -> Transaction:
    return _tx(d, amount, TransactionType.GANHO, cat)


def _gasto(d: date, amount: float, cat: Category, **kw) -> Transaction:
    return _tx(d, amount, TransactionType.GASTO, cat, **kw)


def _budget(cat: Category, limite: float, ano: int = 2026, mes: int = 5) -> Budget:
    return Budget(category=cat.value, monthly_limit=limite, year=ano, month=mes)


def _installment(desc: str, total: float, n: int, start: date) -> Installment:
    return Installment(description=desc, total_amount=total, n_total=n, start_date=start)


def build_historico() -> list[Transaction]:
    """Três meses de histórico (fev/mar/abr) para tendências e alertas comportamentais."""
    txs: list[Transaction] = []
    for mes in (2, 3, 4):
        txs += [
            _ganho(date(2026, mes, 5),  12_000.0),
            _gasto(date(2026, mes, 5),   2_000.0, Category.MORADIA),
            _gasto(date(2026, mes, 10),    800.0, Category.ALIMENTACAO),
            _gasto(date(2026, mes, 12),    300.0, Category.TRANSPORTE),
            _gasto(date(2026, mes, 15),    200.0, Category.SAUDE),
            _gasto(date(2026, mes, 20),    250.0, Category.LAZER),
        ]
    return txs


def build_maio() -> list[Transaction]:
    """Maio/2026 — estouro em Alimentação (R$1.850 vs limite R$1.200)."""
    return [
        _ganho(date(2026, 5,  5), 12_000.0),
        _gasto(date(2026, 5,  5),  2_000.0, Category.MORADIA),
        _gasto(date(2026, 5,  7),    850.0, Category.ALIMENTACAO),
        _gasto(date(2026, 5,  7),    200.0, Category.TRANSPORTE),
        _gasto(date(2026, 5, 10),    400.0, Category.ALIMENTACAO),
        _gasto(date(2026, 5, 12),    350.0, Category.SAUDE),
        _gasto(date(2026, 5, 14),    150.0, Category.OUTROS),
        _gasto(date(2026, 5, 18),    600.0, Category.ALIMENTACAO),
        _gasto(date(2026, 5, 20),    500.0, Category.LAZER),
        _gasto(date(2026, 5, 25),    180.0, Category.MORADIA),
        _gasto(date(2026, 5, 28),    250.0, Category.TRANSPORTE),
        _gasto(date(2026, 5, 10),  2_000.0, Category.INVESTIMENTO),
    ]


def build_parcelas() -> list[Installment]:
    return [
        _installment("Notebook Dell",    4_200.0, 12, date(2026, 1, 1)),
        _installment("Smart TV Samsung", 1_200.0,  6, date(2026, 2, 1)),
    ]


def build_budgets() -> list[Budget]:
    return [
        _budget(Category.MORADIA,     2_200.0),
        _budget(Category.ALIMENTACAO, 1_200.0),   # vai estourar com R$1.850
        _budget(Category.TRANSPORTE,    500.0),
        _budget(Category.SAUDE,         400.0),
        _budget(Category.LAZER,         400.0),
    ]


# Aliases para uso pontual nos testes (sem o prefixo _build_)
ganho = _ganho
gasto = _gasto
budget = _budget
