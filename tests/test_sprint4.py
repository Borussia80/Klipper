"""TDD Sprint 4 — light-mode tokens e budget CRUD modal."""
from __future__ import annotations

import pytest
from core.styles import KLIPPER_CSS


class TestLightModeTokens:
    def _light_block(self) -> str:
        assert "@media (prefers-color-scheme: light)" in KLIPPER_CSS
        return KLIPPER_CSS.split("@media (prefers-color-scheme: light)")[1]

    def test_css_has_light_mode_media_query(self):
        assert "@media (prefers-color-scheme: light)" in KLIPPER_CSS

    def test_light_mode_defines_bg(self):
        assert "--bg:" in self._light_block()

    def test_light_mode_defines_ink(self):
        assert "--ink:" in self._light_block()

    def test_light_mode_defines_surface_1(self):
        assert "--surface-1:" in self._light_block()

    def test_light_mode_defines_rule(self):
        assert "--rule:" in self._light_block()

    def test_light_mode_defines_ink_2(self):
        assert "--ink-2:" in self._light_block()

    def test_light_mode_defines_ink_3(self):
        assert "--ink-3:" in self._light_block()

    def test_dark_root_block_still_present(self):
        """dark mode tokens must survive — still the default."""
        assert ":root {" in KLIPPER_CSS
        dark_root = KLIPPER_CSS.split(":root {")[1]
        assert "--bg:" in dark_root
        assert "--ink:" in dark_root

    def test_light_bg_is_light_color(self):
        """Light mode bg should not start with #0 (dark)."""
        block = self._light_block()
        # find --bg: value
        start = block.index("--bg:") + len("--bg:")
        val = block[start:start + 20].strip().split(";")[0].strip()
        assert not val.startswith("#0"), f"Expected light bg, got {val}"

    def test_light_ink_is_dark_color(self):
        """Light mode ink should be a dark color."""
        block = self._light_block()
        start = block.index("--ink:") + len("--ink:")
        val = block[start:start + 20].strip().split(";")[0].strip()
        # dark ink should start with #1 or #2 (near-black)
        assert val.startswith("#1") or val.startswith("#2"), f"Expected dark ink, got {val}"
