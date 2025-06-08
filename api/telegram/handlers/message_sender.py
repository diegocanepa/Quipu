import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from core import messages

logger = logging.getLogger(__name__)

class MessageSender:
    @staticmethod
    async def send_message(update: Update, text: str, keyboard=None, disable_preview=False) -> None:
        """Helper to send messages with consistent formatting."""
        return await update.effective_message.reply_text(
            text,
            parse_mode='HTML',
            reply_markup=keyboard,
            disable_web_page_preview=disable_preview
        )

    @staticmethod
    def create_keyboard(buttons: list) -> InlineKeyboardMarkup:
        """Helper to create inline keyboards consistently."""
        return InlineKeyboardMarkup([[InlineKeyboardButton(text, callback_data=data)] for text, data in buttons])


    @staticmethod
    async def clean_up_processing_message(processing_msg) -> None:
        """Helper to handle processing messages with cleanup."""
        try:
            await processing_msg.delete()
        except Exception as e:
            logger.warning(f"Failed to delete processing message: {e}")