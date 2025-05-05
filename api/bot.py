import logging
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from bot import command_handlers, message_handlers, audio_handlers
from config import config

logger = logging.getLogger(__name__)

application = (
    Application.builder()
    .token(config.TELEGRAM_BOT_TOKEN)
    .updater(None) 
    .build()
)


def register_handlers(application):
    """Add command and conversation handlers"""
    application.add_handler(CommandHandler("start", command_handlers.start))
    application.add_handler(CommandHandler("help", command_handlers.help_command))
    
    # For all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.handle_text_message))
    
    # For voice messages
    application.add_handler(MessageHandler(filters.VOICE, audio_handlers.handle_audio_message))

    # For confirmation or cancelation
    application.add_handler(CallbackQueryHandler(message_handlers.confirm_save, pattern="^confirm#"))
    application.add_handler(CallbackQueryHandler(message_handlers.cancel_save, pattern="^cancel#"))

async def setup_webhook():
    """Set webhook URL for Telegram"""
    await application.bot.set_webhook(url=config.WEBHOOK_URL)

def get_application():
    return application
