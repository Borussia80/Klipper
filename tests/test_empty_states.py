"""TDD Sprint 09 — k_premium_empty_state() CSS + helper."""
from __future__ import annotations

import pytest


# ── CSS ───────────────────────────────────────────────────────────────────────

class TestEmptyStateCSS:
    def test_class_exists(self):
        from core.styles import KLIPPER_CSS
        assert ".k-empty-state" in KLIPPER_CSS

    def test_has_centered_layout(self):
        from core.styles import KLIPPER_CSS
        idx = KLIPPER_CSS.index(".k-empty-state {")
        snippet = KLIPPER_CSS[idx:idx + 300]
        assert "center" in snippet or "flex" in snippet

    def test_has_icon_class(self):
        from core.styles import KLIPPER_CSS
        assert ".k-empty-state .icon" in KLIPPER_CSS or ".k-empty-icon" in KLIPPER_CSS

    def test_has_title_class(self):
        from core.styles import KLIPPER_CSS
        assert ".k-empty-state .title" in KLIPPER_CSS or ".k-empty-title" in KLIPPER_CSS


# ── Python helper ─────────────────────────────────────────────────────────────

class TestPremiumEmptyStateHelper:
    def test_returns_string(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "Sem transações", "Adicione a primeira")
        assert isinstance(result, str)

    def test_contains_icon(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "Sem transações")
        assert "◎" in result

    def test_contains_title(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "Sem transações")
        assert "Sem transações" in result

    def test_contains_subtitle_when_provided(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "Sem transações", "Adicione a primeira")
        assert "Adicione a primeira" in result

    def test_no_subtitle_when_omitted(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "Sem dados")
        # Should not error and should not add empty subtitle block
        assert result  # not empty

    def test_uses_k_empty_state_class(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "Sem dados")
        assert "k-empty-state" in result

    def test_xss_safe_title(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "<script>alert(1)</script>")
        assert "<script>" not in result

    def test_xss_safe_subtitle(self):
        from core.styles import k_premium_empty_state
        result = k_premium_empty_state("◎", "Título", '<img src=x onerror="alert(1)">')
        # Unescaped < must not appear — it means the tag could execute
        assert "<img" not in result
        assert "&lt;img" in result  # must be escaped, not raw
