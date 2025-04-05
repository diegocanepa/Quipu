import logging
from flask import Blueprint, request, jsonify
from telegram import Update
from config import config
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from bot import command_handlers, message_handlers

logger = logging.getLogger(__name__)

bp = Blueprint('bot', __name__, url_prefix='/bot')

def register_handlers(app: Application):
    """Add handlers"""
    app.add_handler(CommandHandler("start", command_handlers.start))
    app.add_handler(CommandHandler("help", command_handlers.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.echo))
    
async def initializes_telegram_app():
    telegram_app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    register_handlers(telegram_app)
    await telegram_app.initialize()
    await telegram_app.start()
    return telegram_app

@bp.route('/webhook', methods=['POST'])
async def webhook():
    """Handles incoming webhook requests from Telegram."""
    try:
        # Initializes Telegram Application.
        global telegram_app
        telegram_app = await initializes_telegram_app()
        
        # Hanlde request
        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return jsonify({"status": "OK"}), 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"status": "Error", "message": str(e)}), 500