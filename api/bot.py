import logging
from flask import Blueprint, request, jsonify
from telegram import Update
from config import config
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from bot import command_handlers, message_handlers
import asyncio

logger = logging.getLogger(__name__)

bp = Blueprint('bot', __name__, url_prefix='/bot')
telegram_app = None

def register_handlers(app):
    """Add handlers"""
    app.add_handler(CommandHandler("start", command_handlers.start))
    app.add_handler(CommandHandler("help", command_handlers.help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.echo))

async def initialize_telegram_app():
    global telegram_app
    if telegram_app is None:
        telegram_app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        register_handlers(telegram_app)
        await telegram_app.initialize()
        await telegram_app.start()
        logger.info("Telegram app initialized successfully.")


async def process_telegram_update(update: Update):
    try:
        await telegram_app.process_update(update)
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}", exc_info=True)

@bp.route('/webhook', methods=['POST'])
async def webhook():
    """Handles incoming webhook requests from Telegram."""
    try:
        global telegram_app
        if telegram_app is None:
            telegram_app = await initialize_telegram_app()

        data = request.get_json(force=True)
        update = Update.de_json(data, telegram_app.bot)
        asyncio.create_task(process_telegram_update(update))
        return jsonify({"status": "OK"}), 200

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        return jsonify({"status": "Error", "message": str(e)}), 500

async def shutdown_telegram_app():
    global telegram_app
    if telegram_app:
        await telegram_app.stop()
        await telegram_app.shutdown()
        logger.info("Telegram app shutdown successfully")
    