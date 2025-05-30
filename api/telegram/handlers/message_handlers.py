import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from api.telegram.middlewere.require_onboarding import require_onboarding
from core.data_server import DataSaver
from core.message_processor import MessageProcessor
from core.user_data_manager import UserDataManager
from integrations.platforms.telegram_adapter import TelegramAdapter

logger = logging.getLogger(__name__)

message_processor = MessageProcessor()
data_saver = DataSaver()
user_data_manager = UserDataManager()

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

    user_message = telegram_adapter.get_message_text()
    logger.info(
        f"Received message from user {telegram_adapter.get_user_id()}: {user_message}"
    )

    return await message_processor.process_and_respond(
        user_message, platform=telegram_adapter, context=context
    )


async def confirm_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback query handler para el botón de confirmar. Guarda los datos."""
    telegram_adapter = TelegramAdapter(update)

    query = telegram_adapter.get_callback_query()
    user = telegram_adapter.get_user()
    await query.answer()
    logger.info(f"Callback Query Data (Confirm): {query.data}")

    # Extract callback_id
    callback_id = query.data.split("#")[1]

    if f"messageid#{callback_id}" in context.user_data:
        original_message_id = context.user_data[f"messageid#{callback_id}"]

        if (
            original_message_id == query.message.message_id
            and f"pendingsave#{callback_id}" in context.user_data
        ):
            data_to_save = context.user_data[f"pendingsave#{callback_id}"]

            logger.info(f"Mensaje a guardar: {data_to_save} from user {user.id}")

            db_user = user_data_manager.get_user_data(user.id)

            success = data_saver.save_content(data_to_save, db_user)
            original_text = query.message.text

            if success:
                await query.edit_message_text(
                    text=f"{original_text}\n\n✅ Guardado correctamente"
                )
            else:
                await query.edit_message_text(
                    text=f"{original_text}\n\n❌ Error al guardar"
                )
        else:
            await query.edit_message_text(text="❌ La confirmación ha expirado.")
    else:
        await query.edit_message_text(text="❌ No se encontró el mensaje original.")

    # Clean message data
    context.user_data.pop(f"pendingsave#{callback_id}", None)
    context.user_data.pop(f"messageid#{callback_id}", None)

    return ConversationHandler.END


async def cancel_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback query handler para el botón de cancelar."""
    telegram_adapter = TelegramAdapter(update)

    query = telegram_adapter.get_callback_query()
    await query.answer()
    logger.info(f"Callback Query Data (Cancel): {query.data}")

    # Extract callback_id
    callback_id = query.data.split("#")[1]

    # Cancel messae
    await query.edit_message_text(text="❌ Acción cancelada.")

    # Clean message data
    context.user_data.pop(f"pendingsave#{callback_id}", None)
    context.user_data.pop(f"messageid#{callback_id}", None)

    return ConversationHandler.END
