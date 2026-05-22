"""bot/bot.py — Entry point do Klipper Telegram Bot.

Executar localmente:
    python bot/bot.py

Em produção (Railway / Heroku / VPS):
    Definir TELEGRAM_BOT_TOKEN e TELEGRAM_ALLOWED_USER_IDS no ambiente.
    O processo roda independentemente do Streamlit Cloud.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.handlers import (
    cmd_ajuda,
    cmd_saldo,
    cmd_start,
    handle_callback,
    handle_text,
)

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        log.critical("TELEGRAM_BOT_TOKEN não definido. Encerrando.")
        sys.exit(1)

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ajuda", cmd_ajuda))
    app.add_handler(CommandHandler("help", cmd_ajuda))
    app.add_handler(CommandHandler("saldo", cmd_saldo))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    log.info("Klipper Bot iniciado — aguardando mensagens…")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
