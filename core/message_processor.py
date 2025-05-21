# core/message_processor.py
import logging
from typing import List
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from core.llm_processor import LLMProcessor, ProcessingResult

logger = logging.getLogger(__name__)

CONFIRM_SAVE = 1

class MessageProcessor:
    def __init__(self):
        self.llm_processor = LLMProcessor()

    async def process_and_respond(self, user_message: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Processes the user's message using the LLMProcessor and sends responses
        with confirmation options.

        Args:
            update: The Telegram Update object.
            context: The Telegram Context object.

        Returns:
            int: The state for the conversation handler (CONFIRM_SAVE).
        """
        results: List[ProcessingResult] = await self.llm_processor.process_content(user_message)

        if not results:
            await update.message.reply_text("❌ Hubo un error inesperado durante el procesamiento.", parse_mode='MarkdownV2')
            return ConversationHandler.END

        for idx, result in enumerate(results):
            if result.error:
                await update.message.reply_text(f"❌ {result.error}", parse_mode='MarkdownV2')
            else:
                response_text = result.data_object.to_presentation_string()
                callback_id = f"{update.message.message_id}_{idx}"

                keyboard = [
                    [InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm#{callback_id}")],
                    [InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel#{callback_id}")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                sent_message = await update.message.reply_text(response_text, parse_mode='MarkdownV2', reply_markup=reply_markup)

                context.user_data[f'pendingsave#{callback_id}'] = result.data_object
                context.user_data[f'messageid#{callback_id}'] = sent_message.message_id

        return CONFIRM_SAVE 
