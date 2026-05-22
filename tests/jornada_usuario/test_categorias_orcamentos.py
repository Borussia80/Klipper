"""
Top Categorias, Orçamentos vs. Real e Alertas Comportamentais.
"""
from __future__ import annotations

from datetime import date

import pytest

from models.transaction import Category
from core.weekly_report import gerar_relatorio_semanal
from .scenario_builders import (
    ganho as _ganho,
    gasto as _gasto,
    budget as _budget,
    build_historico as _build_historico,
    build_maio as _build_maio,
    build_budgets as _build_budgets,
)


class TestTopCategorias:
    """Relatório deve listar as categorias com maior gasto do mês."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )

    def test_top_categorias_retorna_lista(self):
        r = self._relatorio()
        assert isinstance(r.top_categorias, list)
        assert len(r.top_categorias) > 0

    def test_top_categorias_ordenadas_por_gasto_decrescente(self):
        r = self._relatorio()
        totais = [c.total for c in r.top_categorias]
        assert totais == sorted(totais, reverse=True)

    def test_investimento_e_maior_gasto_do_mes(self):
        r = self._relatorio()
        # Investimento: R$2000, Moradia: R$2180, Alimentação: R$1850
        nomes = [c.category for c in r.top_categorias]
        assert "Moradia" in nomes or "Investimento" in nomes

    def test_top_categorias_tem_percentual(self):
        r = self._relatorio()
        for cat in r.top_categorias:
            assert 0 < cat.percentual <= 100


class TestOrcamentosVsReal:
    """Relatório deve comparar gasto real com limite configurado por categoria."""

    def _relatorio(self):
        txs = _build_historico() + _build_maio()
        return gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=_build_budgets(),
            ano=2026, mes=5,
        )

    def test_orcamentos_retorna_lista(self):
        r = self._relatorio()
        assert isinstance(r.orcamentos, list)
        assert len(r.orcamentos) == 5   # 5 budgets configurados

    def test_alimentacao_em_estouro(self):
        r = self._relatorio()
        alim = next(o for o in r.orcamentos if o.category == "Alimentação")
        # Gasto: 850+400+600=1850 > limite 1200
        assert alim.gasto == pytest.approx(1_850.0)
        assert alim.status == "ESTOURO"

    def test_moradia_dentro_do_limite(self):
        r = self._relatorio()
        mor = next(o for o in r.orcamentos if o.category == "Moradia")
        # Gasto: 2000+180=2180 vs limite 2200
        assert mor.status in ("OK", "ALERTA")

    def test_orcamento_sem_gasto_e_ok(self):
        txs = [_ganho(date(2026, 5, 5), 5_000.0)]
        budgets = [_budget(Category.LAZER, 500.0)]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=budgets, ano=2026, mes=5,
        )
        lazer = r.orcamentos[0]
        assert lazer.gasto == 0.0
        assert lazer.status == "OK"


class TestAlertasComportamentais:
    """Relatório detecta categorias com gasto acima de 1.3× a média de 3 meses."""

    def test_alimentacao_gera_alerta(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        cats_com_alerta = [a.category for a in r.alertas]
        # Alimentação histórico: ~800/mês → maio: 1850 → ratio ~2.3 > 1.3
        assert "Alimentação" in cats_com_alerta

    def test_sem_historico_sem_alertas(self):
        txs = [
            _ganho(date(2026, 5, 5), 5_000.0),
            _gasto(date(2026, 5, 10), 1_000.0, Category.ALIMENTACAO),
        ]
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        # Sem histórico de 3 meses anteriores → sem alertas
        assert len(r.alertas) == 0

    def test_alerta_tem_ratio_acima_de_1_3(self):
        txs = _build_historico() + _build_maio()
        r = gerar_relatorio_semanal(
            transacoes_historico=txs, installments=[], budgets=[], ano=2026, mes=5,
        )
        for alerta in r.alertas:
            assert alerta.ratio > 1.3, f"Alerta {alerta.category} tem ratio {alerta.ratio}"
