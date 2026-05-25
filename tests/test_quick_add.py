"""TDD Sprint 04 — parse_quick_add(): regex parser for quick transaction entry."""
from __future__ import annotations

import pytest
from decimal import Decimal


# ── parse_quick_add ───────────────────────────────────────────────────────────

class TestParseQuickAddValue:
    """Extração de valor numérico da entrada de texto livre."""

    def test_integer_value(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("almoço 42")
        assert result["amount"] == Decimal("42")

    def test_decimal_comma_value(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("uber 24,90")
        assert result["amount"] == Decimal("24.90")

    def test_decimal_dot_value(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("mercado 184.20")
        assert result["amount"] == Decimal("184.20")

    def test_value_at_start(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("42 almoço")
        assert result["amount"] == Decimal("42")

    def test_value_with_r_prefix(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("farmácia R$58,00")
        assert result["amount"] == Decimal("58.00")

    def test_large_value(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("aluguel 1500")
        assert result["amount"] == Decimal("1500")

    def test_no_value_returns_none(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("almoço")
        assert result["amount"] is None

    def test_only_value_returns_amount(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("42")
        assert result["amount"] == Decimal("42")


class TestParseQuickAddDescription:
    """Extração da descrição (texto livre sem o valor)."""

    def test_description_without_value(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("almoço restaurante 42")
        assert "almoço" in result["description"].lower() or "restaurante" in result["description"].lower()

    def test_description_strips_whitespace(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("  café   12  ")
        assert result["description"].strip() == result["description"]

    def test_description_not_empty_when_text_present(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("supermercado 200")
        assert len(result["description"]) > 0

    def test_description_excludes_amount(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("uber 24,90")
        assert "24,90" not in result["description"]
        assert "24.90" not in result["description"]


class TestParseQuickAddPaymentMethod:
    """Detecção automática de meio de pagamento."""

    def test_pix_keyword_detected(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("pix almoço 42")
        assert result["payment_method"] == "PIX"

    def test_pix_uppercase(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("PIX mercado 150")
        assert result["payment_method"] == "PIX"

    def test_credito_keyword(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("crédito itaú 300")
        assert result["payment_method"] == "CARTAO_CREDITO"

    def test_debito_keyword(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("débito supermercado 80")
        assert result["payment_method"] == "CARTAO_DEBITO"

    def test_dinheiro_keyword(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("dinheiro feira 35")
        assert result["payment_method"] == "DINHEIRO"

    def test_no_keyword_defaults_to_pix(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("almoço 42")
        assert result["payment_method"] == "PIX"

    def test_cartao_keyword_maps_to_credito(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("cartão lanchonete 18")
        assert result["payment_method"] in ("CARTAO_CREDITO", "CARTAO_DEBITO")


class TestParseQuickAddCategoryInference:
    """Inferência de categoria por palavras-chave."""

    def test_almoço_infers_alimentacao(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("almoço 42")
        assert result["category"] == "Alimentação"

    def test_mercado_infers_alimentacao(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("supermercado 200")
        assert result["category"] == "Alimentação"

    def test_uber_infers_transporte(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("uber 25")
        assert result["category"] == "Transporte"

    def test_farmácia_infers_saude(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("farmácia 58")
        assert result["category"] == "Saúde"

    def test_remédio_infers_saude(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("remédio 40")
        assert result["category"] == "Saúde"

    def test_unknown_defaults_to_outros(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("xablau 99")
        assert result["category"] == "Outros"

    def test_cinema_infers_lazer(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("cinema 30")
        assert result["category"] == "Lazer"

    def test_aluguel_infers_moradia(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("aluguel 1500")
        assert result["category"] == "Moradia"


class TestParseQuickAddReturnShape:
    """O retorno sempre tem as chaves esperadas."""

    def test_returns_dict(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("café 5")
        assert isinstance(result, dict)

    def test_has_all_required_keys(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("café 5")
        for key in ("amount", "description", "payment_method", "category", "type"):
            assert key in result, f"Missing key: {key}"

    def test_default_type_is_gasto(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("almoço 42")
        assert result["type"] == "GASTO"

    def test_empty_string_returns_none_amount(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("")
        assert result["amount"] is None

    def test_amount_is_decimal_or_none(self):
        from core.quick_add import parse_quick_add
        result = parse_quick_add("café 5,50")
        assert result["amount"] is None or isinstance(result["amount"], Decimal)
