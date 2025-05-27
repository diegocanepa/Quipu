import logging
from typing import Any, List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from core.interfaces.messaging_platform import (
    MessagingPlatformInterface,
    PlatformMessage,
    PlatformUpdate,
    PlatformUser,
)

logger = logging.getLogger(__name__)


class TelegramAdapter(MessagingPlatformInterface):
    """Adaptador específico para la plataforma Telegram"""

    def __init__(self, bot_instance=None, context: ContextTypes.DEFAULT_TYPE = None):
        self.bot = bot_instance
        self.context = context

    def set_bot_context(self, bot_instance, context: ContextTypes.DEFAULT_TYPE):
        """Establece el bot y contexto de Telegram"""
        self.bot = bot_instance
        self.context = context

    async def send_message(self, user_id: str, text: str, **kwargs) -> Any:
        """Envía un mensaje de texto al usuario en Telegram"""
        parse_mode = kwargs.get("parse_mode", "HTML")
        disable_preview = kwargs.get("disable_preview", False)

        return await self.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_preview,
        )

    async def send_message_with_keyboard(
        self, user_id: str, text: str, buttons: List[tuple], **kwargs
    ) -> Any:
        """Envía un mensaje con teclado inline en Telegram"""
        parse_mode = kwargs.get("parse_mode", "HTML")
        disable_preview = kwargs.get("disable_preview", False)

        keyboard = [
            [InlineKeyboardButton(text, callback_data=data)] for text, data in buttons
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        return await self.bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            disable_web_page_preview=disable_preview,
        )

    async def edit_message(self, message_id: str, text: str, **kwargs) -> Any:
        """Edita un mensaje existente en Telegram"""
        # En Telegram necesitamos el chat_id y message_id
        chat_id = kwargs.get("chat_id")
        if not chat_id:
            raise ValueError("chat_id is required for editing Telegram messages")

        return await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=kwargs.get("parse_mode", "HTML"),
        )

    async def answer_callback_query(
        self, callback_query_id: str, text: Optional[str] = None
    ) -> Any:
        """Responde a una consulta de callback en Telegram"""
        return await self.bot.answer_callback_query(
            callback_query_id=callback_query_id, text=text
        )

    async def get_voice_file_data(self, voice_message_data: Any) -> Optional[bytes]:
        """Obtiene los datos de un archivo de voz de Telegram"""
        try:
            file = await self.bot.get_file(voice_message_data.file_id)
            return await file.download_as_bytearray()
        except Exception as e:
            logger.error(f"Error downloading voice file: {e}")
            return None

    def convert_to_platform_update(self, telegram_update: Update) -> PlatformUpdate:
        """Convierte una actualización de Telegram a formato agnóstico"""
        platform_update = PlatformUpdate()

        # Convertir usuario
        if telegram_update.effective_user:
            platform_update.user = PlatformUser(
                platform_user_id=str(telegram_update.effective_user.id),
                username=telegram_update.effective_user.username,
                first_name=telegram_update.effective_user.first_name,
                last_name=telegram_update.effective_user.last_name,
                platform_type="telegram",
            )

        # Convertir mensaje
        if telegram_update.message:
            platform_update.message = PlatformMessage(
                text=telegram_update.message.text,
                user=platform_update.user,
                message_id=str(telegram_update.message.message_id),
                is_voice=bool(telegram_update.message.voice),
                voice_file_data=telegram_update.message.voice
                if telegram_update.message.voice
                else None,
            )

        # Convertir callback query
        if telegram_update.callback_query:
            platform_update.callback_query = {
                "id": telegram_update.callback_query.id,
                "data": telegram_update.callback_query.data,
                "message_id": str(telegram_update.callback_query.message.message_id)
                if telegram_update.callback_query.message
                else None,
                "chat_id": str(telegram_update.callback_query.message.chat_id)
                if telegram_update.callback_query.message
                else None,
            }

        return platform_update
