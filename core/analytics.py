from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.investment import Investment
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


def preparar_dados_bolha(
    portfolio: list[Investment],
    total_portfolio: Decimal,
) -> list[dict]:
    """Agrega dados do portfólio para bubble chart DY × P/VP × valor.

    Exclui ativos sem fundamentos (dy=0 e pvp=0, ex.: ETFs).
    Retorna lista ordenada por valor decrescente.
    """
    rows = []
    total = float(total_portfolio) if total_portfolio else 0.0
    for inv in portfolio:
        if inv.dy_12m == 0.0 and inv.pvp == 0.0:
            continue
        valor = float(inv.quantity) * float(inv.current_price)
        peso = (valor / total * 100.0) if total > 0 else 0.0
        rows.append({
            "ticker": inv.ticker,
            "dy_12m": float(inv.dy_12m),
            "pvp": float(inv.pvp),
            "valor": valor,
            "peso_pct": peso,
            "tipo": inv.type.value,
        })
    rows.sort(key=lambda r: r["valor"], reverse=True)
    return rows


def preparar_dados_linha_normalizado(
    portfolio_hist: list[dict],
    benchmarks_hist: dict[str, list[dict]],
) -> list[dict]:
    """Normaliza histórico de portfólio e benchmarks para base 100 no dia 0.

    Args:
        portfolio_hist: [{"date": date, "valor": float}, ...]
        benchmarks_hist: {ticker: [{"date": date, "close": float}, ...], ...}

    Returns:
        [{"date": str, "Portfólio": float, "BOVA11": float, ...}, ...]
    """
    if not portfolio_hist:
        return []

    base_port = float(portfolio_hist[0]["valor"])
    result = []
    for i, entry in enumerate(portfolio_hist):
        val_port = float(entry["valor"])
        row: dict = {
            "date": entry["date"].strftime("%Y-%m-%d") if hasattr(entry["date"], "strftime") else str(entry["date"]),
            "Portfólio": (val_port / base_port * 100.0) if base_port else 100.0,
        }
        for ticker, hist in benchmarks_hist.items():
            if not hist:
                continue
            base_bench = float(hist[0]["close"])
            close = float(hist[i]["close"]) if i < len(hist) else float(hist[-1]["close"])
            row[ticker] = (close / base_bench * 100.0) if base_bench else 100.0
        result.append(row)
    return result


def preparar_dados_gauge_limite(
    fatura: Decimal,
    limite_total: Decimal,
) -> dict:
    """Prepara dados para gauge Plotly de uso do limite do cartão.

    Returns:
        {"usado": float, "limite": float, "disponivel": float,
         "pct_uso": float, "status": "ok" | "alerta" | "estouro"}
    """
    usado = float(fatura)
    limite = float(limite_total)

    if limite <= 0:
        return {"usado": usado, "limite": limite, "disponivel": 0.0,
                "pct_uso": 0.0, "status": "ok"}

    pct = min(usado / limite * 100.0, 100.0)
    disponivel = max(limite - usado, 0.0)
    status = "estouro" if pct >= 80 else "alerta" if pct >= 50 else "ok"
    return {
        "usado": usado,
        "limite": limite,
        "disponivel": disponivel,
        "pct_uso": pct,
        "status": status,
    }


def preparar_dados_tesouro_historico(
    historico: list[dict],
    bond_name: str,
) -> list[dict]:
    """Filtra e formata histórico do Tesouro para line chart.

    Returns:
        [{"date": str, "Taxa (%)": float, "Preço (R$)": float}, ...]
        ordenado cronologicamente.
    """
    subset = [r for r in historico if r.get("bond_type") == bond_name]
    subset.sort(key=lambda r: r["date"])
    return [
        {
            "date": r["date"].strftime("%d/%m/%Y") if hasattr(r["date"], "strftime") else str(r["date"]),
            "Taxa (%)": float(r["rate_buy"]),
            "Preço (R$)": float(r["price_buy"]),
        }
        for r in subset
    ]


def preparar_gastos_diarios(
    transacoes: list[Transaction],
    ano: int,
    mes: int,
    cumulative: bool = False,
) -> list[dict]:
    """Agrega gastos por dia do mês para line chart.

    Returns:
        [{"dia": int, "date": str, "Gastos": float}, ...] ordenado por dia.
        Se cumulative=True, "Gastos" é acumulado.
    """
    from models.transaction import TransactionType

    por_dia: dict[int, float] = {}
    for t in transacoes:
        if t.date.year != ano or t.date.month != mes:
            continue
        if t.type != TransactionType.GASTO:
            continue
        por_dia[t.date.day] = por_dia.get(t.date.day, 0.0) + float(t.amount)

    if not por_dia:
        return []

    dias_sorted = sorted(por_dia.keys())
    acum = 0.0
    result = []
    for dia in dias_sorted:
        val = por_dia[dia]
        if cumulative:
            acum += val
            val = acum
        d = date(ano, mes, dia)
        result.append({
            "dia": dia,
            "date": d.strftime("%d/%m"),
            "Gastos": val,
        })
    return result


def preparar_comparativo_categorias(
    transacoes_atual: list[Transaction],
    transacoes_anterior: list[Transaction],
    top_n: int = 8,
) -> list[dict]:
    """Agrega gastos por categoria para comparativo mês atual vs anterior.

    Returns:
        [{"categoria": str, "Este mês": float, "Mês anterior": float}, ...]
        ordenado por "Este mês" decrescente, limitado a top_n.
    """
    from models.transaction import TransactionType

    def _agrupar(txs: list[Transaction]) -> dict[str, float]:
        por_cat: dict[str, float] = {}
        for t in txs:
            if t.type != TransactionType.GASTO:
                continue
            por_cat[t.category.value] = por_cat.get(t.category.value, 0.0) + float(t.amount)
        return por_cat

    atual = _agrupar(transacoes_atual)
    anterior = _agrupar(transacoes_anterior)

    todas_cats = set(atual.keys()) | set(anterior.keys())
    if not todas_cats:
        return []

    rows = [
        {
            "categoria": cat,
            "Este mês": atual.get(cat, 0.0),
            "Mês anterior": anterior.get(cat, 0.0),
        }
        for cat in todas_cats
    ]
    rows.sort(key=lambda r: r["Este mês"], reverse=True)
    return rows[:top_n]


def detect_spending_alerts(
    current: dict[str, float],
    baseline: dict[str, float],
    threshold: float = 1.3,
) -> list[dict]:
    """Return categories where current spending exceeds baseline * threshold.

    Args:
        current:   {category: amount} for the period being evaluated.
        baseline:  {category: average_amount} used as reference.
        threshold: multiplier above which an alert is raised (default 1.3).

    Returns:
        List of dicts with keys: category, current, baseline, ratio.
        Sorted by ratio descending. Empty list if no violations.
    """
    alerts = []
    for category, current_amt in current.items():
        base = baseline.get(category, 0.0)
        if base <= 0:
            continue
        ratio = current_amt / base
        if ratio > threshold:
            alerts.append({
                "category": category,
                "current": current_amt,
                "baseline": base,
                "ratio": round(ratio, 2),
            })
    alerts.sort(key=lambda a: a["ratio"], reverse=True)
    return alerts


def preparar_sparkline_score_historico(
    registros: list[tuple[int, int, Decimal, Decimal]],
    meta_poupanca: float = 20.0,
) -> list[dict]:
    """Proxy de score financeiro histórico a partir de (ano, mes, ganhos, gastos).

    Score proxy 0–100: taxa de poupança mapeada linearmente onde meta_poupanca → 100.
    Fórmula: clamp(round(taxa_poupanca * (100 / meta_poupanca)), 0, 100).

    Args:
        registros: lista de (ano, mes, total_ganhos, total_gastos).
        meta_poupanca: percentual de poupança que equivale a 100 pts (padrão 20%).

    Returns:
        Lista de {"mes": "Jan/26", "score": int} ordenada cronologicamente.
    """
    fator = 100.0 / meta_poupanca if meta_poupanca > 0 else 0.0
    ordenados = sorted(registros, key=lambda r: (r[0], r[1]))
    result = []
    for ano, mes, ganhos, gastos in ordenados:
        g = float(ganhos)
        if g <= 0:
            score = 0
        else:
            taxa = (g - float(gastos)) / g * 100.0
            score = min(100, max(0, round(taxa * fator)))
        result.append({"mes": f"{_MESES_PT[mes - 1]}/{str(ano)[-2:]}", "score": score})
    return result
