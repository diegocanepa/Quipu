import logging

from telegram import Update
from telegram.ext import ContextTypes

from core import messages
from core.platforms.telegram_adapter import TelegramAdapter
from core.services.message_service import MessageService
from core.services.onboarding_service import OnboardingService
from core.user_data_manager import UserDataManager

logger = logging.getLogger(__name__)

# Initialize managers and services
user_manager = UserDataManager()

# Create platform adapter and services
telegram_adapter = TelegramAdapter()
message_service = MessageService(telegram_adapter)
onboarding_service = OnboardingService(message_service)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command. Displays the help message."""
    # Configurar el adaptador con el contexto de Telegram
    telegram_adapter.set_bot_context(context.bot, context)

    # Convertir la actualización de Telegram a formato agnóstico
    platform_update = telegram_adapter.convert_to_platform_update(update)

    # Establecer el contexto en el servicio de mensajería
    message_service.set_current_update_context(platform_update, context)

    await message_service.reply_to_current_message(messages.MSG_HELP_TEXT)


async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /info command. Shows the user's current linking status."""
    # Configurar el adaptador con el contexto de Telegram
    telegram_adapter.set_bot_context(context.bot, context)

    # Convertir la actualización de Telegram a formato agnóstico
    platform_update = telegram_adapter.convert_to_platform_update(update)

    # Establecer el contexto en el servicio de mensajería
    message_service.set_current_update_context(platform_update, context)

    # Usar el servicio de onboarding para mostrar la información
    await onboarding_service.show_user_info(platform_update.user)


async def handle_unrecognized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles messages/commands that don't match any specific handler."""
    # Configurar el adaptador con el contexto de Telegram
    telegram_adapter.set_bot_context(context.bot, context)

    # Convertir la actualización de Telegram a formato agnóstico
    platform_update = telegram_adapter.convert_to_platform_update(update)

    # Establecer el contexto en el servicio de mensajería
    message_service.set_current_update_context(platform_update, context)

    user_id = int(platform_update.user.platform_user_id)
    text = platform_update.message.text if platform_update.message else ""

    # IMPORTANT: Check if the user is currently in the onboarding conversation
    if context.user_data.get("onboarding_in_progress"):
        logger.debug(
            f"User {user_id} sent unrecognized message '{text}', but in onboarding conversation."
        )
        return
    else:
        # User is not in onboarding conversation. Check if they are onboarded.
        if not user_manager.is_onboarding_complete(user_id):
            logger.info(
                f"User {user_id} sent unrecognized message '{text}' and is not onboarded."
            )
            await message_service.reply_to_current_message(
                messages.MSG_ONBOARDING_REQUIRED + "\n\n Use /start para comenzar! ✨"
            )
        else:
            logger.info(
                f"User {user_id} sent unrecognized message '{text}' and IS onboarded."
            )
            # User is onboarded but sent something the bot doesn't recognize
            if text.startswith("/"):
                await message_service.reply_to_current_message(
                    messages.MSG_UNKNOWN_COMMAND
                )
            else:
                await message_service.reply_to_current_message(
                    messages.MSG_UNKNOWN_MESSAGE
                )
