"""TDD Sprint 02+03 — Design system: new card hierarchy + mobile bottom nav CSS."""
from __future__ import annotations
import pytest
from core.styles import KLIPPER_CSS


# ── Card hierarchy CSS ────────────────────────────────────────────────────────

class TestCardActionCSS:
    def test_class_exists(self):
        assert ".k-card-action" in KLIPPER_CSS

    def test_has_gradient_background(self):
        idx = KLIPPER_CSS.index(".k-card-action {")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "gradient" in snippet or "electric" in snippet or "3B82F6" in snippet

    def test_has_hover_state(self):
        assert ".k-card-action:hover" in KLIPPER_CSS

    def test_label_child_exists(self):
        assert ".k-card-action .label" in KLIPPER_CSS

    def test_value_child_exists(self):
        assert ".k-card-action .value" in KLIPPER_CSS


class TestCardKpiCSS:
    def test_class_exists(self):
        assert ".k-card-kpi" in KLIPPER_CSS

    def test_has_border(self):
        idx = KLIPPER_CSS.index(".k-card-kpi {")
        snippet = KLIPPER_CSS[idx:idx + 200]
        assert "border" in snippet

    def test_delta_pos_color_green(self):
        assert ".k-card-kpi .delta.pos" in KLIPPER_CSS or "delta.pos" in KLIPPER_CSS

    def test_delta_neg_color_red(self):
        assert ".k-card-kpi .delta.neg" in KLIPPER_CSS or "delta.neg" in KLIPPER_CSS

    def test_value_uses_mono_font(self):
        idx = KLIPPER_CSS.index(".k-card-kpi {")
        block = KLIPPER_CSS[idx:idx + 800]
        assert "font-mono" in block or "JetBrains" in block or "tabular-nums" in block


class TestCardAnalyticsCSS:
    def test_class_exists(self):
        assert ".k-card-analytics" in KLIPPER_CSS

    def test_uses_surface_background(self):
        idx = KLIPPER_CSS.index(".k-card-analytics {")
        snippet = KLIPPER_CSS[idx:idx + 200]
        assert "surface" in snippet or "card" in snippet


class TestCardContextCSS:
    def test_class_exists(self):
        assert ".k-card-context" in KLIPPER_CSS

    def test_has_brass_tint(self):
        idx = KLIPPER_CSS.index(".k-card-context {")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "brass" in snippet or "D9B26F" in snippet or "AE8E59" in snippet

    def test_card_title_uses_brass_color(self):
        idx = KLIPPER_CSS.index(".k-card-context {")
        block = KLIPPER_CSS[idx:idx + 400]
        assert "brass" in block


# ── Bottom nav CSS ────────────────────────────────────────────────────────────

class TestBottomNavCSS:
    def test_class_exists(self):
        assert ".k-bottom-nav" in KLIPPER_CSS

    def test_hidden_by_default(self):
        idx = KLIPPER_CSS.index(".k-bottom-nav {")
        snippet = KLIPPER_CSS[idx:idx + 200]
        assert "display: none" in snippet or "display:none" in snippet

    def test_fixed_position(self):
        idx = KLIPPER_CSS.index(".k-bottom-nav {")
        snippet = KLIPPER_CSS[idx:idx + 200]
        assert "position: fixed" in snippet or "position:fixed" in snippet

    def test_z_index_high(self):
        idx = KLIPPER_CSS.index(".k-bottom-nav {")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "z-index" in snippet
        zi = [s for s in snippet.split() if "z-index" in s or s.isdigit()]
        assert any("999" in s for s in snippet.split(";") if "z-index" in s)

    def test_displayed_in_mobile_block(self):
        mobile_block = KLIPPER_CSS.split("@media (max-width: 640px)")[1]
        assert ".k-bottom-nav" in mobile_block
        idx = mobile_block.index(".k-bottom-nav")
        snippet = mobile_block[idx:idx + 80]
        assert "grid" in snippet or "display" in snippet

    def test_has_backdrop_filter(self):
        idx = KLIPPER_CSS.index(".k-bottom-nav {")
        snippet = KLIPPER_CSS[idx:idx + 400]
        assert "backdrop-filter" in snippet

    def test_item_min_height_44(self):
        assert ".k-bnav-item" in KLIPPER_CSS or "k-bottom-nav a" in KLIPPER_CSS
        idx = KLIPPER_CSS.index(".k-bottom-nav a")
        snippet = KLIPPER_CSS[idx:idx + 500]
        assert "44px" in snippet or "min-height" in snippet


# ── FAB CSS ───────────────────────────────────────────────────────────────────

class TestFabCSS:
    def test_class_exists(self):
        assert ".k-fab" in KLIPPER_CSS

    def test_hidden_by_default(self):
        idx = KLIPPER_CSS.index(".k-fab {")
        snippet = KLIPPER_CSS[idx:idx + 200]
        assert "display: none" in snippet or "display:none" in snippet

    def test_fixed_position(self):
        idx = KLIPPER_CSS.index(".k-fab {")
        snippet = KLIPPER_CSS[idx:idx + 200]
        assert "position: fixed" in snippet or "position:fixed" in snippet

    def test_has_shadow(self):
        idx = KLIPPER_CSS.index(".k-fab {")
        snippet = KLIPPER_CSS[idx:idx + 400]
        assert "box-shadow" in snippet

    def test_displayed_in_mobile_block(self):
        mobile_block = KLIPPER_CSS.split("@media (max-width: 640px)")[1]
        assert ".k-fab" in mobile_block
        idx = mobile_block.index(".k-fab")
        snippet = mobile_block[idx:idx + 60]
        assert "flex" in snippet or "display" in snippet

    def test_hover_scales_up(self):
        assert ".k-fab:hover" in KLIPPER_CSS


# ── Segmented control CSS ─────────────────────────────────────────────────────

class TestSegCtrlCSS:
    def test_class_exists(self):
        assert ".k-seg-ctrl" in KLIPPER_CSS

    def test_active_segment_has_background(self):
        assert ".k-seg-ctrl .seg.active" in KLIPPER_CSS

    def test_has_border_radius(self):
        idx = KLIPPER_CSS.index(".k-seg-ctrl {")
        snippet = KLIPPER_CSS[idx:idx + 200]
        assert "border-radius" in snippet


# ── Bottom sheet CSS ──────────────────────────────────────────────────────────

class TestBottomSheetCSS:
    def test_class_exists(self):
        assert ".k-bottom-sheet" in KLIPPER_CSS

    def test_fixed_position(self):
        idx = KLIPPER_CSS.index(".k-bottom-sheet {")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "fixed" in snippet

    def test_has_top_border_radius(self):
        idx = KLIPPER_CSS.index(".k-bottom-sheet {")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "border-radius" in snippet

    def test_handle_exists(self):
        assert ".k-bottom-sheet .handle" in KLIPPER_CSS


# ── Python helpers ────────────────────────────────────────────────────────────

class TestKpiCardHelper:
    def test_returns_string(self):
        from core.styles import kpi_card
        result = kpi_card("Saldo", "R$ 1.000", "▲ 5%", "pos")
        assert isinstance(result, str)

    def test_contains_label(self):
        from core.styles import kpi_card
        result = kpi_card("Saldo", "R$ 1.000")
        assert "Saldo" in result

    def test_contains_value(self):
        from core.styles import kpi_card
        result = kpi_card("Saldo", "R$ 1.000")
        assert "R$ 1.000" in result

    def test_delta_html_present_when_provided(self):
        from core.styles import kpi_card
        result = kpi_card("Saldo", "R$ 1.000", delta="▲ 5%", tone="pos")
        assert "▲ 5%" in result
        assert "pos" in result

    def test_no_delta_html_when_empty(self):
        from core.styles import kpi_card
        result = kpi_card("Saldo", "R$ 1.000")
        assert 'class="delta' not in result

    def test_uses_k_card_kpi_class(self):
        from core.styles import kpi_card
        result = kpi_card("Saldo", "R$ 1.000")
        assert "k-card-kpi" in result


class TestActionCardHelper:
    def test_returns_string(self):
        from core.styles import action_card
        result = action_card("Caixa", "R$ 5.000", "sem pendências")
        assert isinstance(result, str)

    def test_contains_label(self):
        from core.styles import action_card
        result = action_card("Caixa", "R$ 5.000")
        assert "Caixa" in result

    def test_contains_value(self):
        from core.styles import action_card
        result = action_card("Caixa", "R$ 5.000")
        assert "R$ 5.000" in result

    def test_uses_k_card_action_class(self):
        from core.styles import action_card
        result = action_card("Caixa", "R$ 5.000")
        assert "k-card-action" in result

    def test_sub_present_when_provided(self):
        from core.styles import action_card
        result = action_card("Caixa", "R$ 5.000", sub="sem pendências")
        assert "sem pendências" in result


class TestContextCardHelper:
    def test_returns_string(self):
        from core.styles import context_card
        result = context_card("WikiAgent", "<p>engines</p>")
        assert isinstance(result, str)

    def test_contains_title(self):
        from core.styles import context_card
        result = context_card("WikiAgent", "<p>engines</p>")
        assert "WikiAgent" in result

    def test_contains_body(self):
        from core.styles import context_card
        result = context_card("WikiAgent", "<p>engines</p>")
        assert "<p>engines</p>" in result

    def test_uses_k_card_context_class(self):
        from core.styles import context_card
        result = context_card("WikiAgent", "<p>engines</p>")
        assert "k-card-context" in result

    def test_hint_present_when_provided(self):
        from core.styles import context_card
        result = context_card("WikiAgent", "<p>engines</p>", hint="v2.0")
        assert "v2.0" in result
