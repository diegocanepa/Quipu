import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler, CallbackQueryHandler
from bot import command_handlers, message_handlers
from config import config

logger = logging.getLogger(__name__)

def register_handlers(app: Application):
    """Add handlers"""
    app.add_handler(CommandHandler("start", command_handlers.start))
    app.add_handler(CommandHandler("help", command_handlers.help_command))
    
def register_conversation_handlers(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.proccess_message)],
        states={
            message_handlers.CONFIRM_SAVE: [
                CallbackQueryHandler(message_handlers.confirm_save, pattern="^confirm_"),
                CallbackQueryHandler(message_handlers.cancel_save, pattern="^cancel_"),
            ],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)
    
def run_telegram_bot(): 
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    register_handlers(application)
    register_conversation_handlers(application)
    application.run_polling()
    