# In your main bot file (e.g., api/bot.py)
import logging
import os

from telegram import Update
from telegram.ext import ContextTypes

from api.telegram.middlewere.require_onboarding import require_onboarding
from core.audio_processor import AudioProcessor
from core.feature_flag import (
    FeatureFlagsEnum,
    get_disabled_message,
    is_feature_enabled,
)
from core.message_processor import MessageProcessor
from integrations.platforms.telegram_adapter import TelegramAdapter
from core.messages import MSG_VOICE_NO_TEXT, MSG_VOICE_PROCESSING_ERROR

logger = logging.getLogger(__name__)

class AudioHandlers:
    """
    Handles all audio-related operations for the Telegram bot.
    This includes processing voice messages and managing audio transcriptions.
    """

    def __init__(self):
        """Initialize the audio handlers with required processors."""
        self.audio_processor = AudioProcessor()
        self.message_processor = MessageProcessor()

    @require_onboarding
    async def handle_audio_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handles incoming voice messages and calls the audio processor.
        
        Args:
            update (Update): The Telegram update object containing the voice message
            context (ContextTypes.DEFAULT_TYPE): The context object for the conversation
        """
        user = context.user_data.get('current_user')
        telegram_adapter = TelegramAdapter(update, user)

        if not is_feature_enabled(FeatureFlagsEnum.AUDIO_TRANSCRIPTION):
            await telegram_adapter.reply_text(
                get_disabled_message(FeatureFlagsEnum.AUDIO_TRANSCRIPTION)
            )
            return

        user_id = telegram_adapter.get_user().id
        file_id = telegram_adapter.get_voice_file_id()
        logger.info(f"Voice message received from user {user_id} with file ID: {file_id}")

        try:
            # Get the File object from Telegram
            file = await context.bot.get_file(file_id)
            filename = f"voice_{user_id}.ogg"

            # Download directly to local disk (avoiding requests and URL)
            await file.download_to_drive(custom_path=filename)

            # Process audio
            transcription_result = await self.audio_processor.process_audio(filename)
            logger.info(transcription_result)
            os.remove(filename)
            
            message = telegram_adapter.map_to_message(message_text=transcription_result)

            if transcription_result:
                await self.message_processor.process_and_respond(user_message=message, platform=telegram_adapter)
            else:
                await telegram_adapter.reply_text(MSG_VOICE_NO_TEXT)

        except Exception as e:
            logger.error(f"Error handling voice message: {e}")
            await telegram_adapter.reply_text(MSG_VOICE_PROCESSING_ERROR)

# Create a singleton instance
audio_handlers = AudioHandlers()
