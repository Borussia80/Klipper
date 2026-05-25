"""Consilium — lógica pura extraída de pages/5_AI_Consilium.py.

Funções puras: sem I/O, sem Streamlit. Facilita testes e reutilização.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from core.anti_bs import PERGUNTA_OBRIGATORIA

# ── Mapeamento de modelos ──────────────────────────────────────────────────────

_MODEL_MAP: dict[str, str] = {
    "claude": "claude-sonnet-4-6",
    "gemini": "gemini/gemini-2.0-flash",
    "gpt4o":  "gpt-4o",
    "qwen":   "openai/qwen-plus",
    "kimi":   "openai/moonshot-v1-8k",
}

_AUTO_ORDER = [
    ("claude", "ANTHROPIC_API_KEY"),
    ("gemini", "GOOGLE_API_KEY"),
    ("gpt4o",  "OPENAI_API_KEY"),
    ("qwen",   "DASHSCOPE_API_KEY"),
    ("kimi",   "MOONSHOT_API_KEY"),
]

_FALLBACK_AUTO = "gemini/gemini-2.0-flash"


def resolve_provider(provider_key: str, env: dict[str, str] | None = None) -> str:
    """Resolve provider key → model string.

    Args:
        provider_key: "auto", "claude", "gemini", "gpt4o", "qwen", "kimi".
        env: Environment variables dict (defaults to os.environ if None).

    Returns:
        LiteLLM model string.
    """
    if env is None:
        env = dict(os.environ)

    if provider_key == "auto":
        for provider, key in _AUTO_ORDER:
            if env.get(key):
                return _MODEL_MAP[provider]
        return _FALLBACK_AUTO

    return _MODEL_MAP.get(provider_key, _MODEL_MAP["claude"])


# ── Confidence helpers ─────────────────────────────────────────────────────────

_CONFIDENCE_PCT: dict[str, int] = {
    "VERY_LOW": 20,
    "LOW":      40,
    "MODERATE": 60,
    "HIGH":     80,
    "CRITICAL": 100,
}

_CONFIDENCE_TONE: dict[str, str] = {
    "VERY_LOW": "neg",
    "LOW":      "warn",
    "MODERATE": "brass",
    "HIGH":     "pos",
    "CRITICAL": "neg",
}


def confidence_to_pct(confidence_str: str) -> int:
    """Converte string de confidence em percentual 0–100 para gauge."""
    return _CONFIDENCE_PCT.get(confidence_str.upper(), 50)


def confidence_tone(confidence_str: str) -> str:
    """Retorna tone CSS class para a confidence (pos/neg/brass/warn)."""
    return _CONFIDENCE_TONE.get(confidence_str.upper(), "brass")


# ── System prompt ──────────────────────────────────────────────────────────────

def build_system_prompt() -> str:
    """Retorna o system prompt do M4 Consilium."""
    return (
        "Você é M4 — Auditoria Histórica do WikiAgent Financeiro Klipper.\n\n"
        "Diretrizes absolutas:\n"
        "- Matemática ancora. Narrativa sem evidência quantitativa não altera decisão.\n"
        "- Contexto modula risco — nunca compra ativo sozinho.\n"
        "- Sem verborreia. Resposta máxima: 300 palavras.\n"
        "- Declarar incerteza SEMPRE que dados forem insuficientes.\n"
        "- Reportar riscos antes de oportunidades.\n"
        "- P/VP sozinho não valida ativo. DY alto exige validação de sustentabilidade.\n\n"
        "WikiAgent M1 Thresholds:\n"
        "- Score ≥ 0.60 → COMPRAR | 0.30–0.59 → MANTER | < 0.30 → REDUZIR\n\n"
        "M2 Limites (Beginner Mode):\n"
        "- Max por ativo: 10% | Max por tese/setor: 25% | Caixa mínimo: 20%\n\n"
        f'Anti-BS: "{PERGUNTA_OBRIGATORIA}"'
    )


# ── Chat message ───────────────────────────────────────────────────────────────

@dataclass
class ConsiliumMessage:
    """Mensagem do histórico de chat M4."""
    role: str
    content: str
    model: str | None = None


def chat_history_to_messages(history: list[ConsiliumMessage]) -> list[dict]:
    """Converte histórico de ConsiliumMessage para formato LiteLLM [{role, content}]."""
    return [{"role": m.role, "content": m.content} for m in history]
