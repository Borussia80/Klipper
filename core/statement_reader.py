"""core/statement_reader.py — Leitura de extratos bancários e faturas em PDF.

Pipeline:
  1. Detecta se o PDF tem texto seleccionável (PyMuPDF) ou é imagem (OCR via PaddleOCR).
  2. Extrai o texto bruto.
  3. Analisa linha a linha buscando padrões data + valor + descrição.
  4. Retorna lista de ParsedTransaction para revisão antes da importação.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime

import fitz  # PyMuPDF

from models.transaction import Category, TransactionType

log = logging.getLogger(__name__)

# ── Regex de extração ──────────────────────────────────────────────────────────
# Datas: DD/MM/AAAA | DD/MM/AA | DD/MM | DD mês
_DATE_RE = re.compile(
    r"(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?"
    r"|(\d{1,2})\s+(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)",
    re.IGNORECASE,
)
_MONTH_MAP = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}
# Valores: 1.234,56 | 1234,56 | -1.234,56 | +5.000,00
_AMOUNT_RE = re.compile(r"([+-]?\d{1,3}(?:\.\d{3})*,\d{2})")
# Indicadores de débito/crédito no final da linha (Itaú, BB)
_DC_SUFFIX = re.compile(r"\b([CD]|DB|CR|Deb|Cred)\b\.?$", re.IGNORECASE)
# Linhas de saldo/cabeçalho que não são transações
_SKIP_RE = re.compile(
    r"saldo\s+do\s+dia|per[ií]odo\s+de\s+visualiza|emitido\s+em|"
    r"data\s+lan[çc]amentos|aviso!|limite\s+da\s+conta|extrato\s+conta",
    re.IGNORECASE,
)

# ── Categorização por palavras-chave ───────────────────────────────────────────
_CATEGORY_KEYWORDS: list[tuple[str, Category]] = [
    ("ifood", Category.ALIMENTACAO), ("rappi", Category.ALIMENTACAO),
    ("mercado", Category.ALIMENTACAO), ("supermercado", Category.ALIMENTACAO),
    ("padaria", Category.ALIMENTACAO), ("restaurante", Category.ALIMENTACAO),
    ("alimenta", Category.ALIMENTACAO), ("lanchonete", Category.ALIMENTACAO),
    ("uber", Category.TRANSPORTE), ("99pop", Category.TRANSPORTE),
    ("combustiv", Category.TRANSPORTE), ("gasolina", Category.TRANSPORTE),
    ("estacion", Category.TRANSPORTE), ("metro ", Category.TRANSPORTE),
    ("onibus", Category.TRANSPORTE), ("pedagio", Category.TRANSPORTE),
    ("aluguel", Category.MORADIA), ("condomin", Category.MORADIA),
    ("energia", Category.MORADIA), ("celesc", Category.MORADIA),
    ("internet", Category.MORADIA), ("vivo", Category.MORADIA),
    ("claro", Category.MORADIA), ("oi ", Category.MORADIA),
    ("farmacia", Category.SAUDE), ("drogaria", Category.SAUDE),
    ("laborat", Category.SAUDE), ("hospital", Category.SAUDE),
    ("clinica", Category.SAUDE), ("plano saude", Category.SAUDE),
    ("escola", Category.EDUCACAO), ("faculdade", Category.EDUCACAO),
    ("curso", Category.EDUCACAO), ("mensalid", Category.EDUCACAO),
    ("netflix", Category.LAZER), ("spotify", Category.LAZER),
    ("prime video", Category.LAZER), ("disney", Category.LAZER),
    ("cinema", Category.LAZER), ("steam", Category.LAZER),
    ("salario", Category.RENDA), ("salário", Category.RENDA),
    ("holerite", Category.RENDA), ("pro-labore", Category.RENDA),
    ("freelance", Category.FREELANCE), ("freela", Category.FREELANCE),
    ("invest", Category.INVESTIMENTO), ("fii", Category.INVESTIMENTO),
    ("cdb", Category.INVESTIMENTO), ("tesouro", Category.INVESTIMENTO),
]


@dataclass
class ParsedTransaction:
    date: date
    description: str
    amount: float
    tx_type: TransactionType
    category: Category
    confidence: float
    raw_line: str = field(default="", repr=False)


@dataclass
class StatementResult:
    transactions: list[ParsedTransaction]
    pdf_type: str          # "text" | "ocr"
    page_count: int
    raw_text: str = field(default="", repr=False)
    warnings: list[str] = field(default_factory=list)


# ── Interface pública ──────────────────────────────────────────────────────────

def read_statement(pdf_bytes: bytes) -> StatementResult:
    """Ponto de entrada único: lê PDF e retorna transações parseadas."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pdf_type = _detect_pdf_type(doc)
    warnings: list[str] = []

    if pdf_type == "text":
        raw_text = _extract_text(doc)
    else:
        raw_text, ocr_warnings = _extract_ocr(doc)
        warnings.extend(ocr_warnings)

    transactions = _parse_transactions(raw_text)
    return StatementResult(
        transactions=transactions,
        pdf_type=pdf_type,
        page_count=len(doc),
        raw_text=raw_text,
        warnings=warnings,
    )


# ── Detecção de tipo ───────────────────────────────────────────────────────────

def _detect_pdf_type(doc: fitz.Document) -> str:
    """Retorna 'text' se o PDF tem texto seleccionável, 'ocr' caso contrário."""
    total_chars = sum(len(page.get_text().strip()) for page in doc)
    return "text" if total_chars > 100 else "ocr"


# ── Extração de texto ──────────────────────────────────────────────────────────

def _extract_text(doc: fitz.Document) -> str:
    """Extrai texto preservando linhas de tabela via coordenadas de palavras."""
    lines = []
    for page in doc:
        words = page.get_text("words")  # (x0, y0, x1, y1, word, block, line, word_no)
        if not words:
            lines.append(page.get_text("text"))
            continue
        rows: dict[int, list[tuple[float, str]]] = {}
        for item in words:
            x0, y0, word = item[0], item[1], item[4]
            y_bucket = round(y0 / 3) * 3
            rows.setdefault(y_bucket, []).append((x0, word))
        for y_key in sorted(rows):
            row_words = sorted(rows[y_key], key=lambda w: w[0])
            lines.append(" ".join(w[1] for w in row_words))
    return "\n".join(lines)


def _extract_ocr(doc: fitz.Document) -> tuple[str, list[str]]:
    """Extrai texto via PaddleOCR. Retorna (texto, avisos)."""
    try:
        import numpy as np
        from paddleocr import PaddleOCR
    except ImportError as e:
        return "", [f"PaddleOCR indisponível: {e}. Instale paddleocr."]

    ocr = _get_ocr_engine()
    pages_text: list[str] = []
    warnings: list[str] = []

    for page_num, page in enumerate(doc):
        mat = fitz.Matrix(2.0, 2.0)  # zoom 2× para melhor OCR
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)

        try:
            result = ocr.ocr(img, cls=False)
            if result and result[0]:
                lines = sorted(result[0], key=lambda x: x[0][0][1])  # ordem por Y
                pages_text.append(" ".join(item[1][0] for item in lines))
        except Exception as e:
            warnings.append(f"Página {page_num + 1}: OCR falhou — {e}")

    return "\n".join(pages_text), warnings


def _get_ocr_engine():
    """Inicializa PaddleOCR uma única vez (chamado em contexto Streamlit via cache)."""
    from paddleocr import PaddleOCR
    return PaddleOCR(use_angle_cls=False, lang="pt", show_log=False)


# ── Parsing de transações ──────────────────────────────────────────────────────

def _parse_transactions(text: str) -> list[ParsedTransaction]:
    results: list[ParsedTransaction] = []
    for line in text.splitlines():
        tx = _parse_line(line.strip())
        if tx:
            results.append(tx)
    return results


def _parse_line(line: str) -> ParsedTransaction | None:
    if len(line) < 8:
        return None
    if _SKIP_RE.search(line):
        return None

    tx_date = _extract_date(line)
    if tx_date is None:
        return None

    amounts = _AMOUNT_RE.findall(line)
    if not amounts:
        return None

    raw_amount = amounts[-1]  # último valor na linha = valor da transação
    amount, tx_type = _parse_amount_and_type(raw_amount, line)
    if amount is None or amount <= 0:
        return None

    description = _extract_description(line, raw_amount)
    category = _categorize(description)
    confidence = 0.85 if category != Category.OUTROS else 0.55

    return ParsedTransaction(
        date=tx_date,
        description=description or line[:60],
        amount=amount,
        tx_type=tx_type,
        category=category,
        confidence=confidence,
        raw_line=line,
    )


def _extract_date(line: str) -> date | None:
    m = _DATE_RE.search(line)
    if not m:
        return None
    today = date.today()
    try:
        if m.group(4):  # "14 mai" format
            day = int(m.group(4))
            month = _MONTH_MAP[m.group(5).lower()]
            return date(today.year, month, day)
        day, month = int(m.group(1)), int(m.group(2))
        year_raw = m.group(3)
        if year_raw:
            year = int(year_raw) + (2000 if len(year_raw) == 2 else 0)
        else:
            year = today.year
        return date(year, month, day)
    except (ValueError, KeyError):
        return None


def _parse_amount_and_type(raw: str, line: str) -> tuple[float | None, TransactionType]:
    normalized = raw.replace(".", "").replace(",", ".")
    try:
        value = float(normalized)
    except ValueError:
        return None, TransactionType.GASTO

    # Sinal negativo explícito → débito (Itaú e maioria dos bancos)
    if raw.startswith("-") or value < 0:
        return abs(value), TransactionType.GASTO

    # Sufixo D/C (Bradesco, BB)
    dc = _DC_SUFFIX.search(line)
    if dc:
        letter = dc.group(1).upper()
        if letter in {"D", "DB", "DEB"}:
            return value, TransactionType.GASTO
        if letter in {"C", "CR", "CRED"}:
            return value, TransactionType.GANHO

    # Sinal positivo explícito → crédito
    if raw.startswith("+"):
        return value, TransactionType.GANHO

    # Valor positivo sem sinal → crédito (padrão Itaú: débitos sempre têm "-")
    return value, TransactionType.GANHO


def _extract_description(line: str, amount_str: str) -> str:
    desc = _DATE_RE.sub("", line)
    desc = desc.replace(amount_str, "")
    desc = _DC_SUFFIX.sub("", desc)
    desc = re.sub(r"R\$", "", desc)
    return re.sub(r"\s+", " ", desc).strip(" -+.,")


def _categorize(description: str) -> Category:
    lower = description.lower()
    for keyword, category in _CATEGORY_KEYWORDS:
        if keyword in lower:
            return category
    return Category.OUTROS
