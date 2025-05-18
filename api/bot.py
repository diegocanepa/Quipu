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
from api.handlers import command_handlers, message_handlers, audio_handlers
from config import config
from api.handlers.handlers import (
    onboarding_conv_handler,
    show_info,
    trigger_sheet_linking_cmd,
    trigger_webapp_linking_cmd,
    handle_unrecognized,
    help_command,
)

logger = logging.getLogger(__name__)

application = (
    Application.builder()
    .token(config.TELEGRAM_BOT_TOKEN)
    .updater(None) 
    .build()
)

def register_handlers(application):
    """Add command and conversation handlers"""
    
    # Order matters! The most specific handlers should often come first.
    # The ConversationHandler now includes the deeplink handling in its entry_points

    # 1. Onboarding Conversation Handler (handles all /start variants and the setup flow)
    application.add_handler(onboarding_conv_handler)
    logger.info("Added onboarding_conv_handler with deep linking support.")

    # 2. Command Handlers (can be used after onboarding)
    application.add_handler(CommandHandler("info", show_info))
    application.add_handler(CommandHandler("help", help_command))
    logger.info("Added info and help handlers.")

    # 3. Handlers for manually triggering linking after initial onboarding
    application.add_handler(CommandHandler("linksheet", trigger_sheet_linking_cmd))
    application.add_handler(CommandHandler("linkweb", trigger_webapp_linking_cmd))
    logger.info("Added manual linking command handlers (/linksheet, /linkweb).")

    # For all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.handle_text_message))
    
    # For voice messages
    application.add_handler(MessageHandler(filters.VOICE, audio_handlers.handle_audio_message))
    
    # For confirmation or cancelation
    application.add_handler(CallbackQueryHandler(message_handlers.confirm_save, pattern="^confirm#"))
    application.add_handler(CallbackQueryHandler(message_handlers.cancel_save, pattern="^cancel#"))
    
    # Last. Fallback Handler for unrecognized messages/commands
    application.add_handler(MessageHandler(filters.ALL, handle_unrecognized))
    logger.info("Added fallback handler for unrecognized messages.")

async def setup_webhook():
    """Set webhook URL for Telegram"""
    await application.bot.set_webhook(url=config.WEBHOOK_URL)

def get_application():
    return application