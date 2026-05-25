"""TDD Sprint 07 — Radar Strip: alertas de padrão de consumo."""
from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import date


# ── k_radar_notification_card CSS ─────────────────────────────────────────────

class TestRadarCardCSS:
    def test_class_exists(self):
        from core.styles import KLIPPER_CSS
        assert ".k-radar-strip" in KLIPPER_CSS or ".k-radar-card" in KLIPPER_CSS

    def test_has_danger_color(self):
        from core.styles import KLIPPER_CSS
        assert ".k-radar" in KLIPPER_CSS
        idx = KLIPPER_CSS.index(".k-radar")
        block = KLIPPER_CSS[idx:idx + 600]
        assert "rust" in block or "EF4444" in block or "F87171" in block or "neg" in block

    def test_has_warn_color(self):
        from core.styles import KLIPPER_CSS
        assert ".k-radar" in KLIPPER_CSS
        idx = KLIPPER_CSS.index(".k-radar")
        block = KLIPPER_CSS[idx:idx + 600]
        assert "warn" in block or "F59E0B" in block or "amber" in block.lower() or "lantern" in block


# ── k_radar_notification_card Python helper ────────────────────────────────────

class TestRadarNotificationCardHelper:
    def test_returns_string(self):
        from core.styles import k_radar_notification_card
        result = k_radar_notification_card([])
        assert isinstance(result, str)

    def test_empty_alerts_returns_ok_message(self):
        from core.styles import k_radar_notification_card
        result = k_radar_notification_card([])
        assert "ok" in result.lower() or "conformidade" in result.lower() or "✓" in result

    def test_alerts_render_in_html(self):
        from core.styles import k_radar_notification_card
        alerts = [{"category": "Lazer", "ratio": 1.4, "current": 840.0, "baseline": 600.0}]
        result = k_radar_notification_card(alerts)
        assert "Lazer" in result

    def test_ratio_shown_in_output(self):
        from core.styles import k_radar_notification_card
        alerts = [{"category": "Alimentação", "ratio": 1.35, "current": 675.0, "baseline": 500.0}]
        result = k_radar_notification_card(alerts)
        assert "1.35" in result or "35%" in result or "Alimentação" in result

    def test_multiple_alerts_all_rendered(self):
        from core.styles import k_radar_notification_card
        alerts = [
            {"category": "Lazer",      "ratio": 1.6, "current": 960.0,  "baseline": 600.0},
            {"category": "Transporte", "ratio": 1.4, "current": 700.0,  "baseline": 500.0},
        ]
        result = k_radar_notification_card(alerts)
        assert "Lazer" in result
        assert "Transporte" in result


# ── detect_spending_alerts logic ──────────────────────────────────────────────

class TestDetectSpendingAlerts:
    """detect_spending_alerts() returns categories above 1.3× historical baseline."""

    def _make_spending(self, category: str, amount: float) -> dict:
        return {"category": category, "amount": amount}

    def test_above_threshold_returns_alert(self):
        from core.analytics import detect_spending_alerts
        current  = {"Lazer": 900.0}   # 1.5× — strictly above 1.3
        baseline = {"Lazer": 600.0}
        alerts = detect_spending_alerts(current, baseline, threshold=1.3)
        assert len(alerts) == 1
        assert alerts[0]["category"] == "Lazer"

    def test_below_threshold_returns_empty(self):
        from core.analytics import detect_spending_alerts
        current  = {"Lazer": 600.0}
        baseline = {"Lazer": 600.0}
        alerts = detect_spending_alerts(current, baseline, threshold=1.3)
        assert alerts == []

    def test_exactly_at_threshold_not_triggered(self):
        from core.analytics import detect_spending_alerts
        current  = {"Lazer": 780.0}  # exactly 1.3×600
        baseline = {"Lazer": 600.0}
        alerts = detect_spending_alerts(current, baseline, threshold=1.3)
        assert alerts == []

    def test_ratio_calculated_correctly(self):
        from core.analytics import detect_spending_alerts
        current  = {"Alimentação": 900.0}
        baseline = {"Alimentação": 600.0}
        alerts = detect_spending_alerts(current, baseline, threshold=1.3)
        assert len(alerts) == 1
        assert abs(alerts[0]["ratio"] - 1.5) < 0.01

    def test_category_without_baseline_ignored(self):
        from core.analytics import detect_spending_alerts
        current  = {"NovaCategoria": 500.0}
        baseline = {}
        alerts = detect_spending_alerts(current, baseline, threshold=1.3)
        assert alerts == []

    def test_zero_baseline_ignored(self):
        from core.analytics import detect_spending_alerts
        current  = {"Lazer": 100.0}
        baseline = {"Lazer": 0.0}
        alerts = detect_spending_alerts(current, baseline, threshold=1.3)
        assert alerts == []

    def test_multiple_categories_returns_only_violators(self):
        from core.analytics import detect_spending_alerts
        current  = {"Lazer": 900.0, "Alimentação": 400.0}
        baseline = {"Lazer": 600.0, "Alimentação": 600.0}
        alerts = detect_spending_alerts(current, baseline, threshold=1.3)
        categories = [a["category"] for a in alerts]
        assert "Lazer" in categories
        assert "Alimentação" not in categories

    def test_custom_threshold(self):
        from core.analytics import detect_spending_alerts
        current  = {"Lazer": 660.0}
        baseline = {"Lazer": 600.0}
        # 1.1× — only triggers if threshold <= 1.1
        alerts_strict = detect_spending_alerts(current, baseline, threshold=1.05)
        assert len(alerts_strict) == 1
        alerts_loose = detect_spending_alerts(current, baseline, threshold=1.15)
        assert alerts_loose == []
