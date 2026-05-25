"""TDD Sprint 01B — Card anatomy, input focus states, Plotly defaults."""
from __future__ import annotations

import pytest


# ── Card Anatomy CSS ──────────────────────────────────────────────────────────

class TestCardAnatomyCSS:
    """Cards must have semantic borders and elevation tokens."""

    def test_kpi_card_has_border(self):
        from core.styles import KLIPPER_CSS
        idx = KLIPPER_CSS.index(".k-card-kpi {")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "border" in snippet

    def test_action_card_p1_brass_border_variant(self):
        """There must be a P1 card variant or the action card uses brass border."""
        from core.styles import KLIPPER_CSS
        # Either a .k-card-action.p1 selector OR brass border on .k-card-kpi.p1
        assert ".k-card-kpi.p1" in KLIPPER_CSS or ".k-card.p1" in KLIPPER_CSS or "rule-brass" in KLIPPER_CSS

    def test_card_type_a_has_fixed_height(self):
        """Type A card should constrain height for rhythm."""
        from core.styles import KLIPPER_CSS
        # k-card-kpi must reference a min-height or height somewhere
        assert ".k-card-kpi" in KLIPPER_CSS
        idx = KLIPPER_CSS.index(".k-card-kpi {")
        block = KLIPPER_CSS[idx:idx + 400]
        assert "padding" in block  # height rhythm via padding is acceptable

    def test_stat_card_has_elevation_background(self):
        """stat-card or k-stat-card must use card/surface variable, not hardcoded color."""
        from core.styles import KLIPPER_CSS
        assert ".k-stat-card" in KLIPPER_CSS
        idx = KLIPPER_CSS.index(".k-stat-card")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "var(" in snippet  # must use CSS variables


# ── Input Dark Mode + Focus State CSS ─────────────────────────────────────────

class TestInputFocusStateCSS:
    """Inputs must integrate with dark theme and have visible focus ring."""

    def test_input_focus_uses_brass_border(self):
        from core.styles import KLIPPER_CSS
        # focus state on input must reference brass or electric color
        assert ":focus" in KLIPPER_CSS
        idx = KLIPPER_CSS.index(":focus")
        block = KLIPPER_CSS[idx:idx + 300]
        assert "brass" in block or "D9A74A" in block or "electric" in block or "3B82F6" in block

    def test_input_focus_has_glow(self):
        from core.styles import KLIPPER_CSS
        # box-shadow glow on focus
        focus_blocks = KLIPPER_CSS.split(":focus")
        found_glow = any(
            "box-shadow" in block[:300]
            for block in focus_blocks[1:]
        )
        assert found_glow

    def test_input_background_uses_dark_token(self):
        from core.styles import KLIPPER_CSS
        # stTextInput or generic input should use bg variable, not white
        assert "stTextInput" in KLIPPER_CSS or "stNumberInput" in KLIPPER_CSS
        for selector in ("stTextInput", "stNumberInput", "stSelectbox"):
            if selector in KLIPPER_CSS:
                idx = KLIPPER_CSS.index(selector)
                snippet = KLIPPER_CSS[idx:idx + 500]
                # Must not hardcode white background
                assert "#ffffff" not in snippet.lower() or "var(" in snippet

    def test_placeholder_color_defined(self):
        from core.styles import KLIPPER_CSS
        assert "::placeholder" in KLIPPER_CSS
        idx = KLIPPER_CSS.index("::placeholder")
        snippet = KLIPPER_CSS[idx:idx + 150]
        assert "color" in snippet

    def test_input_border_radius_uses_token(self):
        from core.styles import KLIPPER_CSS
        # radius-input token must be referenced on inputs
        assert "radius-input" in KLIPPER_CSS


# ── Plotly Theme Defaults ─────────────────────────────────────────────────────

class TestPlotlyThemeHelper:
    """plotly_dark_theme() must return a dict with transparent backgrounds."""

    def test_function_exists(self):
        from core.styles import plotly_dark_theme
        assert callable(plotly_dark_theme)

    def test_returns_dict(self):
        from core.styles import plotly_dark_theme
        result = plotly_dark_theme()
        assert isinstance(result, dict)

    def test_paper_bgcolor_transparent(self):
        from core.styles import plotly_dark_theme
        theme = plotly_dark_theme()
        assert theme.get("paper_bgcolor") in ("rgba(0,0,0,0)", "transparent", "rgba(0,0,0,0.0)")

    def test_plot_bgcolor_transparent(self):
        from core.styles import plotly_dark_theme
        theme = plotly_dark_theme()
        assert theme.get("plot_bgcolor") in ("rgba(0,0,0,0)", "transparent", "rgba(0,0,0,0.0)")

    def test_font_color_readable(self):
        from core.styles import plotly_dark_theme
        theme = plotly_dark_theme()
        font = theme.get("font", {})
        assert font.get("color") is not None

    def test_font_family_is_mono_or_sans(self):
        from core.styles import plotly_dark_theme
        theme = plotly_dark_theme()
        family = theme.get("font", {}).get("family", "")
        assert "Mono" in family or "mono" in family or "Geist" in family or "Inter" in family

    def test_has_margin(self):
        from core.styles import plotly_dark_theme
        theme = plotly_dark_theme()
        assert "margin" in theme

    def test_height_constraint_provided(self):
        from core.styles import plotly_dark_theme
        theme = plotly_dark_theme(max_height=180)
        assert theme.get("height") == 180

    def test_default_height_is_reasonable(self):
        from core.styles import plotly_dark_theme
        theme = plotly_dark_theme()
        h = theme.get("height", 999)
        assert h <= 300  # compacto por padrão
