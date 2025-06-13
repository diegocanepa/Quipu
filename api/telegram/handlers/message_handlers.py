import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from api.telegram.middlewere.require_onboarding import require_onboarding
from core.message_processor import MessageProcessor
from integrations.platforms.telegram_adapter import TelegramAdapter

logger = logging.getLogger(__name__)

# Variable set to know the stage of the conversation
CONFIRM_SAVE = 1

class MessageHandlers:
    """
    Handles all message-related operations for the Telegram bot.
    This includes processing text messages and handling save confirmations/cancellations.
    """

    def __init__(self):
        """Initialize the message handlers with a message processor."""
        self.message_processor = MessageProcessor()

    @require_onboarding
    async def handle_text_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handles incoming messages from Telegram users, processes them using the LLMProcessor,
        and sends a separate response back to the user for each processed result.
        """
        user = context.user_data.get('current_user')
        telegram_adapter = TelegramAdapter(update, user)
        user_message = telegram_adapter.map_to_message()

        logger.info(f"Received message from user {user_message.user_id}: {user_message}")

        return await self.message_processor.process_and_respond(user_message, platform=telegram_adapter)

    @require_onboarding
    async def confirm_save(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Callback query handler for the confirm button. Saves the data.

        Args:
            update (Update): The Telegram update object containing the callback query
            context (ContextTypes.DEFAULT_TYPE): The context object for the conversation

        Returns:
            int: ConversationHandler.END to end the conversation
        """
        user = context.user_data.get('current_user')
        telegram_adapter = TelegramAdapter(update, user)
        query = telegram_adapter.get_callback_query()
        user = telegram_adapter.get_user()
        
        logger.info("Processing confirm save callback", extra={
            "user_id": user.id,
            "callback_data": query.data,
            "message_id": query.message.message_id
        })

        await query.answer()

        # Extract callback_id
        callback_id = query.data.split("#")[1]
        logger.debug("Extracted callback_id", extra={
            "callback_id": callback_id,
            "user_id": user.id
        })

        response = self.message_processor.save_and_respond(
            user_id=user.id,
            message_id=callback_id,
            platform=telegram_adapter
        )

        await query.edit_message_text(text=response, parse_mode='HTML')
        return ConversationHandler.END

    @require_onboarding
    async def cancel_save(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Callback query handler for the cancel button.

        Args:
            update (Update): The Telegram update object containing the callback query
            context (ContextTypes.DEFAULT_TYPE): The context object for the conversation

        Returns:
            int: ConversationHandler.END to end the conversation
        """
        user = context.user_data.get('current_user')
        telegram_adapter = TelegramAdapter(update, user)
        query = telegram_adapter.get_callback_query()
        user_id = telegram_adapter.get_user().id

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

        response = self.message_processor.cancel_and_respond(
            user_id=user_id, 
            message_id=callback_id, 
            platform=telegram_adapter
        )

        await query.edit_message_text(text=response, parse_mode='HTML')
        return ConversationHandler.END

# Create a singleton instance
message_handlers = MessageHandlers()
