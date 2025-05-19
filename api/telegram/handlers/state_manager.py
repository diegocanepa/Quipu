import logging
from telegram.ext import ContextTypes, ConversationHandler
from core.onboarding import states
from telegram import Update

logger = logging.getLogger(__name__)

class StateManager:
    @staticmethod
    def set_conversation_state(context: ContextTypes.DEFAULT_TYPE, state, in_progress: bool = True) -> None:
        """Helper to set conversation state consistently."""
        context.user_data['onboarding_in_progress'] = in_progress
        context.user_data['onboarding_state'] = state

    @staticmethod
    def get_current_state(context: ContextTypes.DEFAULT_TYPE) -> str:
        """Helper to get current conversation state."""
        return context.user_data.get('onboarding_state', states.CHOOSING_LINK_METHOD)

    @staticmethod
    async def end_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE, success_message: str) -> int:
        """Helper to handle successful onboarding completion."""
        from api.telegram.handlers.message_sender import MessageSender  # Import here to avoid circular imports
        
        StateManager.set_conversation_state(context, states.FINISHED, False)
        await MessageSender.send_message(update, success_message)
        return ConversationHandler.END