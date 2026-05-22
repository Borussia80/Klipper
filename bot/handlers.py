"""bot/handlers.py — Handlers do Telegram Bot Klipper."""

from __future__ import annotations

import logging
import os
from datetime import date

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.parser import ParsedCapture, parse_message
from models.transaction import Category, PaymentMethod, Transaction, TransactionType

log = logging.getLogger(__name__)

_ALLOWED_IDS: frozenset[int] = frozenset(
    int(x) for x in os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "").split(",") if x.strip()
)

_CATEGORY_LABELS: dict[str, str] = {
    "Alimentação": "🍽️", "Transporte": "🚗", "Moradia": "🏠",
    "Saúde": "💊", "Educação": "📚", "Lazer": "🎮",
    "Investimento": "📈", "Renda": "💰", "Freelance": "💼", "Outros": "📎",
}


def _is_allowed(update: Update) -> bool:
    if not _ALLOWED_IDS:
        return True  # sem restrição se variável não configurada
    return update.effective_user.id in _ALLOWED_IDS


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return
    await update.message.reply_text(
        "⚓ *Klipper Bot*\n\n"
        "Registre lançamentos com linguagem natural:\n"
        "• `gastei 45 no ifood`\n"
        "• `paguei 250 fono`\n"
        "• `recebi 5000 salario`\n\n"
        "Comandos:\n"
        "/saldo — resumo do mês atual\n"
        "/ajuda — exemplos e dicas",
        parse_mode="Markdown",
    )


async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return
    await update.message.reply_text(
        "📖 *Como usar*\n\n"
        "*Gastos:*\n"
        "`gastei 50 mercado`\n"
        "`paguei R$ 150 aluguel`\n"
        "`45,90 ifood`\n\n"
        "*Receitas:*\n"
        "`recebi 5.000 salario`\n"
        "`ganhei 800 freela`\n\n"
        "*Saúde (Pedro):*\n"
        "`paguei 250 fono` — detectado como Saúde automaticamente\n\n"
        "O bot detecta a categoria automaticamente. "
        "Você pode editar antes de confirmar.",
        parse_mode="Markdown",
    )


async def cmd_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return
    try:
        from core.repositories import TransactionRepository
        from core.analytics import calcular_saldo_mensal
        repo = TransactionRepository()
        hoje = date.today()
        txs = repo.list_by_month(hoje.year, hoje.month)
        saldo = calcular_saldo_mensal(txs, hoje.year, hoje.month)
        await update.message.reply_text(
            f"📊 *{hoje.strftime('%B/%Y').capitalize()}*\n\n"
            f"💰 Ganhos: R$ {saldo.total_ganhos:,.2f}\n"
            f"💸 Gastos: R$ {saldo.total_gastos:,.2f}\n"
            f"{'✅' if saldo.saldo >= 0 else '⚠️'} Saldo: R$ {saldo.saldo:,.2f}\n"
            f"💹 Poupança: {saldo.taxa_poupanca:.1f}%",
            parse_mode="Markdown",
        )
    except Exception as e:
        log.error("Erro ao buscar saldo: %s", e)
        await update.message.reply_text("❌ Não foi possível buscar o saldo. Verifique a conexão.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Interpreta mensagem livre como lançamento financeiro."""
    if not _is_allowed(update):
        return

    text = (update.message.text or "").strip()
    capture = parse_message(text)

    if capture is None:
        await update.message.reply_text(
            "Não entendi. Tente: `gastei 50 mercado` ou `recebi 5000 salario`",
            parse_mode="Markdown",
        )
        return

    context.user_data["pending"] = capture
    await update.message.reply_text(
        _format_preview(capture),
        reply_markup=_confirm_keyboard(),
        parse_mode="Markdown",
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa botões inline (Confirmar / Cancelar / Editar categoria)."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    capture: ParsedCapture | None = context.user_data.get("pending")

    if data == "cancel" or capture is None:
        await query.edit_message_text("❌ Cancelado.")
        context.user_data.pop("pending", None)
        return

    if data == "confirm":
        await _persist_capture(capture, query)
        context.user_data.pop("pending", None)
        return

    if data.startswith("cat:"):
        cat_value = data[4:]
        try:
            capture.category = Category(cat_value)
            context.user_data["pending"] = capture
            await query.edit_message_text(
                _format_preview(capture),
                reply_markup=_confirm_keyboard(),
                parse_mode="Markdown",
            )
        except ValueError:
            await query.edit_message_text("Categoria inválida.")

    if data == "edit_cat":
        await query.edit_message_text(
            "Escolha a categoria:",
            reply_markup=_category_keyboard(),
        )


async def _persist_capture(capture: ParsedCapture, query) -> None:
    try:
        from core.repositories import TransactionRepository
        tx = Transaction(
            date=date.today(),
            amount=capture.amount,
            type=capture.type,
            category=capture.category,
            notes=capture.description,
            payment_method=PaymentMethod.PIX,
        )
        TransactionRepository().create(tx)
        icon = "✅" if capture.type == TransactionType.GANHO else "💸"
        await query.edit_message_text(
            f"{icon} Registrado!\n"
            f"R$ {capture.amount:,.2f} · {capture.category.value}"
        )
    except Exception as e:
        log.error("Erro ao persistir lançamento: %s", e)
        await query.edit_message_text("❌ Erro ao salvar. Tente novamente.")


def _format_preview(c: ParsedCapture) -> str:
    icon = "💰" if c.type == TransactionType.GANHO else "💸"
    cat_icon = _CATEGORY_LABELS.get(c.category.value, "📎")
    conf = "🟢" if c.confidence >= 0.85 else "🟡"
    return (
        f"{icon} *Confirmar lançamento?*\n\n"
        f"Valor: *R$ {c.amount:,.2f}*\n"
        f"Tipo: {'Receita' if c.type == TransactionType.GANHO else 'Gasto'}\n"
        f"Categoria: {cat_icon} {c.category.value} {conf}\n"
        f"Descrição: _{c.description}_"
    )


def _confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirmar", callback_data="confirm"),
            InlineKeyboardButton("✏️ Categoria", callback_data="edit_cat"),
            InlineKeyboardButton("❌ Cancelar", callback_data="cancel"),
        ]
    ])


def _category_keyboard() -> InlineKeyboardMarkup:
    cats = [c for c in Category]
    rows = [[InlineKeyboardButton(c.value, callback_data=f"cat:{c.value}")] for c in cats]
    rows.append([InlineKeyboardButton("⬅️ Voltar", callback_data="cancel")])
    return InlineKeyboardMarkup(rows)
