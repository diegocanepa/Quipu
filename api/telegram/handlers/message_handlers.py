import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from api.telegram.middlewere.require_onboarding import require_onboarding
from core.data_server import DataSaver
from core.message_processor import MessageProcessor
from core.platforms.telegram_adapter import TelegramAdapter
from core.services.message_service import MessageService
from core.user_data_manager import UserDataManager

logger = logging.getLogger(__name__)

message_processor = MessageProcessor()
data_saver = DataSaver()
user_data_manager = UserDataManager()

# Create platform adapter and services for callback handlers
telegram_adapter = TelegramAdapter()
message_service = MessageService(telegram_adapter)

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

    user_message = update.message.text
    logger.info(
        f"Received message from user {update.effective_user.id}: {user_message}"
    )

    return await message_processor.process_and_respond(
        user_message, update=update, context=context
    )


async def confirm_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback query handler para el botón de confirmar. Guarda los datos."""
    query = update.callback_query
    user = update.effective_user
    await query.answer()
    logger.info(f"Callback Query Data (Confirm): {query.data}")

    # Configurar el adaptador con el contexto de Telegram
    telegram_adapter.set_bot_context(context.bot, context)

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
                new_text = f"{original_text}\n\n✅ Guardado correctamente"
            else:
                new_text = f"{original_text}\n\n❌ Error al guardar"

            # Usar el adaptador para editar el mensaje
            await telegram_adapter.edit_message(
                str(query.message.message_id),
                new_text,
                chat_id=str(query.message.chat_id),
            )
        else:
            await telegram_adapter.edit_message(
                str(query.message.message_id),
                "❌ La confirmación ha expirado.",
                chat_id=str(query.message.chat_id),
            )
    else:
        await telegram_adapter.edit_message(
            str(query.message.message_id),
            "❌ No se encontró el mensaje original.",
            chat_id=str(query.message.chat_id),
        )

    # Clean message data
    context.user_data.pop(f"pendingsave#{callback_id}", None)
    context.user_data.pop(f"messageid#{callback_id}", None)

    return ConversationHandler.END


async def cancel_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback query handler para el botón de cancelar."""
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback Query Data (Cancel): {query.data}")

    # Configurar el adaptador con el contexto de Telegram
    telegram_adapter.set_bot_context(context.bot, context)

    # Extract callback_id
    callback_id = query.data.split("#")[1]

    # Cancel message usando el adaptador
    await telegram_adapter.edit_message(
        str(query.message.message_id),
        "❌ Acción cancelada.",
        chat_id=str(query.message.chat_id),
    )

    # Clean message data
    context.user_data.pop(f"pendingsave#{callback_id}", None)
    context.user_data.pop(f"messageid#{callback_id}", None)

    return ConversationHandler.END
