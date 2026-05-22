"""
Jornada Completa — semana a semana.

Simula Roberto abrindo conta em fevereiro, acumulando histórico durante 4 meses
e gerando o relatório de maio com todas as seções preenchidas.
"""
from __future__ import annotations

from datetime import datetime

import pytest

from core.weekly_report import gerar_relatorio_semanal
from .scenario_builders import (
    build_historico as _build_historico,
    build_maio as _build_maio,
    build_parcelas as _build_parcelas,
    build_budgets as _build_budgets,
)


class TestJornadaCompletaSemanaASemana:
    """
    Simula a jornada completa do usuário:
    - Abre conta em fevereiro
    - Registra transações semana a semana durante 4 meses
    - Cria parcelamentos
    - Configura orçamentos
    - Gera relatório semanal em maio
    - Valida todas as seções do relatório
    """

    @pytest.fixture()
    def relatorio_maio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs,
            installments=_build_parcelas(),
            budgets=_build_budgets(),
            ano=2026,
            mes=5,
            meta_poupanca=30.0,
            caixa_pct=20.0,
        )

    def test_relatorio_gerado_com_sucesso(self, relatorio_maio):
        assert relatorio_maio is not None

    def test_relatorio_tem_data_geracao(self, relatorio_maio):
        assert isinstance(relatorio_maio.gerado_em, datetime)

    def test_saldo_positivo_no_mes(self, relatorio_maio):
        assert relatorio_maio.saldo_mes.saldo > 0

    def test_score_entre_0_e_100(self, relatorio_maio):
        assert 0 <= relatorio_maio.score.total <= 100

    def test_tendencias_cobrindo_quatro_meses(self, relatorio_maio):
        assert len(relatorio_maio.tendencias) == 4

    def test_top_categorias_ate_cinco(self, relatorio_maio):
        assert 1 <= len(relatorio_maio.top_categorias) <= 5

    def test_orcamentos_presentes(self, relatorio_maio):
        assert len(relatorio_maio.orcamentos) == 5

    def test_parcelas_presentes(self, relatorio_maio):
        assert len(relatorio_maio.parcelas) == 2

    def test_comprometimento_futuro_presente(self, relatorio_maio):
        assert len(relatorio_maio.comprometimento) > 0

    def test_relatorio_indica_estouro_em_alimentacao(self, relatorio_maio):
        alim = next(
            (o for o in relatorio_maio.orcamentos if o.category == "Alimentação"), None
        )
        assert alim is not None
        assert alim.status == "ESTOURO"

    def test_relatorio_detecta_alerta_comportamental(self, relatorio_maio):
        # Alimentação em maio (~1850) vs média fev-abr (~800) → ratio > 1.3
        assert len(relatorio_maio.alertas) > 0

    def test_relatorio_score_nao_e_perfeito_com_estouro(self, relatorio_maio):
        # Orçamento em estouro → não pode ter 100
        assert relatorio_maio.score.total < 100

    def test_resumo_parcelas_tem_total_restante_positivo(self, relatorio_maio):
        for p in relatorio_maio.parcelas:
            assert p.total_remaining > 0

    def test_serie_tendencia_ascendente_ou_estavel(self, relatorio_maio):
        """Ganhos de fev-mai são todos 12k — linha plana esperada."""
        t = relatorio_maio.tendencias
        ganhos = [m.ganhos for m in t]
        # Todos devem ser ≈ 12000 (fev-mai mesma renda)
        assert all(g == pytest.approx(12_000.0) for g in ganhos)
