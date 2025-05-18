import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from core.user_data_manager import UserDataManager
from telegram.ext import ContextTypes
from core.messages import MSG_ONBOARDING_REQUIRED, BTN_GOOGLE_SHEET, BTN_WEBAPP

logger = logging.getLogger(__name__)

# Initialize UserDataManager
user_manager = UserDataManager()

# --- Check Onboarding Status Helper ---
# This helper can be used inside protected handlers to quickly check status.
# A global middleware is more complex to integrate cleanly with ConversationHandler.
def require_onboarding(handler_func):
    """Decorator/Wrapper to check if user is onboarded before running handler."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_manager.is_onboarding_complete(user_id):
            logger.debug(f"User {user_id} is onboarded. Proceeding with handler {handler_func.__name__}.")
            return await handler_func(update, context)
        else:
            logger.info(f"User {user_id} is NOT onboarded. Blocking handler {handler_func.__name__}.")
            keyboard = [
                [InlineKeyboardButton(BTN_GOOGLE_SHEET, callback_data='link_sheet')],
                [InlineKeyboardButton(BTN_WEBAPP, callback_data='link_webapp')]
            ]
            await update.effective_message.reply_text(MSG_ONBOARDING_REQUIRED, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
            # Optionally, redirect them to start onboarding if they aren't already in the process
            # Note: ConversationHandler might already be active, checking context.user_data is needed for complex cases.
            # For simplicity here, we just send the message. The main /start handler handles the initial entry.
            return
    return wrapper