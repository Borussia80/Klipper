"""TDD tests — novos componentes de layout: hero_section, tx_row, setup_sidebar."""
from __future__ import annotations

import pytest


# ── hero_section ───────────────────────────────────────────────────────────────

def test_hero_section_returns_string():
    from core.styles import hero_section
    result = hero_section("Dashboard", "R$ 1.000,00", "R$ 500,00", "R$ 500,00")
    assert isinstance(result, str) and len(result) > 0


def test_hero_section_contains_title():
    from core.styles import hero_section
    result = hero_section("Dashboard", "R$ 1.000,00", "R$ 500,00", "R$ 500,00")
    assert "Dashboard" in result


def test_hero_section_contains_saldo():
    from core.styles import hero_section
    result = hero_section("Mês Atual", "R$ 9.999,00", "R$ 4.000,00", "R$ 1.500,00")
    assert "9.999,00" in result


def test_hero_section_contains_ganhos():
    from core.styles import hero_section
    result = hero_section("Mês Atual", "R$ 3.000,00", "R$ 4.000,00", "R$ 1.500,00")
    assert "4.000,00" in result


def test_hero_section_contains_gastos():
    from core.styles import hero_section
    result = hero_section("Mês Atual", "R$ 3.000,00", "R$ 4.000,00", "R$ 1.500,00")
    assert "1.500,00" in result


def test_hero_section_has_hero_class():
    from core.styles import hero_section
    result = hero_section("Dashboard", "R$ 1.000,00", "R$ 500,00", "R$ 500,00")
    assert "k-hero" in result


def test_hero_section_subtitle_included_when_provided():
    from core.styles import hero_section
    result = hero_section("Dashboard", "R$ 1.000,00", "R$ 500,00", "R$ 500,00",
                          subtitle="maio · 2026")
    assert "maio · 2026" in result


def test_hero_section_no_subtitle_by_default():
    from core.styles import hero_section
    # deve funcionar sem subtitle (parâmetro opcional)
    result = hero_section("Dashboard", "R$ 0,00", "R$ 0,00", "R$ 0,00")
    assert "k-hero" in result


def test_hero_section_is_html():
    from core.styles import hero_section
    result = hero_section("Dashboard", "R$ 1.000,00", "R$ 500,00", "R$ 500,00")
    assert "<div" in result and "</div>" in result


# ── tx_row ─────────────────────────────────────────────────────────────────────

def test_tx_row_returns_string():
    from core.styles import tx_row
    result = tx_row("Alimentação", "Restaurante", "23/Mai", "Almoço", "-R$ 45,00", "neg")
    assert isinstance(result, str) and len(result) > 0


def test_tx_row_is_html():
    from core.styles import tx_row
    result = tx_row("Alimentação", "Restaurante", "23/Mai", "Almoço", "-R$ 45,00", "neg")
    assert "<div" in result and "</div>" in result


def test_tx_row_has_row_class():
    from core.styles import tx_row
    result = tx_row("Alimentação", "Restaurante", "23/Mai", "Almoço", "-R$ 45,00", "neg")
    assert "k-tx-row" in result


def test_tx_row_contains_name():
    from core.styles import tx_row
    result = tx_row("Alimentação", "Restaurante Xpto", "23/Mai", "Almoço", "-R$ 45,00", "neg")
    assert "Restaurante Xpto" in result


def test_tx_row_contains_amount():
    from core.styles import tx_row
    result = tx_row("Salário", "Empresa SA", "01/Mai", "Renda", "+R$ 8.000,00", "pos")
    assert "8.000,00" in result


def test_tx_row_contains_date():
    from core.styles import tx_row
    result = tx_row("Alimentação", "Loja", "15/Jun", "Compras", "-R$ 99,00", "neg")
    assert "15/Jun" in result


def test_tx_row_contains_category():
    from core.styles import tx_row
    result = tx_row("Transporte", "Uber", "10/Mai", "Mobilidade", "-R$ 25,00", "neg")
    # nome da categoria ou inicial aparecem
    assert "Transporte" in result or "T" in result


def test_tx_row_neg_tone_applied():
    from core.styles import tx_row
    result = tx_row("Alimentação", "Restaurante", "23/Mai", "Almoço", "-R$ 45,00", "neg")
    assert "neg" in result


def test_tx_row_pos_tone_applied():
    from core.styles import tx_row
    result = tx_row("Salário", "Empresa", "01/Mai", "Renda", "+R$ 5.000,00", "pos")
    assert "pos" in result


def test_tx_row_notes_shown_when_provided():
    from core.styles import tx_row
    result = tx_row("Alimentação", "Restaurante", "23/Mai", "Almoço", "-R$ 45,00", "neg",
                    notes="Almoço de negócios")
    assert "Almoço de negócios" in result


def test_tx_row_works_without_notes():
    from core.styles import tx_row
    # notes é opcional — não deve lançar exceção
    result = tx_row("Saúde", "Farmácia", "05/Mai", "Saúde", "-R$ 30,00", "neg")
    assert "k-tx-row" in result


# ── setup_sidebar ──────────────────────────────────────────────────────────────

def test_setup_sidebar_is_callable():
    from core.styles import setup_sidebar
    assert callable(setup_sidebar)


def test_setup_sidebar_accepts_ctx_kwarg():
    """setup_sidebar deve aceitar ctx sem lançar TypeError."""
    import inspect
    from core.styles import setup_sidebar
    sig = inspect.signature(setup_sidebar)
    assert "ctx" in sig.parameters


def test_setup_sidebar_accepts_violations_kwarg():
    import inspect
    from core.styles import setup_sidebar
    sig = inspect.signature(setup_sidebar)
    assert "violations" in sig.parameters


def test_setup_sidebar_accepts_include_ai_qa_kwarg():
    import inspect
    from core.styles import setup_sidebar
    sig = inspect.signature(setup_sidebar)
    assert "include_ai_qa" in sig.parameters
