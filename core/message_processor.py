# core/message_processor.py
import logging
from typing import List

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from core.llm_processor import LLMProcessor, ProcessingResult
from core.platforms.telegram_adapter import TelegramAdapter
from core.services.message_service import MessageService

logger = logging.getLogger(__name__)

CONFIRM_SAVE = 1


class MessageProcessor:
    def __init__(self):
        self.llm_processor = LLMProcessor()
        # Crear el adaptador de Telegram
        self.telegram_adapter = TelegramAdapter()
        # Crear el servicio de mensajería usando el adaptador
        self.message_service = MessageService(self.telegram_adapter)

    async def process_and_respond(
        self, user_message: str, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Processes the user's message using the LLMProcessor and sends responses
        with confirmation options using the platform adapter.

        Args:
            update: The Telegram Update object.
            context: The Telegram Context object.

        Returns:
            int: The state for the conversation handler (CONFIRM_SAVE).
        """
        # Configurar el adaptador con el contexto de Telegram
        self.telegram_adapter.set_bot_context(context.bot, context)

        # Convertir la actualización de Telegram a formato agnóstico
        platform_update = self.telegram_adapter.convert_to_platform_update(update)

        # Establecer el contexto en el servicio de mensajería
        self.message_service.set_current_update_context(platform_update, context)

        results: List[ProcessingResult] = await self.llm_processor.process_content(
            user_message
        )

        if not results:
            await self.message_service.reply_to_current_message(
                "❌ Hubo un error inesperado durante el procesamiento.",
                parse_mode="MarkdownV2",
            )
            return ConversationHandler.END

        for idx, result in enumerate(results):
            if result.error:
                await self.message_service.reply_to_current_message(
                    f"❌ {result.error}", parse_mode="MarkdownV2"
                )
            else:
                response_text = result.data_object.to_presentation_string()
                callback_id = f"{update.message.message_id}_{idx}"

                buttons = [
                    ("✅ Confirmar", f"confirm#{callback_id}"),
                    ("❌ Cancelar", f"cancel#{callback_id}"),
                ]

                sent_message = await self.message_service.reply_with_keyboard(
                    response_text, buttons, parse_mode="MarkdownV2"
                )

                context.user_data[f"pendingsave#{callback_id}"] = result.data_object
                context.user_data[f"messageid#{callback_id}"] = sent_message.message_id

        return CONFIRM_SAVE
