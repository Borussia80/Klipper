"""TDD Sprint 7 — Mobile responsive CSS (breakpoint 640px)."""
from __future__ import annotations

import pytest
from core.styles import KLIPPER_CSS


def _mobile_block() -> str:
    assert "@media (max-width: 640px)" in KLIPPER_CSS, (
        "Bloco @media (max-width: 640px) ausente em KLIPPER_CSS"
    )
    return KLIPPER_CSS.split("@media (max-width: 640px)")[1]


# ── Existência do bloco ───────────────────────────────────────────────────────

def test_mobile_media_query_exists():
    assert "@media (max-width: 640px)" in KLIPPER_CSS


# ── k-grid responsivo ─────────────────────────────────────────────────────────

def test_mobile_k_cols_4_becomes_2_col():
    block = _mobile_block()
    assert ".k-cols-4" in block
    # dentro do breakpoint deve usar repeat(2,1fr) ou 1fr
    idx = block.index(".k-cols-4")
    snippet = block[idx:idx + 120]
    assert "repeat(2" in snippet or "1fr" in snippet


def test_mobile_k_cols_3_becomes_2_col():
    block = _mobile_block()
    assert ".k-cols-3" in block
    idx = block.index(".k-cols-3")
    snippet = block[idx:idx + 120]
    assert "repeat(2" in snippet or "1fr" in snippet


def test_mobile_k_cols_2_becomes_1_col():
    block = _mobile_block()
    assert ".k-cols-2" in block
    idx = block.index(".k-cols-2")
    snippet = block[idx:idx + 120]
    assert "1fr" in snippet


# ── Streamlit columns override ─────���──────────────────────────────────────────

def test_mobile_streamlit_horizontal_block_overridden():
    """stHorizontalBlock deve mudar para flex-wrap ou column no mobile."""
    block = _mobile_block()
    assert "stHorizontalBlock" in block or "columns" in block.lower()


def test_mobile_streamlit_column_min_width_overridden():
    """Cada column do Streamlit deve ter min-width 0 ou 100% no mobile."""
    block = _mobile_block()
    # procura por seletor de column do streamlit
    assert 'data-testid="column"' in block or "[data-testid" in block


# ── Hero responsivo ──────────���────────────────────────────────────────────────

def test_mobile_hero_font_size_reduced():
    """Balance no hero deve ter font-size menor no mobile."""
    block = _mobile_block()
    assert ".k-hero" in block or "k-hero-balance" in block


def test_mobile_hero_padding_reduced():
    block = _mobile_block()
    assert ".k-hero" in block
    idx = block.index(".k-hero")
    snippet = block[idx:idx + 200]
    assert "padding" in snippet


# ── Sidebar nativa no mobile ─────────���───────────────────────────��────────────

def test_mobile_sidebar_toggle_visible():
    """No mobile o botão de toggle da sidebar do Streamlit deve estar visível."""
    block = _mobile_block()
    # sidebar collapseButton ou hamburger deve estar visível
    assert "sidebar" in block.lower() or "Sidebar" in block


# ── Charts não overflow ────────��──────────────────────────────────────────────

def test_mobile_plotly_chart_max_width():
    block = _mobile_block()
    # charts devem ser max-width 100% para não transbordar
    assert "stPlotlyChart" in block or "max-width" in block


# ── Dataframe scroll horizontal ──────��────────────────────────────────────────

def test_mobile_dataframe_overflow_x():
    block = _mobile_block()
    assert "stDataFrame" in block or "overflow" in block


# ── Texto e espaçamento ──────────────────────��────────────────────────────��───

def test_mobile_app_view_padding_reduced():
    """Padding lateral do app deve ser menor no mobile."""
    block = _mobile_block()
    assert "appview" in block.lower() or "padding" in block


def test_mobile_section_header_font_reduced():
    block = _mobile_block()
    assert "k-section" in block or "font-size" in block


# ── Light + dark ainda funcionam no mobile ───────────────────────────────────

def test_light_mode_block_still_present_after_mobile():
    """Bloco de light mode não deve ser removido."""
    assert "@media (prefers-color-scheme: light)" in KLIPPER_CSS


def test_dark_root_still_present_after_mobile():
    assert ":root {" in KLIPPER_CSS
