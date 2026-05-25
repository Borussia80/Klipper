"""TDD Sprint 08 — Consilium chat interface: core/consilium.py."""
from __future__ import annotations

import pytest


# ── confidence_to_pct ─────────────────────────────────────────────────────────

class TestConfidenceToPct:
    """confidence_to_pct(confidence_str) → int 0–100 para o gauge."""

    def _fn(self, s):
        from core.consilium import confidence_to_pct
        return confidence_to_pct(s)

    def test_very_low(self):
        assert self._fn("VERY_LOW") == 20

    def test_low(self):
        assert self._fn("LOW") == 40

    def test_moderate(self):
        assert self._fn("MODERATE") == 60

    def test_high(self):
        assert self._fn("HIGH") == 80

    def test_critical(self):
        assert self._fn("CRITICAL") == 100

    def test_unknown_returns_50(self):
        assert self._fn("DESCONHECIDO") == 50

    def test_case_insensitive(self):
        assert self._fn("moderate") == 60

    def test_returns_int(self):
        assert isinstance(self._fn("HIGH"), int)


# ── resolve_provider ──────────────────────────────────────────────────────────

class TestResolveProvider:
    """resolve_provider(key, env) → model string; env é dict de variáveis."""

    def _fn(self, key, env=None):
        from core.consilium import resolve_provider
        return resolve_provider(key, env or {})

    def test_auto_picks_claude_when_anthropic_set(self):
        result = self._fn("auto", {"ANTHROPIC_API_KEY": "sk-abc"})
        assert result == "claude-sonnet-4-6"

    def test_auto_skips_to_gemini_when_only_google_set(self):
        result = self._fn("auto", {"GOOGLE_API_KEY": "gk-abc"})
        assert result == "gemini/gemini-2.0-flash"

    def test_auto_skips_to_gpt_when_only_openai_set(self):
        result = self._fn("auto", {"OPENAI_API_KEY": "oai-abc"})
        assert result == "gpt-4o"

    def test_auto_no_key_falls_back_to_gemini(self):
        result = self._fn("auto", {})
        assert result == "gemini/gemini-2.0-flash"

    def test_explicit_claude(self):
        assert self._fn("claude") == "claude-sonnet-4-6"

    def test_explicit_gemini(self):
        assert self._fn("gemini") == "gemini/gemini-2.0-flash"

    def test_explicit_gpt4o(self):
        assert self._fn("gpt4o") == "gpt-4o"

    def test_explicit_qwen(self):
        assert self._fn("qwen") == "openai/qwen-plus"

    def test_explicit_kimi(self):
        assert self._fn("kimi") == "openai/moonshot-v1-8k"

    def test_unknown_falls_back_to_claude(self):
        assert self._fn("inexistente") == "claude-sonnet-4-6"


# ── build_system_prompt ───────────────────────────────────────────────────────

class TestBuildSystemPrompt:
    def test_returns_string(self):
        from core.consilium import build_system_prompt
        assert isinstance(build_system_prompt(), str)

    def test_contains_m1_threshold(self):
        from core.consilium import build_system_prompt
        prompt = build_system_prompt()
        assert "M1" in prompt or "WikiAgent" in prompt

    def test_contains_anti_bs_rule(self):
        from core.consilium import build_system_prompt
        prompt = build_system_prompt()
        assert "Matemática" in prompt or "narrativa" in prompt.lower() or "evidência" in prompt.lower()

    def test_under_2000_chars(self):
        from core.consilium import build_system_prompt
        assert len(build_system_prompt()) < 2000

    def test_m2_limits_mentioned(self):
        from core.consilium import build_system_prompt
        prompt = build_system_prompt()
        assert "10%" in prompt or "M2" in prompt


# ── ConsiliumMessage ──────────────────────────────────────────────────────────

class TestConsiliumMessage:
    def test_user_role(self):
        from core.consilium import ConsiliumMessage
        m = ConsiliumMessage(role="user", content="olá")
        assert m.role == "user"
        assert m.content == "olá"

    def test_assistant_role(self):
        from core.consilium import ConsiliumMessage
        m = ConsiliumMessage(role="assistant", content="resposta")
        assert m.role == "assistant"

    def test_model_default_none(self):
        from core.consilium import ConsiliumMessage
        m = ConsiliumMessage(role="user", content="x")
        assert m.model is None

    def test_model_can_be_set(self):
        from core.consilium import ConsiliumMessage
        m = ConsiliumMessage(role="assistant", content="x", model="claude-sonnet-4-6")
        assert m.model == "claude-sonnet-4-6"


# ── chat_history_to_messages ──────────────────────────────────────────────────

class TestChatHistoryToMessages:
    """Converte lista de ConsiliumMessage para formato LiteLLM [{role, content}]."""

    def _msg(self, role, content, model=None):
        from core.consilium import ConsiliumMessage
        return ConsiliumMessage(role=role, content=content, model=model)

    def _fn(self, history):
        from core.consilium import chat_history_to_messages
        return chat_history_to_messages(history)

    def test_empty_history_returns_empty(self):
        assert self._fn([]) == []

    def test_single_user_message(self):
        result = self._fn([self._msg("user", "pergunta")])
        assert result == [{"role": "user", "content": "pergunta"}]

    def test_multi_turn(self):
        history = [
            self._msg("user", "q1"),
            self._msg("assistant", "a1", model="claude-sonnet-4-6"),
        ]
        result = self._fn(history)
        assert len(result) == 2
        assert result[0] == {"role": "user", "content": "q1"}
        assert result[1] == {"role": "assistant", "content": "a1"}

    def test_model_not_in_output(self):
        history = [self._msg("assistant", "resp", model="gpt-4o")]
        result = self._fn(history)
        assert "model" not in result[0]

    def test_preserves_order(self):
        history = [self._msg("user", f"msg{i}") for i in range(5)]
        result = self._fn(history)
        assert [r["content"] for r in result] == [f"msg{i}" for i in range(5)]


# ── confidence_tone ───────────────────────────────────────────────────────────

class TestConfidenceTone:
    """confidence_tone(confidence_str) → CSS tone class string."""

    def _fn(self, s):
        from core.consilium import confidence_tone
        return confidence_tone(s)

    def test_critical_is_neg(self):
        assert self._fn("CRITICAL") == "neg"

    def test_high_is_pos(self):
        assert self._fn("HIGH") == "pos"

    def test_moderate_is_brass(self):
        assert self._fn("MODERATE") == "brass"

    def test_low_is_warn(self):
        assert self._fn("LOW") == "warn"

    def test_very_low_is_neg(self):
        assert self._fn("VERY_LOW") == "neg"

    def test_returns_string(self):
        assert isinstance(self._fn("MODERATE"), str)
