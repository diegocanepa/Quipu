from telegram.ext import Application
from config import config

application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).updater(None).build()
