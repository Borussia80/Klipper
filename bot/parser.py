"""bot/parser.py — Interpreta mensagens em linguagem natural para lançamentos financeiros."""

from __future__ import annotations

import re
from dataclasses import dataclass

from models.transaction import Category, TransactionType

# ── Mapeamento de palavras-chave para categorias ───────────────────────────────
_CATEGORY_KEYWORDS: list[tuple[str, Category]] = [
    # Alimentação
    ("ifood", Category.ALIMENTACAO), ("rappi", Category.ALIMENTACAO),
    ("mercado", Category.ALIMENTACAO), ("supermercado", Category.ALIMENTACAO),
    ("padaria", Category.ALIMENTACAO), ("restaurante", Category.ALIMENTACAO),
    ("lanche", Category.ALIMENTACAO), ("pizza", Category.ALIMENTACAO),
    ("cafe", Category.ALIMENTACAO), ("café", Category.ALIMENTACAO),
    ("almoco", Category.ALIMENTACAO), ("almoço", Category.ALIMENTACAO),
    ("jantar", Category.ALIMENTACAO), ("feira", Category.ALIMENTACAO),
    ("hortifruti", Category.ALIMENTACAO), ("acougue", Category.ALIMENTACAO),
    # Transporte
    ("uber", Category.TRANSPORTE), ("99pop", Category.TRANSPORTE),
    ("onibus", Category.TRANSPORTE), ("metro", Category.TRANSPORTE),
    ("combustivel", Category.TRANSPORTE), ("gasolina", Category.TRANSPORTE),
    ("etanol", Category.TRANSPORTE), ("posto", Category.TRANSPORTE),
    ("estacionamento", Category.TRANSPORTE), ("pedagio", Category.TRANSPORTE),
    # Moradia
    ("aluguel", Category.MORADIA), ("condominio", Category.MORADIA),
    ("agua", Category.MORADIA), ("luz", Category.MORADIA),
    ("energia", Category.MORADIA), ("gas", Category.MORADIA),
    ("internet", Category.MORADIA), ("iptu", Category.MORADIA),
    # Saúde
    ("farmacia", Category.SAUDE), ("remedio", Category.SAUDE),
    ("medico", Category.SAUDE), ("hospital", Category.SAUDE),
    ("laboratorio", Category.SAUDE), ("exame", Category.SAUDE),
    ("fono", Category.SAUDE), ("terapia", Category.SAUDE),
    ("fonoaudiologia", Category.SAUDE), ("psico", Category.SAUDE),
    # Educação
    ("escola", Category.EDUCACAO), ("curso", Category.EDUCACAO),
    ("faculdade", Category.EDUCACAO), ("mensalidade", Category.EDUCACAO),
    ("livro", Category.EDUCACAO), ("material", Category.EDUCACAO),
    # Lazer
    ("netflix", Category.LAZER), ("spotify", Category.LAZER),
    ("amazon", Category.LAZER), ("cinema", Category.LAZER),
    ("show", Category.LAZER), ("viagem", Category.LAZER),
    ("hotel", Category.LAZER), ("passagem", Category.LAZER),
    # Renda / Investimento
    ("salario", Category.RENDA), ("salário", Category.RENDA),
    ("holerite", Category.RENDA), ("pro-labore", Category.RENDA),
    ("freelance", Category.FREELANCE), ("freela", Category.FREELANCE),
    ("invest", Category.INVESTIMENTO), ("fii", Category.INVESTIMENTO),
    ("acao", Category.INVESTIMENTO), ("ativo", Category.INVESTIMENTO),
]

_GASTO_TRIGGERS: frozenset[str] = frozenset({
    "gastei", "paguei", "comprei", "despesa", "gasto", "pago",
    "saiu", "debito", "debitei",
})
_GANHO_TRIGGERS: frozenset[str] = frozenset({
    "recebi", "ganhei", "entrou", "ganho", "renda", "recebimento",
    "credito", "creditou",
})

# Captura valores como: 50 | 50,00 | 50.00 | 1.500,00 | R$50 | R$ 1.500,00
_AMOUNT_RE = re.compile(
    r"(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2}|\d+,\d{2}|\d+\.\d{2}|\d+)"
)


@dataclass
class ParsedCapture:
    amount: float
    type: TransactionType
    category: Category
    description: str
    raw: str
    confidence: float


def parse_message(text: str) -> ParsedCapture | None:
    """
    Interpreta mensagem livre como lançamento financeiro.

    Retorna None se não for possível extrair um valor monetário.
    """
    amount = _parse_amount(text)
    if not amount or amount <= 0:
        return None

    tx_type   = _detect_type(text)
    category  = _detect_category(text)
    desc      = _clean_description(text)
    # Confiança cai quando categoria não foi detectada
    confidence = 0.90 if category != Category.OUTROS else 0.60

    return ParsedCapture(
        amount=amount,
        type=tx_type,
        category=category,
        description=desc or "sem descrição",
        raw=text,
        confidence=confidence,
    )


def _parse_amount(text: str) -> float | None:
    m = _AMOUNT_RE.search(text)
    if not m:
        return None
    raw = m.group(1)
    # Normaliza separadores brasileiros: 1.234,56 → 1234.56 | 1234,56 → 1234.56
    if "." in raw and "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    else:
        raw = raw.replace(",", ".")
    try:
        return round(float(raw), 2)
    except ValueError:
        return None


def _detect_type(text: str) -> TransactionType:
    words = set(text.lower().split())
    if words & _GANHO_TRIGGERS:
        return TransactionType.GANHO
    return TransactionType.GASTO


def _detect_category(text: str) -> Category:
    lower = text.lower()
    for keyword, category in _CATEGORY_KEYWORDS:
        if re.search(r"\b" + re.escape(keyword) + r"\b", lower):
            return category
    return Category.OUTROS


def _clean_description(text: str) -> str:
    """Remove valor, gatilhos e stopwords; retorna descrição limpa."""
    desc = _AMOUNT_RE.sub("", text)
    desc = re.sub(r"\bR\$\b", "", desc, flags=re.IGNORECASE)
    stopwords = _GASTO_TRIGGERS | _GANHO_TRIGGERS | {"no", "na", "em", "de", "da", "do", "o", "a"}
    for word in stopwords:
        desc = re.sub(r"\b" + re.escape(word) + r"\b", "", desc, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", desc).strip(" ,.-")
