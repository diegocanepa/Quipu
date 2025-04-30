from flask import Blueprint, request, Response
from http import HTTPStatus
from telegram import Update
from bot.bot_instance import application
from bot import command_handlers
from bot import message_handlers
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters

telegram_bp = Blueprint("telegram", __name__)

# Registrar handlers
application.add_handler(CommandHandler("start", command_handlers.start))
application.add_handler(CommandHandler("help", command_handlers.help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.proccess_message))
application.add_handler(CallbackQueryHandler(message_handlers.confirm_save, pattern="^confirm#"))
application.add_handler(CallbackQueryHandler(message_handlers.cancel_save, pattern="^cancel#"))

@telegram_bp.route("/telegram", methods=["POST"])
async def telegram_webhook():
    update = Update.de_json(data=request.json, bot=application.bot)
    await application.update_queue.put(update)
    return Response(status=HTTPStatus.OK)
