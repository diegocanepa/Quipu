import logging
from typing import List
from telegram import Update
from core.llm_processor import LLMProcessor, ProcessingResult
from telegram.ext import ContextTypes
from config import config

logger = logging.getLogger(__name__)

llm_processor = LLMProcessor()


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """    
    Handles incoming messages from Telegram users, processes them using the LLMProcessor,
    and sends a separate response back to the user for each processed result.
    """
    
    user_message = update.message.text
    logger.info(f"Received message from user {update.effective_user.id}: {user_message}")

    results: List[ProcessingResult] = await llm_processor.process_content(user_message)

    if not results:
        await update.message.reply_text("❌ Hubo un error inesperado durante el procesamiento.", parse_mode='MarkdownV2')
        return
    
    for result in results:
        if result.error is None:
            response_text = format_processing_result(result)
            await update.message.reply_text(response_text, parse_mode='MarkdownV2')
        else:
            await update.message.reply_text(f'Hubo un error procesando el mensaje: {result.error}.')
            
def format_processing_result(result: ProcessingResult) -> str:
    """
    Formats a ProcessingResult object into the desired user-friendly message with emojis.
    """
    if result.error:
        return f"❌ {result.error}"
    
    formatted_data = result.data_object.to_formatted_string()
    status_spreadsheet = "✅ Spreedsheet" if result.saved_to_spreadsheet else "⚠️ Spreedsheet"
    status_database = "✅ Base de datos" if result.saved_to_database else "⚠️ Base de datos"
    return f"{formatted_data}\n\n{status_spreadsheet}\n{status_database}"