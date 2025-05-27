import logging

from telegram import Update
from telegram.ext import ContextTypes

from core.messages import BTN_GOOGLE_SHEET, BTN_WEBAPP, MSG_ONBOARDING_REQUIRED
from core.platforms.telegram_adapter import TelegramAdapter
from core.services.message_service import MessageService
from core.user_data_manager import UserDataManager

logger = logging.getLogger(__name__)

# Initialize UserDataManager
user_manager = UserDataManager()

# Create platform adapter and services
telegram_adapter = TelegramAdapter()
message_service = MessageService(telegram_adapter)


# --- Check Onboarding Status Helper ---
# This helper can be used inside protected handlers to quickly check status.
# A global middleware is more complex to integrate cleanly with ConversationHandler.
def require_onboarding(handler_func):
    """Decorator/Wrapper to check if user is onboarded before running handler."""

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user_manager.is_onboarding_complete(user.id):
            logger.debug(
                f"User {user.id} is onboarded. Proceeding with handler {handler_func.__name__}."
            )
            return await handler_func(update, context)
        else:
            logger.info(
                f"User {user.id} is NOT onboarded. Blocking handler {handler_func.__name__}."
            )
            create_user_if_not_exists(
                user.id, user.username, user.first_name, user.last_name
            )
            logger.info(f"User {user.id} created.")

            # Configurar el adaptador con el contexto de Telegram
            telegram_adapter.set_bot_context(context.bot, context)

            # Convertir la actualización de Telegram a formato agnóstico
            platform_update = telegram_adapter.convert_to_platform_update(update)

            # Establecer el contexto en el servicio de mensajería
            message_service.set_current_update_context(platform_update, context)

            buttons = [(BTN_GOOGLE_SHEET, "link_sheet"), (BTN_WEBAPP, "link_webapp")]

            await message_service.reply_with_keyboard(
                MSG_ONBOARDING_REQUIRED, buttons, parse_mode="HTML"
            )
            return

    return wrapper


def create_user_if_not_exists(user_id, username, first_name, last_name):
    user_exists = user_manager.get_user_data(user_id) is not None
    if not user_exists:
        user_manager.create_user(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
