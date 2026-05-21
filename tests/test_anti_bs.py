from __future__ import annotations

import pytest
from models.investment import Investment, InvestmentType
from core.anti_bs import verificar_alertas, DY_EXCESSIVO_THRESHOLD, LIQUIDEZ_MINIMA


def _inv(**kwargs) -> Investment:
    defaults = dict(
        ticker="TEST11", type=InvestmentType.FII,
        quantity=100, avg_price=10.0, current_price=10.0,
        dy_12m=8.0, pvp=0.90, liquidity_daily=500_000,
    )
    defaults.update(kwargs)
    return Investment(**defaults)


class TestVerificarAlertas:
    def test_ativo_saudavel_sem_alertas(self):
        inv = _inv(dy_12m=9.0, pvp=0.90, liquidity_daily=800_000)
        alertas = verificar_alertas(inv, peso_portfolio_pct=3.0)
        assert alertas == []

    def test_dy_excessivo_dispara_alerta_critical(self):
        inv = _inv(dy_12m=DY_EXCESSIVO_THRESHOLD + 1)
        alertas = verificar_alertas(inv)
        codigos = [a.code for a in alertas]
        assert "ABS_DY_EXCESSIVO" in codigos
        assert any(a.severity == "CRITICAL" for a in alertas if a.code == "ABS_DY_EXCESSIVO")

    def test_desconto_sem_qualidade_pvp_baixo_dy_baixo(self):
        # P/VP < 0.5 com DY < 6% → armadilha clássica
        inv = _inv(pvp=0.40, dy_12m=4.5)
        alertas = verificar_alertas(inv)
        codigos = [a.code for a in alertas]
        assert "ABS_DESCONTO_SEM_QUALIDADE" in codigos

    def test_pvp_baixo_com_dy_bom_nao_dispara_desconto(self):
        # P/VP baixo mas DY adequado → não é armadilha
        inv = _inv(pvp=0.45, dy_12m=10.0)
        alertas = verificar_alertas(inv)
        codigos = [a.code for a in alertas]
        assert "ABS_DESCONTO_SEM_QUALIDADE" not in codigos

    def test_baixa_liquidez_dispara_warning(self):
        inv = _inv(liquidity_daily=LIQUIDEZ_MINIMA - 1)
        alertas = verificar_alertas(inv)
        codigos = [a.code for a in alertas]
        assert "ABS_BAIXA_LIQUIDEZ" in codigos
        assert any(a.severity == "WARNING" for a in alertas if a.code == "ABS_BAIXA_LIQUIDEZ")

    def test_concentracao_alta_dispara_warning(self):
        inv = _inv()
        alertas = verificar_alertas(inv, peso_portfolio_pct=9.0)
        codigos = [a.code for a in alertas]
        assert "ABS_CONCENTRACAO" in codigos

    def test_multiplos_alertas_simultaneos(self):
        # DY excessivo + baixa liquidez + concentração alta
        inv = _inv(dy_12m=20.0, liquidity_daily=50_000)
        alertas = verificar_alertas(inv, peso_portfolio_pct=9.5)
        assert len(alertas) >= 3
