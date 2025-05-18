import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core import messages
from config import config

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
    def get_error_keyboard(current_state: str) -> InlineKeyboardMarkup:
        """Helper to get appropriate error keyboard based on state."""
        from core.onboarding import states  # Import here to avoid circular imports
        
        if current_state == states.GOOGLE_SHEET_AWAITING_URL:
            buttons = [
                (messages.BTN_SWITCH_TO_WEBAPP, 'switch_to_webapp'),
                (messages.BTN_CANCEL_ONBOARDING, 'cancel_onboarding')
            ]
        elif current_state == states.WEBAPP_SHOWING_INSTRUCTIONS:
            buttons = [
                (messages.BTN_SWITCH_TO_SHEET, 'switch_to_sheet'),
                (messages.BTN_CANCEL_ONBOARDING, 'cancel_onboarding')
            ]
        else:
            buttons = [(messages.BTN_CANCEL_ONBOARDING, 'cancel_onboarding')]
        
        return MessageSender.create_keyboard(buttons)

    @staticmethod
    async def clean_up_processing_message(processing_msg) -> None:
        """Helper to handle processing messages with cleanup."""
        try:
            await processing_msg.delete()
        except Exception as e:
            logger.warning(f"Failed to delete processing message: {e}")