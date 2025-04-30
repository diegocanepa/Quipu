import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bot import command_handlers, message_handlers
from config import config

logger = logging.getLogger(__name__)

application = (
    Application.builder()
    .token(config.TELEGRAM_BOT_TOKEN)
    .updater(None) 
    .build()
)

def register_handlers():
    application.add_handler(CommandHandler("start", command_handlers.start))
    application.add_handler(CommandHandler("help", command_handlers.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.proccess_message))
    application.add_handler(CallbackQueryHandler(message_handlers.confirm_save, pattern="^confirm#"))
    application.add_handler(CallbackQueryHandler(message_handlers.cancel_save, pattern="^cancel#"))

register_handlers()
