from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as Date

from models.transaction import Transaction, TransactionType
from models.budget import Budget
from models.installment import Installment


@dataclass
class OrcamentoStatus:
    category: str
    limite: float
    gasto: float

    @property
    def pct(self) -> float:
        return round((self.gasto / self.limite * 100), 1) if self.limite > 0 else 0.0

    @property
    def status(self) -> str:
        if self.pct >= 100:
            return "ESTOURO"
        if self.pct >= 80:
            return "ALERTA"
        return "OK"


@dataclass
class BehavioralAlert:
    code: str
    category: str
    gasto_atual: float
    media_3m: float
    ratio: float


@dataclass
class ScoreFinanceiro:
    total: int
    cumpriu_orcamento: bool
    atingiu_meta_poupanca: bool
    caixa_m2_ok: bool
    sem_gasto_acima_media: bool
    sem_parcela_atrasada: bool
    detalhes: dict[str, int] = field(default_factory=dict)


def calcular_score_financeiro(
    transacoes: list[Transaction],
    budgets: list[Budget],
    installments: list[Installment],
    taxa_poupanca_atual: float,
    meta_poupanca: float,
    caixa_pct: float,
    transacoes_3_meses: list[Transaction] | None = None,
) -> ScoreFinanceiro:
    """
    Score 0–100:
      - Orçamento OK (todas as categorias dentro do limite): +30
      - Meta de poupança atingida: +25
      - Caixa M2 ≥ 20%: +20
      - Sem gasto acima da média dos últimos 3 meses: +15
      - Sem parcela atrasada: +10
    """
    sem_estouro   = _cumpriu_orcamento(transacoes, budgets)
    atingiu_poupa = taxa_poupanca_atual >= meta_poupanca
    caixa_ok      = caixa_pct >= 20.0
    sem_acima     = _sem_gasto_acima_media(transacoes, transacoes_3_meses)
    sem_atraso    = _sem_parcela_atrasada(installments)

    pontos = {
        "orcamento": 30 if sem_estouro   else 0,
        "poupanca":  25 if atingiu_poupa else 0,
        "caixa":     20 if caixa_ok      else 0,
        "media":     15 if sem_acima     else 0,
        "parcelas":  10 if sem_atraso    else 0,
    }
    return ScoreFinanceiro(
        total=sum(pontos.values()),
        cumpriu_orcamento=sem_estouro,
        atingiu_meta_poupanca=atingiu_poupa,
        caixa_m2_ok=caixa_ok,
        sem_gasto_acima_media=sem_acima,
        sem_parcela_atrasada=sem_atraso,
        detalhes=pontos,
    )


def _cumpriu_orcamento(transacoes: list[Transaction], budgets: list[Budget]) -> bool:
    if not budgets:
        return True
    return all(s.status != "ESTOURO" for s in calcular_uso_orcamento(transacoes, budgets))


def _sem_gasto_acima_media(
    transacoes: list[Transaction],
    transacoes_3_meses: list[Transaction] | None,
) -> bool:
    if not transacoes_3_meses:
        return True
    return len(detectar_alertas_padrao(transacoes, transacoes_3_meses)) == 0


def _sem_parcela_atrasada(installments: list[Installment]) -> bool:
    hoje = Date.today()
    return not any(
        inst.is_active and inst.next_due_date and inst.next_due_date < hoje
        for inst in installments
    )


def detectar_alertas_padrao(
    transacoes_mes_atual: list[Transaction],
    transacoes_3_meses: list[Transaction],
    threshold: float = 1.3,
) -> list[BehavioralAlert]:
    """Detects categories where spending > threshold × 3-month average."""
    gastos_atual = _gastos_por_categoria(transacoes_mes_atual)
    gastos_3m = _gastos_por_categoria(transacoes_3_meses)

    alertas: list[BehavioralAlert] = []
    for cat, gasto in gastos_atual.items():
        media = gastos_3m.get(cat, 0.0) / 3.0
        if media > 0 and gasto > media * threshold:
            alertas.append(BehavioralAlert(
                code="GASTO_ACIMA_MEDIA",
                category=cat,
                gasto_atual=round(gasto, 2),
                media_3m=round(media, 2),
                ratio=round(gasto / media, 2),
            ))
    return alertas


def calcular_uso_orcamento(
    transacoes: list[Transaction],
    budgets: list[Budget],
) -> list[OrcamentoStatus]:
    """Returns spending vs limit for each budget category."""
    gastos = _gastos_por_categoria(transacoes)
    result: list[OrcamentoStatus] = []
    for b in budgets:
        gasto = gastos.get(b.category, 0.0)
        result.append(OrcamentoStatus(
            category=b.category,
            limite=b.monthly_limit,
            gasto=round(gasto, 2),
        ))
    return result


def _gastos_por_categoria(transacoes: list[Transaction]) -> dict[str, float]:
    totais: dict[str, float] = {}
    for t in transacoes:
        if t.type == TransactionType.GASTO:
            cat = t.category.value
            totais[cat] = totais.get(cat, 0.0) + t.amount
    return totais
