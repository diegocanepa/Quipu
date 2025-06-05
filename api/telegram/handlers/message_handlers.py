import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from api.telegram.middlewere.require_onboarding import require_onboarding
from core.message_processor import MessageProcessor
from integrations.platforms.telegram_adapter import TelegramAdapter

logger = logging.getLogger(__name__)

message_processor = MessageProcessor()

# Variable set to know the stage of the conversation
CONFIRM_SAVE = 1


@require_onboarding
async def handle_text_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handles incoming messages from Telegram users, processes them using the LLMProcessor,
    and sends a separate response back to the user for each processed result.
    """
    telegram_adapter = TelegramAdapter(update)
    user_message = telegram_adapter.map_to_message()

    logger.info( f"Received message from user {user_message.user_id}: {user_message}")

    return await message_processor.process_and_respond(user_message, platform=telegram_adapter)


async def confirm_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback query handler para el botón de confirmar. Guarda los datos.

    Args:
        update (Update): The Telegram update object containing the callback query
        context (ContextTypes.DEFAULT_TYPE): The context object for the conversation

    Returns:
        int: ConversationHandler.END to end the conversation
    """
    telegram_adapter = TelegramAdapter(update)
    query = telegram_adapter.get_callback_query()
    user_id = telegram_adapter.get_user_id()
    logger.info("Processing confirm save callback", extra={
        "user_id": user_id,
        "callback_data": query.data,
        "message_id": query.message.message_id
    })

    await query.answer()

    # Extract callback_id
    callback_id = query.data.split("#")[1]
    logger.debug("Extracted callback_id", extra={
        "callback_id": callback_id,
        "user_id": user_id
    })

    response = message_processor.save_and_respond(
        user_id=user_id,
        message_id=callback_id,
        platform=telegram_adapter
    )

    await query.edit_message_text(text=response, parse_mode='HTML') # :TODO This is a edit message so I can't use the platform adapter
    return ConversationHandler.END


async def cancel_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback query handler para el botón de cancelar."""
    telegram_adapter = TelegramAdapter(update)
    query = telegram_adapter.get_callback_query()
    user_id = telegram_adapter.get_user_id()

    await query.answer()

    logger.info("Processing cancel callback", extra={
        "user_id": user_id,
        "callback_data": query.data,
        "message_id": query.message.message_id
    })
    # Extract callback_id
    callback_id = query.data.split("#")[1]
    logger.debug("Extracted callback_id", extra={
        "callback_id": callback_id,
        "user_id": user_id
    })

    response = message_processor.cancel_and_respond(user_id=user_id, message_id=callback_id, platform=telegram_adapter)

    await query.edit_message_text(text=response, parse_mode='HTML') # :TODO This is a edit message so I can't use the platform adapter
    return ConversationHandler.END
