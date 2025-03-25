import logging
from telegram import Update
from core.llm_processor import LLMProcessor
from telegram.ext import ContextTypes
from config import config

logger = logging.getLogger(__name__)

llm_processor = LLMProcessor()

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echoes the user's message by making an HTTP request."""
    user_message = update.message.text
    logger.info(f"Received message from user {update.effective_user.id}: {user_message}")

    result = llm_processor.process_content(user_message)

    if result:
        result = result.model_dump()
        response_text = f"API Response: {result}"
        await update.message.reply_text(response_text)
    else:
        await update.message.reply_text("Hubo un error, intenta nuevamente!.")