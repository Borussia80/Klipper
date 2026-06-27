"""Categorização fuzzy de transações — local, explicável, sem ML pesado.

Para finanças pessoais (poucos milhares de transações/usuário), fuzzy bem feito
entrega mais que SVM/redes neurais, e é:
  • explicável  — devolve o padrão que casou e o score;
  • local       — roda no `core/`, sem mandar a transação para um LLM (privacidade);
  • rápido      — rapidfuzz é C++, custo desprezível por transação.

Camadas, em ordem de precedência (a primeira que decide com confiança vence):
  1. Histórico do usuário — rótulos que ele já confirmou (fuzzy alto).
  2. Regras de keyword     — substring determinístico (rápido, previsível).
  3. Fuzzy                 — Jaro-Winkler + token_set_ratio, tolera ruído/OCR/typo.
  4. Fallback              — OUTROS, marcado como NÃO confiável (validar à mão).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from rapidfuzz import fuzz, process
from rapidfuzz.distance import JaroWinkler

from models.transaction import Category

# ── Base de regras: keyword (stem) → categoria ────────────────────────────────
# Canônica. `statement_reader` importa daqui.
CATEGORY_KEYWORDS: list[tuple[str, Category]] = [
    ("ifood", Category.ALIMENTACAO), ("rappi", Category.ALIMENTACAO),
    ("mercado", Category.ALIMENTACAO), ("supermercado", Category.ALIMENTACAO),
    ("padaria", Category.ALIMENTACAO), ("restaurante", Category.ALIMENTACAO),
    ("alimenta", Category.ALIMENTACAO), ("lanchonete", Category.ALIMENTACAO),
    ("uber", Category.TRANSPORTE), ("99pop", Category.TRANSPORTE),
    ("combustiv", Category.TRANSPORTE), ("gasolina", Category.TRANSPORTE),
    ("estacion", Category.TRANSPORTE), ("metro", Category.TRANSPORTE),
    ("onibus", Category.TRANSPORTE), ("pedagio", Category.TRANSPORTE),
    ("aluguel", Category.MORADIA), ("condomin", Category.MORADIA),
    ("energia", Category.MORADIA), ("celesc", Category.MORADIA),
    ("internet", Category.MORADIA), ("vivo", Category.MORADIA),
    ("claro", Category.MORADIA), ("oi", Category.MORADIA),
    ("farmacia", Category.SAUDE), ("drogaria", Category.SAUDE),
    ("laborat", Category.SAUDE), ("hospital", Category.SAUDE),
    ("clinica", Category.SAUDE), ("plano saude", Category.SAUDE),
    ("escola", Category.EDUCACAO), ("faculdade", Category.EDUCACAO),
    ("curso", Category.EDUCACAO), ("mensalid", Category.EDUCACAO),
    ("netflix", Category.LAZER), ("spotify", Category.LAZER),
    ("prime video", Category.LAZER), ("disney", Category.LAZER),
    ("cinema", Category.LAZER), ("steam", Category.LAZER),
    ("salario", Category.RENDA), ("holerite", Category.RENDA),
    ("pro-labore", Category.RENDA), ("rendimento", Category.RENDA),
    ("rend pago", Category.RENDA),
    ("freelance", Category.FREELANCE), ("freela", Category.FREELANCE),
    ("invest", Category.INVESTIMENTO), ("fii", Category.INVESTIMENTO),
    ("cdb", Category.INVESTIMENTO), ("tesouro", Category.INVESTIMENTO),
]

# Ruído de extrato/maquininha — removido antes de casar.
# (Cuidado: não inclui termos que SÃO keyword, ex.: "mensalidade".)
_NOISE_TOKENS = frozenset({
    "pg", "pag", "pagto", "pagamento", "compra", "cartao", "card", "deb",
    "debito", "cred", "credito", "ted", "doc", "pix", "saque", "tar",
    "tarifa", "taxa", "parc", "parcela", "ltda", "me", "epp", "sa", "br",
    "trip", "help", "payment", "purchase",
    # preposições/artigos PT — não carregam sinal de categoria
    "de", "do", "da", "das", "dos",
})

_PUNCT_RE = re.compile(r"[*#/\\\-_.,:;|()]+")
_DIGIT_RE = re.compile(r"\d+")
_SPACE_RE = re.compile(r"\s+")

# Confiança: acima de FUZZY_CONFIDENT é automático; entre DOUBTFUL e CONFIDENT
# decide mas marca para validação; abaixo cai em OUTROS.
FUZZY_CONFIDENT = 0.86
FUZZY_DOUBTFUL = 0.72
HISTORY_CONFIDENT = 0.90


@dataclass(frozen=True)
class CategoryGuess:
    category: Category
    score: float          # 0–1
    source: str           # "history" | "rule" | "fuzzy" | "fallback"
    matched: str          # padrão/descrição que casou (explicabilidade)
    confident: bool       # False → pedir validação ao usuário


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize(text: str) -> str:
    """Limpa ruído bancário e deixa só tokens semânticos, sem acento, minúsculos.

    Ex.: 'PG *UBER TRIP HELP DE_BR 12/05'  →  'uber'
    """
    t = strip_accents(text).lower()
    t = _PUNCT_RE.sub(" ", t)
    t = _DIGIT_RE.sub(" ", t)
    tokens = [tok for tok in t.split() if len(tok) > 1 and tok not in _NOISE_TOKENS]
    return _SPACE_RE.sub(" ", " ".join(tokens)).strip()


# Keywords normalizadas (uma vez) — preserva ordem/categoria.
_NORM_KEYWORDS: list[tuple[str, Category]] = [
    (normalize(kw) or kw, cat) for kw, cat in CATEGORY_KEYWORDS
]
_KEYWORD_CHOICES: list[str] = [kw for kw, _ in _NORM_KEYWORDS]


def _best_fuzzy(norm_desc: str) -> tuple[Category, float, str] | None:
    """Melhor categoria por similaridade fuzzy. None se a descrição for vazia."""
    if not norm_desc:
        return None

    # token_set_ratio / WRatio: bom para multi-palavra e ordem trocada.
    extracted = process.extractOne(norm_desc, _KEYWORD_CHOICES, scorer=fuzz.WRatio)
    best_kw, wr_score = (extracted[0], extracted[1] / 100.0) if extracted else ("", 0.0)

    # Jaro-Winkler por token: pega typo/OCR em keyword curta (uber↔ubre).
    desc_tokens = norm_desc.split()
    jw_best, jw_kw = 0.0, ""
    for kw in _KEYWORD_CHOICES:
        for tok in desc_tokens:
            sim = JaroWinkler.similarity(tok, kw)
            if sim > jw_best:
                jw_best, jw_kw = sim, kw

    if jw_best > wr_score:
        best_kw, score = jw_kw, jw_best
    else:
        score = wr_score

    cat = next(c for k, c in _NORM_KEYWORDS if k == best_kw)
    return cat, score, best_kw


def categorize(
    description: str,
    history: list[tuple[str, Category]] | None = None,
) -> CategoryGuess:
    """Categoriza uma descrição de transação. Sempre devolve um CategoryGuess.

    `history`: rótulos que o usuário já confirmou — pares (descrição_bruta, categoria).
    Têm precedência sobre as regras genéricas (é o "aprende com o histórico").
    """
    norm = normalize(description)
    if not norm:
        return CategoryGuess(Category.OUTROS, 0.0, "fallback", "", confident=False)

    # 1. Histórico do usuário
    if history:
        best_score, best_cat, best_match = 0.0, Category.OUTROS, ""
        for raw, cat in history:
            hnorm = normalize(raw)
            if not hnorm:
                continue
            sim = max(
                fuzz.token_set_ratio(norm, hnorm) / 100.0,
                JaroWinkler.similarity(norm, hnorm),
            )
            if sim > best_score:
                best_score, best_cat, best_match = sim, cat, hnorm
        if best_score >= HISTORY_CONFIDENT:
            return CategoryGuess(best_cat, best_score, "history", best_match, confident=True)

    # 2. Regras — substring determinístico
    for kw, cat in _NORM_KEYWORDS:
        if kw in norm:
            return CategoryGuess(cat, 1.0, "rule", kw, confident=True)

    # 3. Fuzzy
    fuzzy = _best_fuzzy(norm)
    if fuzzy:
        cat, score, matched = fuzzy
        if score >= FUZZY_CONFIDENT:
            return CategoryGuess(cat, score, "fuzzy", matched, confident=True)
        if score >= FUZZY_DOUBTFUL:
            return CategoryGuess(cat, score, "fuzzy", matched, confident=False)

    # 4. Fallback
    return CategoryGuess(Category.OUTROS, 0.0, "fallback", "", confident=False)


def categorize_category(
    description: str,
    history: list[tuple[str, Category]] | None = None,
) -> Category:
    """Atalho que devolve só a Category — drop-in para o parser de extratos."""
    return categorize(description, history).category
