"""
Testes de performance — financial_ai context pipeline e analytics em volume.

Limites estabelecidos por medição empírica com margem de segurança 3×.
Cada assertion de tempo deve passar em hardware de CI (GitHub Actions, Streamlit Cloud).
"""

from __future__ import annotations

from datetime import date, timedelta
from time import perf_counter

import pytest

from core.analytics import calcular_saldo_mensal, calcular_top_categorias
from core.behavioral import (
    BehavioralAlert,
    OrcamentoStatus,
    ScoreFinanceiro,
    detectar_alertas_padrao,
)
from core.financial_ai import (
    FinancialContext,
    _context_to_text,
    build_financial_context,
)
from core.installment_engine import (
    calcular_comprometimento_mensal,
    gerar_parcelas,
)
from models.bank_account import AccountType, BankAccount
from models.budget import Budget
from models.installment import Installment
from models.transaction import Category, PaymentMethod, Transaction, TransactionType


# ── Builders ──────────────────────────────────────────────────────────────────

def _tx(
    amount: float,
    tipo: TransactionType = TransactionType.GASTO,
    category: Category = Category.ALIMENTACAO,
    tx_date: date | None = None,
) -> Transaction:
    return Transaction(
        date=tx_date or date(2026, 5, 15),
        amount=amount,
        type=tipo,
        category=category,
        payment_method=PaymentMethod.PIX,
    )


def _batch_txs(n: int, ano: int = 2026, meses: tuple[int, ...] = (5,)) -> list[Transaction]:
    cats = list(Category)
    base = date(ano, 1, 1)
    return [
        _tx(
            amount=float((i % 500) + 1),
            tipo=TransactionType.GANHO if i % 7 == 0 else TransactionType.GASTO,
            category=cats[i % len(cats)],
            tx_date=base + timedelta(days=i % 365),
        )
        for i in range(n)
    ]


def _make_installments(n: int) -> list[Installment]:
    return [
        Installment(
            description=f"Parcelamento #{i}",
            total_amount=float(1000 + i * 10),
            n_total=12,
            start_date=date(2026, 1, 15),
        )
        for i in range(n)
    ]


def _make_accounts(n: int) -> list[BankAccount]:
    return [
        BankAccount(
            name=f"Conta {i}",
            bank=f"Banco {i % 5}",
            type=list(AccountType)[i % 3],
            balance=float(10_000 + i * 500),
            color="#D9B26F",
        )
        for i in range(n)
    ]


def _make_score(total: int = 75) -> ScoreFinanceiro:
    return ScoreFinanceiro(
        total=total,
        cumpriu_orcamento=True,
        atingiu_meta_poupanca=True,
        caixa_m2_ok=True,
        sem_gasto_acima_media=True,
        sem_parcela_atrasada=True,
        detalhes={"orcamento": 30, "poupanca": 25, "caixa": 20},
    )


def _make_alertas(n: int) -> list[BehavioralAlert]:
    cats = list(Category)
    return [
        BehavioralAlert(
            code="GASTO_ACIMA_MEDIA",
            category=cats[i % len(cats)].value,
            gasto_atual=1500.0 + i * 100,
            media_3m=1000.0 + i * 50,
            ratio=1.5,
        )
        for i in range(n)
    ]


def _make_orcamentos(n: int) -> list[OrcamentoStatus]:
    cats = list(Category)
    return [
        OrcamentoStatus(
            category=cats[i % len(cats)].value,
            limite=2000.0,
            gasto=1600.0 + i * 20,
        )
        for i in range(n)
    ]


# ── build_financial_context ───────────────────────────────────────────────────

class TestBuildFinancialContextPerformance:

    def test_contexto_vazio_e_instantaneo(self):
        start = perf_counter()
        ctx = build_financial_context(2026, 5)
        elapsed = perf_counter() - start
        assert isinstance(ctx, FinancialContext)
        assert elapsed < 0.002  # < 2 ms

    def test_contexto_completo_com_dados_realistas_e_rapido(self):
        from core.analytics import calcular_saldo_mensal, calcular_top_categorias

        txs = _batch_txs(5_000)
        saldo = calcular_saldo_mensal(txs, 2026, 5)
        top = calcular_top_categorias(txs, n=10)
        score = _make_score()
        alertas = _make_alertas(5)
        orcamentos = _make_orcamentos(10)
        contas = _make_accounts(8)
        parcelas = _make_installments(50)

        start = perf_counter()
        ctx = build_financial_context(
            2026, 5,
            saldo=saldo,
            score=score,
            alertas_padrao=alertas,
            orcamentos=orcamentos,
            top_categorias=top,
            contas=contas,
            parcelas_ativas=parcelas,
        )
        elapsed = perf_counter() - start

        assert isinstance(ctx, FinancialContext)
        assert elapsed < 0.010  # < 10 ms — construção é só dataclass

    def test_contexto_preserva_referencias_dos_objetos_passados(self):
        score = _make_score(80)
        contas = _make_accounts(3)
        ctx = build_financial_context(2026, 5, score=score, contas=contas)
        assert ctx.score is score
        assert ctx.contas is contas


# ── _context_to_text ──────────────────────────────────────────────────────────

class TestContextToTextPerformance:

    def _full_ctx(self) -> FinancialContext:
        from core.analytics import calcular_saldo_mensal, calcular_top_categorias
        txs = _batch_txs(2_000)
        saldo = calcular_saldo_mensal(txs, 2026, 5)
        top = calcular_top_categorias(txs, n=10)
        return build_financial_context(
            2026, 5,
            saldo=saldo,
            score=_make_score(72),
            alertas_padrao=_make_alertas(4),
            orcamentos=_make_orcamentos(8),
            top_categorias=top,
            contas=_make_accounts(10),
            parcelas_ativas=_make_installments(30),
        )

    def test_serializacao_completa_e_rapida(self):
        ctx = self._full_ctx()
        start = perf_counter()
        text = _context_to_text(ctx)
        elapsed = perf_counter() - start
        assert elapsed < 0.005  # < 5 ms — pura formatação de strings

    def test_contexto_vazio_produz_cabecalho(self):
        ctx = build_financial_context(2026, 5)
        text = _context_to_text(ctx)
        assert "2026" in text
        assert len(text) > 0

    def test_texto_completo_contem_secoes_esperadas(self):
        ctx = self._full_ctx()
        text = _context_to_text(ctx)
        assert "Saldo mensal" in text
        assert "Score financeiro" in text
        assert "Top categorias" in text
        assert "Contas bancárias" in text
        assert "Parcelamentos ativos" in text

    def test_texto_completo_tem_tamanho_adequado_para_llm(self):
        """Contexto não pode exceder ~6 000 chars (≈ 1 500 tokens para LLM econômico)."""
        ctx = self._full_ctx()
        text = _context_to_text(ctx)
        assert len(text) < 6_000, f"Contexto muito longo: {len(text)} chars"

    def test_texto_inclui_valores_monetarios_formatados(self):
        from core.analytics import calcular_saldo_mensal
        txs = [
            _tx(5000.0, TransactionType.GANHO, Category.RENDA, date(2026, 5, 1)),
            _tx(1234.56, TransactionType.GASTO, Category.ALIMENTACAO, date(2026, 5, 5)),
        ]
        saldo = calcular_saldo_mensal(txs, 2026, 5)
        ctx = build_financial_context(2026, 5, saldo=saldo)
        text = _context_to_text(ctx)
        assert "5.000" in text or "5,000" in text or "5000" in text
        assert "taxa de poupança" in text.lower()

    def test_alertas_em_estouro_aparecem_no_texto(self):
        orcamentos = [
            OrcamentoStatus(category="Alimentação", limite=1000.0, gasto=1500.0),  # ESTOURO
            OrcamentoStatus(category="Transporte",  limite=500.0,  gasto=200.0),   # OK
        ]
        ctx = build_financial_context(2026, 5, orcamentos=orcamentos)
        text = _context_to_text(ctx)
        assert "Alimentação" in text
        assert "ESTOURO" in text
        assert "Transporte" not in text  # OK não aparece

    def test_parcelas_limitadas_a_5_no_texto(self):
        """Texto deve listar no máximo 5 parcelamentos para não explodir contexto."""
        ctx = build_financial_context(
            2026, 5, parcelas_ativas=_make_installments(20)
        )
        text = _context_to_text(ctx)
        # "Parcelamento #" aparece no texto — deve ser no máximo 5
        count = text.count("Parcelamento #")
        assert count <= 5


# ── Analytics em volume ───────────────────────────────────────────────────────

class TestAnalyticsVolumePerformance:

    def test_saldo_mensal_com_50k_transacoes(self):
        txs = _batch_txs(50_000)
        start = perf_counter()
        saldo = calcular_saldo_mensal(txs, 2026, 5)
        elapsed = perf_counter() - start
        assert saldo.total_ganhos >= 0
        assert elapsed < 0.5

    def test_top_categorias_com_50k_transacoes(self):
        txs = _batch_txs(50_000)
        start = perf_counter()
        top = calcular_top_categorias(txs, n=10)
        elapsed = perf_counter() - start
        assert len(top) == 10
        assert elapsed < 0.5

    def test_detectar_alertas_padrao_com_volume(self):
        txs_mes = _batch_txs(3_000, meses=(5,))
        txs_3m  = _batch_txs(9_000, meses=(2, 3, 4))
        start = perf_counter()
        alertas = detectar_alertas_padrao(txs_mes, txs_3m)
        elapsed = perf_counter() - start
        assert isinstance(alertas, list)
        assert elapsed < 0.3


# ── Parcelamentos em volume ───────────────────────────────────────────────────

class TestInstallmentVolumePerformance:

    def test_gerar_parcelas_para_2000_planos(self):
        insts = _make_installments(2_000)
        start = perf_counter()
        all_parcelas = [p for inst in insts for p in gerar_parcelas(inst)]
        elapsed = perf_counter() - start
        assert len(all_parcelas) == 24_000  # 2000 × 12
        assert elapsed < 2.5

    def test_calcular_comprometimento_mensal_com_500_parcelamentos(self):
        insts = _make_installments(500)
        start = perf_counter()
        comp = calcular_comprometimento_mensal(insts)
        elapsed = perf_counter() - start
        assert isinstance(comp, dict)
        assert elapsed < 0.1

    def test_comprometimento_mensal_soma_correta(self):
        """
        Todos os meses futuros de uma carteira simples devem ter parcela idêntica.
        start_date em 2030 garante que todos os 12 meses estão no futuro.
        """
        inst = Installment(
            description="Teste fixo",
            total_amount=1200.0,
            n_total=12,
            start_date=date(2030, 1, 1),
        )
        comp = calcular_comprometimento_mensal([inst])
        # todos os 12 meses de jan/2030 a dez/2030 são futuros
        assert len(comp) == 12
        for v in comp.values():
            assert v == pytest.approx(100.0)


# ── Pipeline completo: dados → contexto → texto ───────────────────────────────

class TestPipelineContextoPonta_a_Ponta:

    def test_pipeline_completo_dentro_do_limite_de_tempo(self):
        """
        Simula o que o Dashboard faz: carregar dados, calcular analytics,
        construir contexto, serializar para o LLM.
        Deve completar em < 800 ms (dados já em memória, sem I/O de rede).
        """
        from core.analytics import calcular_saldo_mensal, calcular_top_categorias
        from core.behavioral import (
            calcular_score_financeiro,
            calcular_uso_orcamento,
            detectar_alertas_padrao,
        )

        txs_mes = _batch_txs(10_000)
        txs_3m  = _batch_txs(30_000)
        budgets = [
            Budget(category=c.value, monthly_limit=2000, year=2026, month=5)
            for c in list(Category)[:6]
        ]
        insts = _make_installments(200)

        start = perf_counter()

        saldo   = calcular_saldo_mensal(txs_mes, 2026, 5)
        top     = calcular_top_categorias(txs_mes, n=10)
        alertas = detectar_alertas_padrao(txs_mes, txs_3m)
        orcam   = calcular_uso_orcamento(txs_mes, budgets)
        score   = calcular_score_financeiro(
            txs_mes, budgets, insts,
            taxa_poupanca_atual=saldo.taxa_poupanca,
            meta_poupanca=20.0,
            caixa_pct=25.0,
            transacoes_3_meses=txs_3m,
        )
        ctx  = build_financial_context(
            2026, 5,
            saldo=saldo, score=score, alertas_padrao=alertas,
            orcamentos=orcam, top_categorias=top,
            contas=_make_accounts(5), parcelas_ativas=insts[:50],
        )
        text = _context_to_text(ctx)

        elapsed = perf_counter() - start

        assert len(text) > 100
        assert elapsed < 0.800

    def test_pipeline_com_dados_vazios_nao_levanta_excecao(self):
        """Pipeline com todos os dados vazios deve produzir texto sem erros."""
        ctx  = build_financial_context(2026, 5)
        text = _context_to_text(ctx)
        assert "## Contexto financeiro" in text
