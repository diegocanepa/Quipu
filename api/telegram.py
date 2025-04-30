from flask import Flask, request, Response
from telegram import Update
from bot.bot_instance import application

flask_app = Flask(__name__)

@flask_app.post("/telegram")
async def telegram_webhook():
    update = Update.de_json(data=request.json, bot=application.bot)
    await application.update_queue.put(update)
    return Response(status=200)

app = flask_app  # Vercel necesita esto
