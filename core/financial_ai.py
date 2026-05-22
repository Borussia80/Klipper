"""Financial AI — NVIDIA NIM-powered personal finance intelligence for Klipper."""

from __future__ import annotations

import calendar
import logging
import os
from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.analytics import CategoriaResumo, SaldoMensal
    from core.behavioral import BehavioralAlert, OrcamentoStatus, ScoreFinanceiro
    from models.bank_account import BankAccount
    from models.installment import Installment

log = logging.getLogger(__name__)

_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
_CHAT_MODEL   = "meta/llama-3.3-70b-instruct"
_VISION_MODEL = "meta/llama-3.2-11b-vision-instruct"

SYSTEM_PROMPT = """Você é Kira — a inteligência financeira pessoal do Klipper.

Você conhece TODOS os dados financeiros do usuário: saldo, gastos por categoria,
orçamentos, parcelas, contas e score de saúde financeira.

Diretrizes absolutas:
- Matemática ancora. Narrativa sem evidência quantitativa não altera decisão.
- Seja direto e conciso. Máximo 200 palavras por resposta.
- Use R$ e % em todas as métricas.
- Reporte riscos antes de oportunidades.
- Declare incerteza quando dados forem insuficientes.
- Nunca invente dados que não estão no contexto.
- Responda sempre em português brasileiro.
"""


@dataclass
class FinancialContext:
    """Structured snapshot of all financial data for AI briefing."""
    ano: int
    mes: int
    saldo: "SaldoMensal | None" = None
    score: "ScoreFinanceiro | None" = None
    alertas_padrao: list["BehavioralAlert"] = field(default_factory=list)
    orcamentos: list["OrcamentoStatus"] = field(default_factory=list)
    top_categorias: list["CategoriaResumo"] = field(default_factory=list)
    contas: list["BankAccount"] = field(default_factory=list)
    parcelas_ativas: list["Installment"] = field(default_factory=list)


def build_financial_context(
    ano: int,
    mes: int,
    *,
    saldo: "SaldoMensal | None" = None,
    score: "ScoreFinanceiro | None" = None,
    alertas_padrao: "list[BehavioralAlert] | None" = None,
    orcamentos: "list[OrcamentoStatus] | None" = None,
    top_categorias: "list[CategoriaResumo] | None" = None,
    contas: "list[BankAccount] | None" = None,
    parcelas_ativas: "list[Installment] | None" = None,
) -> FinancialContext:
    return FinancialContext(
        ano=ano,
        mes=mes,
        saldo=saldo,
        score=score,
        alertas_padrao=alertas_padrao or [],
        orcamentos=orcamentos or [],
        top_categorias=top_categorias or [],
        contas=contas or [],
        parcelas_ativas=parcelas_ativas or [],
    )


def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _context_to_text(ctx: FinancialContext) -> str:
    mes_nome = calendar.month_name[ctx.mes]
    lines = [f"## Contexto financeiro — {mes_nome}/{ctx.ano}\n"]

    if ctx.saldo:
        s = ctx.saldo
        lines.append(
            f"**Saldo mensal:** entradas {_fmt_brl(s.total_ganhos)} | "
            f"gastos {_fmt_brl(s.total_gastos)} | "
            f"saldo {_fmt_brl(s.saldo)} | "
            f"taxa de poupança {s.taxa_poupanca:.1f}%"
        )

    if ctx.score:
        sc = ctx.score
        lines.append(
            f"\n**Score financeiro:** {sc.total}/100 | "
            f"orçamento {'✓' if sc.cumpriu_orcamento else '✗'} | "
            f"poupança {'✓' if sc.atingiu_meta_poupanca else '✗'} | "
            f"caixa M2 {'✓' if sc.caixa_m2_ok else '✗'} | "
            f"sem parcela atrasada {'✓' if sc.sem_parcela_atrasada else '✗'}"
        )

    if ctx.top_categorias:
        lines.append("\n**Top categorias de gasto:**")
        for c in ctx.top_categorias:
            lines.append(f"  - {c.category}: {_fmt_brl(c.total)} ({c.percentual:.1f}%)")

    if ctx.orcamentos:
        linhas_orc = [o for o in ctx.orcamentos if o.status != "OK"]
        if linhas_orc:
            lines.append("\n**Orçamentos em alerta/estouro:**")
            for o in linhas_orc:
                lines.append(
                    f"  - {o.category}: {_fmt_brl(o.gasto)} / {_fmt_brl(o.limite)} "
                    f"({o.pct:.0f}%) [{o.status}]"
                )

    if ctx.alertas_padrao:
        lines.append("\n**Alertas de padrão de gasto:**")
        for a in ctx.alertas_padrao:
            lines.append(
                f"  - {a.category}: {_fmt_brl(a.gasto_atual)} vs média {_fmt_brl(a.media_3m)} "
                f"({a.ratio:.1f}×)"
            )

    if ctx.contas:
        lines.append("\n**Contas bancárias:**")
        total = sum(c.balance for c in ctx.contas)
        for c in ctx.contas:
            lines.append(f"  - {c.name} ({c.bank}): {_fmt_brl(c.balance)}")
        lines.append(f"  **Patrimônio total em contas:** {_fmt_brl(total)}")

    if ctx.parcelas_ativas:
        comprometimento = sum(i.installment_amount for i in ctx.parcelas_ativas if i.is_active)
        lines.append(
            f"\n**Parcelamentos ativos:** {len(ctx.parcelas_ativas)} planos | "
            f"comprometimento mensal {_fmt_brl(comprometimento)}"
        )
        for i in ctx.parcelas_ativas[:5]:
            lines.append(
                f"  - {i.description}: {_fmt_brl(i.installment_amount)}/mês "
                f"({i.n_remaining} restantes)"
            )

    return "\n".join(lines)


def _get_client():
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError("openai package not installed. Run: pip install openai") from e

    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY não configurada no ambiente.")

    return OpenAI(base_url=_NIM_BASE_URL, api_key=api_key)


def ask(
    question: str,
    ctx: FinancialContext | None = None,
    history: list[dict] | None = None,
) -> str:
    """Send a question to NVIDIA NIM with full financial context injected."""
    client = _get_client()

    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if ctx:
        ctx_text = _context_to_text(ctx)
        messages.append({"role": "system", "content": ctx_text})

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": question})

    try:
        resp = client.chat.completions.create(
            model=_CHAT_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=512,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        log.error("Erro ao chamar NVIDIA NIM: %s", e)
        raise


def auto_briefing(ctx: FinancialContext) -> str:
    """Generate a concise daily financial briefing for the Dashboard widget."""
    hoje = date.today()
    prompt = (
        f"Hoje é {hoje.strftime('%d/%m/%Y')}. "
        "Analise os dados financeiros e gere um briefing de até 3 parágrafos curtos com: "
        "(1) situação geral do mês, (2) principal ponto de atenção, (3) uma ação recomendada. "
        "Seja direto. Use os números do contexto."
    )
    return ask(prompt, ctx=ctx)


def extract_pdf_transactions(pdf_bytes: bytes, bank_name: str = "") -> str:
    """
    Extract transactions from a bank statement PDF using NVIDIA vision model.

    Returns raw text that should be parsed into Transaction objects.
    Caller is responsible for parsing the response.
    """
    import base64

    client = _get_client()

    pdf_b64 = base64.b64encode(pdf_bytes).decode()
    prompt = (
        f"Extraia todas as transações deste extrato bancário ({bank_name}). "
        "Para cada transação, retorne uma linha no formato: "
        "DATA|DESCRIÇÃO|VALOR|TIPO (DÉBITO ou CRÉDITO). "
        "Use formato de data DD/MM/YYYY. Use ponto como separador decimal. "
        "Não inclua cabeçalhos nem explicações — apenas as linhas de dados."
    )

    try:
        resp = client.chat.completions.create(
            model=_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:application/pdf;base64,{pdf_b64}"},
                    },
                ],
            }],
            temperature=0.1,
            max_tokens=2048,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        log.error("Erro ao extrair PDF com NVIDIA NIM: %s", e)
        raise
