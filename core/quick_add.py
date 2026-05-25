"""Quick Add parser — interpreta entrada de texto livre como transação financeira.

Exemplos:
    "almoço 42"          → {amount: 42, category: Alimentação, payment_method: PIX}
    "pix mercado 150"    → {amount: 150, category: Alimentação, payment_method: PIX}
    "crédito cinema 30"  → {amount: 30, category: Lazer, payment_method: CARTAO_CREDITO}
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

# ── Payment method keywords ───────────────────────────────────────────────────

_PM_PATTERNS: list[tuple[str, str]] = [
    (r"(?<!\w)pix(?!\w)",                       "PIX"),
    (r"cr[eé]dito",                             "CARTAO_CREDITO"),
    (r"d[eé]bito",                              "CARTAO_DEBITO"),
    (r"cart[aã]o",                              "CARTAO_CREDITO"),
    (r"dinheiro|esp[eé]cie",                    "DINHEIRO"),
    (r"(?<!\w)ted(?!\w)|transfer[eê]ncia",      "TED"),
    (r"boleto",                                 "BOLETO"),
]

# ── Category keyword mapping ──────────────────────────────────────────────────

_CAT_PATTERNS: list[tuple[str, str]] = [
    (r"almo[cç]o|janta|refei[cç][aã]o|restaurante|lanche"
     r"|caf[eé]|pizza|supermercado|mercado"
     r"|padaria|feira|delivery|ifood|rappi",
     "Alimentação"),
    (r"uber|taxi|t[aá]xi|[oô]nibus|metr[oô]"
     r"|combust[ií]vel|gasolina|estacionamento|ped[aá]gio",
     "Transporte"),
    (r"farm[aá]cia|rem[eé]dio|m[eé]dico"
     r"|consulta|exame|hospital|plano.*sa[uú]de",
     "Saúde"),
    (r"aluguel|condom[ií]nio|[aá]gua"
     r"|energia|luz|g[aá]s|iptu",
     "Moradia"),
    (r"curso|livro|escola|faculdade|universidade"
     r"|mensalidade|educa[cç][aã]o",
     "Educação"),
    (r"cinema|show|concerto|viagem|hotel|netflix"
     r"|spotify|lazer|jogo|jogos",
     "Lazer"),
    (r"sal[aá]rio|freela|freelance"
     r"|dividendo|provento",
     "Renda"),
]

# ── Value extraction regex ────────────────────────────────────────────────────

# Matches optional R$ prefix then a number with optional thousands/decimal separators
_VALUE_RE = re.compile(r"R\$\s*(\d[\d.,]*)|((?<!\d)\d[\d.,]*(?!\d))", re.IGNORECASE)


def _normalise_amount(raw: str) -> Decimal | None:
    """Normalise Brazilian/international number string to Decimal."""
    raw = raw.strip()
    if "," in raw and "." in raw:
        # "1.234,56" → thousands dot, decimal comma
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        parts = raw.split(",")
        # decimal comma if last segment has 1-2 digits
        if len(parts[-1]) <= 2:
            raw = raw.replace(",", ".")
        else:
            raw = raw.replace(",", "")
    elif "." in raw:
        parts = raw.split(".")
        # thousands dot if last segment has 3 digits
        if len(parts[-1]) == 3:
            raw = raw.replace(".", "")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return None


def _extract_amount(text: str) -> tuple[Decimal | None, str]:
    """Return (amount, text_without_amount). Handles R$, commas and dots."""
    # Try R$-prefixed first, then bare number
    match = _VALUE_RE.search(text)
    if not match:
        return None, text.strip()
    raw = match.group(1) or match.group(2)
    amount = _normalise_amount(raw)
    if amount is None:
        return None, text.strip()
    cleaned = (text[: match.start()] + text[match.end() :]).strip()
    cleaned = re.sub(r"R\$\s*$", "", cleaned).strip()
    return amount, cleaned


def _detect_payment_method(text: str) -> str:
    lower = text.lower()
    for pattern, method in _PM_PATTERNS:
        if re.search(pattern, lower):
            return method
    return "PIX"


def _infer_category(text: str) -> str:
    lower = text.lower()
    for pattern, category in _CAT_PATTERNS:
        if re.search(pattern, lower):
            return category
    return "Outros"


def parse_quick_add(text: str) -> dict:
    """Parse free-form text into a transaction dict.

    Returns keys: amount (Decimal|None), description (str),
                  payment_method (str), category (str), type (str).
    """
    text = (text or "").strip()
    if not text:
        return {
            "amount": None,
            "description": "",
            "payment_method": "PIX",
            "category": "Outros",
            "type": "GASTO",
        }

    payment_method = _detect_payment_method(text)
    # Remove payment keywords from text before inferring category / description
    pm_free = text
    for pattern, _ in _PM_PATTERNS:
        pm_free = re.sub(pattern, "", pm_free, flags=re.IGNORECASE).strip()

    category = _infer_category(pm_free or text)
    amount, description = _extract_amount(pm_free or text)

    return {
        "amount": amount,
        "description": description,
        "payment_method": payment_method,
        "category": category,
        "type": "GASTO",
    }
