import logging
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackQueryHandler,
)
from api.telegram.handlers import command_handlers, message_handlers, audio_handlers
from config import config
from api.telegram.handlers.onboarding_handlers import onboarding_conv_handler

logger = logging.getLogger(__name__)

application = (
    Application.builder()
    .token(config.TELEGRAM_BOT_TOKEN)
    .updater(None) 
    .build()
)

def register_handlers(application):
    """
    Add command and conversation handlers for the bot.
    Order matters! The most specific handlers should often come first.
    """

    # 1. Onboarding Conversation Handler (handles all /start variants and the setup flow)
    application.add_handler(onboarding_conv_handler)
    logger.info("Added onboarding_conv_handler with deep linking support.")

    # 2. Command Handlers (can be used after onboarding)
    application.add_handler(CommandHandler("info", command_handlers.show_info))
    application.add_handler(CommandHandler("help", command_handlers.help_command))
    logger.info("Added info and help handlers.")

    # 3. For all text messages (not commands) and confirmation or cancelation of transactions
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.handle_text_message))
    application.add_handler(CallbackQueryHandler(message_handlers.confirm_save, pattern="^confirm#"))
    application.add_handler(CallbackQueryHandler(message_handlers.cancel_save, pattern="^cancel#"))
    logger.info("Added text message handlers and confirmation and cancelation handlers.")
    
    # 4. For voice messages
    application.add_handler(MessageHandler(filters.VOICE, audio_handlers.handle_audio_message))
    logger.info("Added voice message handler.")
    
    # Last. Fallback Handler for unrecognized messages/commands
    application.add_handler(MessageHandler(filters.ALL, command_handlers.handle_unrecognized))
    logger.info("Added fallback handler for unrecognized messages.")

async def setup_webhook():
    """Set webhook URL for Telegram"""
    await application.bot.set_webhook(url=config.WEBHOOK_URL)

def get_application():
    return application