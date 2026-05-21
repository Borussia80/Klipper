"""
Testes de integração — sinergia completa entre M1/M2/M3/Anti-BS/Fragility.

Cada cenário testa o pipeline WikiAgent ponta a ponta:
  M1 (score) → M3 (ajuste contexto) → Fragility (redução) → Decisão → Anti-BS → M2

Princípio validado: "Matemática ancora. Contexto modula risco."
"""
from __future__ import annotations

import pytest
from models.investment import Investment, InvestmentType
from core.m1_quant import calcular_score_m1, classificar_score, Decisao
from core.m2_governance import verificar_limites, hard_fail
from core.m3_context import MarketRegime, Confidence, ajustar_prudencia
from core.anti_bs import verificar_alertas
from core.fragility import calcular_fragility_score, reduzir_exposicao_por_fragilidade


def _pipeline(
    inv: Investment,
    regime: MarketRegime,
    confidence: Confidence,
    peso_pct: float = 5.0,
) -> tuple[float, float, float, Decisao]:
    """Executa pipeline completo: retorna (score_m1, score_m3, score_final, decisao)."""
    score_m1 = calcular_score_m1(
        dy=inv.dy_12m, pvp=inv.pvp, liquidez=inv.liquidity_daily,
        volatilidade=inv.volatility, spread_cdi=inv.spread_vs_cdi,
    )
    score_m3 = ajustar_prudencia(score_m1, regime, confidence)
    frag = calcular_fragility_score(inv, peso_portfolio_pct=peso_pct)
    score_final = reduzir_exposicao_por_fragilidade(score_m3, frag.total)
    decisao = classificar_score(score_final)
    return score_m1, score_m3, score_final, decisao


def _fii(ticker="TEST11", **kwargs) -> Investment:
    defaults = dict(
        type=InvestmentType.FII, quantity=100,
        avg_price=10.0, current_price=10.0,
        dy_12m=10.0, pvp=0.90, liquidity_daily=500_000,
        volatility=10.0, spread_vs_cdi=2.0, sector="Papel",
    )
    defaults.update(kwargs)
    return Investment(ticker=ticker, **defaults)


class TestPipelineCompleto:

    def test_ativo_excelente_em_risk_on_recomenda_comprar(self):
        """FII com todos os fundamentos fortes em regime favorável → COMPRAR."""
        inv = _fii(dy_12m=13.0, pvp=0.75, liquidity_daily=2_000_000,
                   volatility=5.0, spread_vs_cdi=4.0)
        _, _, score_final, decisao = _pipeline(inv, MarketRegime.RISK_ON, Confidence.HIGH)
        assert decisao == Decisao.COMPRAR
        assert score_final >= 0.60

    def test_ativo_fraco_recomenda_reduzir(self):
        """FII com fundamentos ruins → REDUZIR independente do regime."""
        inv = _fii(dy_12m=2.0, pvp=1.5, liquidity_daily=20_000,
                   volatility=35.0, spread_vs_cdi=-2.0)
        _, _, score_final, decisao = _pipeline(inv, MarketRegime.RISK_ON, Confidence.HIGH)
        assert decisao == Decisao.REDUZIR
        assert score_final < 0.30

    def test_contexto_rebaixa_comprar_para_manter(self):
        """M1 diz COMPRAR mas crise de liquidez rebaixa para MANTER."""
        inv = _fii(dy_12m=12.0, pvp=0.80, liquidity_daily=1_000_000,
                   volatility=8.0, spread_vs_cdi=3.0)
        _, score_m1, _, _ = _pipeline(inv, MarketRegime.RISK_ON, Confidence.HIGH)
        _, _, score_crise, decisao_crise = _pipeline(
            inv, MarketRegime.LIQUIDITY_CRISIS, Confidence.LOW
        )
        # score M1 base era COMPRAR, crise rebaixa
        assert score_crise < score_m1
        assert classificar_score(score_m1) == Decisao.COMPRAR
        # em crise severa com confidence LOW, score final pode cair para MANTER
        assert decisao_crise in (Decisao.MANTER, Decisao.REDUZIR)

    def test_contexto_nunca_eleva_score(self):
        """Nenhum regime pode elevar o score M1 — só reduz ou mantém."""
        inv = _fii(dy_12m=10.0, pvp=0.88)
        score_m1 = calcular_score_m1(inv.dy_12m, inv.pvp, inv.liquidity_daily,
                                     inv.volatility, inv.spread_vs_cdi)
        for regime in MarketRegime:
            for conf in Confidence:
                ajustado = ajustar_prudencia(score_m1, regime, conf)
                assert ajustado <= score_m1, f"Score elevado em {regime}/{conf}"

    def test_fragilidade_alta_rebaixa_mesmo_com_m1_bom(self):
        """M1 forte mas fragilidade alta → decisão mais conservadora."""
        inv = _fii(dy_12m=13.0, pvp=0.70, liquidity_daily=50_000,  # ilíquido
                   volatility=5.0, spread_vs_cdi=4.0)
        score_m1 = calcular_score_m1(inv.dy_12m, inv.pvp, inv.liquidity_daily,
                                     inv.volatility, inv.spread_vs_cdi)
        frag = calcular_fragility_score(inv, peso_portfolio_pct=9.0,
                                        governanca=0.8, dependencia_credito=0.9)
        score_final = reduzir_exposicao_por_fragilidade(score_m1, frag.total)
        assert score_final < score_m1
        assert frag.total > 0.5  # confirma fragilidade alta

    def test_anti_bs_independente_do_score_m1(self):
        """Anti-BS detecta armadilha mesmo quando score M1 parece ok."""
        # DY alto infla score M1, mas Anti-BS sinaliza risco
        inv = _fii(dy_12m=18.0, pvp=0.90, liquidity_daily=500_000)
        score_m1 = calcular_score_m1(inv.dy_12m, inv.pvp, inv.liquidity_daily,
                                     inv.volatility, inv.spread_vs_cdi)
        alertas = verificar_alertas(inv)
        # M1 pode dizer COMPRAR (DY alto infla score)
        assert classificar_score(score_m1) == Decisao.COMPRAR
        # mas Anti-BS deve alertar sobre DY excessivo
        assert any(a.code == "ABS_DY_EXCESSIVO" for a in alertas)

    def test_m2_bloqueia_mesmo_com_score_excelente(self):
        """M2 hard fail bloqueia entrada independente do score M1."""
        inv = _fii(ticker="MXRF11", dy_12m=13.0, pvp=0.70,
                   liquidity_daily=2_000_000, volatility=5.0, spread_vs_cdi=4.0)
        _, _, _, decisao = _pipeline(inv, MarketRegime.RISK_ON, Confidence.HIGH)
        assert decisao == Decisao.COMPRAR  # M1 diz comprar

        # Portfolio 100% concentrado em um ativo → M2 hard fail
        alertas = verificar_limites([inv], caixa_disponivel=0)
        falhou, motivo = hard_fail(alertas)
        assert falhou  # mesmo com COMPRAR no M1, M2 bloqueia
        assert len(motivo) > 0

    def test_euphoria_aumenta_cautela_mesmo_sem_mudar_decisao(self):
        """Em EUPHORIA, mesmo com RISK_ON os scores são penalizados."""
        inv = _fii(dy_12m=12.0, pvp=0.82, liquidity_daily=1_200_000,
                   volatility=7.0, spread_vs_cdi=3.0)
        score_m1 = calcular_score_m1(inv.dy_12m, inv.pvp, inv.liquidity_daily,
                                     inv.volatility, inv.spread_vs_cdi)
        score_risk_on = ajustar_prudencia(score_m1, MarketRegime.RISK_ON, Confidence.HIGH)
        score_euphoria = ajustar_prudencia(score_m1, MarketRegime.EUPHORIA, Confidence.HIGH)
        # EUPHORIA penaliza mais que RISK_ON
        assert score_euphoria < score_risk_on

    def test_pipeline_ordem_de_reducao_correta(self):
        """Score só pode decrescer ao longo do pipeline: M1 ≥ M3 ≥ Final."""
        inv = _fii(dy_12m=11.0, pvp=0.85, liquidity_daily=600_000,
                   volatility=12.0, spread_vs_cdi=2.5)
        score_m1, score_m3, score_final, _ = _pipeline(
            inv, MarketRegime.CREDIT_STRESS, Confidence.LOW, peso_pct=7.0
        )
        assert score_m1 >= score_m3 >= score_final >= 0.0
