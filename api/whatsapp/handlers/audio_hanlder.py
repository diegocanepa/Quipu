import logging
import os
from typing import Optional

from pywa_async import WhatsApp, types
from core.audio_processor import AudioProcessor
from core.message_processor import MessageProcessor
from core.feature_flag import (
    FeatureFlagsEnum,
    get_disabled_message,
    is_feature_enabled,
)
from integrations.platforms.whatsapp_adapter import WhatsAppV2Adapter
from core.user_data_manager import UserDataManager
from api.whatsapp.messages import messages
from config import config

logger = logging.getLogger(__name__)

class WhatsAppV2AudioHandler:
    """
    Handles all audio-related operations for the WhatsApp v2 bot.
    This includes processing voice messages and managing audio transcriptions.
    """

    def __init__(self, wa: WhatsApp):
        """
        Initialize the audio handler with required processors.

        Args:
            wa: The WhatsApp client instance
        """
        self.wa = wa
        self.audio_processor = AudioProcessor()
        self.message_processor = MessageProcessor()
        self.user_manager = UserDataManager()

    async def handle_audio_message(self, message: types.Message) -> None:
        """
        Handles incoming voice messages and calls the audio processor.
        
        Args:
            message: The WhatsApp message object containing the voice message
        """
        platform = None
        platform_user_id = None
        message_id = None
        path = None
        
        try:
            # Initialize platform adapter without user
            platform = WhatsAppV2Adapter(self.wa, message, None)
            
            # Extract basic message info
            platform_user_id = platform.get_platform_user_id()
            message_id = platform.get_message_id()
            
            logger.info(f"Processing WhatsApp audio message. ID: {message_id}, User: {platform_user_id}")

            if not platform_user_id:
                logger.error(f"No user ID found in message. Message ID: {message_id}")
                return

            # Get user
            user = self.user_manager.get_user_by_whatsapp_user_id(platform_user_id)
            if not user:
                logger.info(f"New user registration required. User: {platform_user_id}")
                await platform.reply_text(messages.MSG_WELCOME.format(webapp_url=config.WEBAPP_BASE_URL))
                return

            # Update platform adapter with user
            platform = WhatsAppV2Adapter(self.wa, message, user)

            if not is_feature_enabled(FeatureFlagsEnum.AUDIO_TRANSCRIPTION):
                await platform.reply_text(
                    get_disabled_message(FeatureFlagsEnum.AUDIO_TRANSCRIPTION)
                )
                return

            # Get audio file
            audio = message.audio
            if not audio:
                logger.error(f"No audio found in message. ID: {message_id}")
                await platform.reply_text(messages.MSG_UNEXPECTED_ERROR)
                return

            # Download audio file
            path = await audio.download()

            # Process audio
            transcription_result = await self.audio_processor.process_audio(path)
            logger.info(f"Audio transcription result: {transcription_result}")
            
            if transcription_result:
                user_message = platform.map_to_message(message_text=transcription_result)
                await self.message_processor.process_and_respond(
                    user_message=user_message,
                    platform=platform
                )
            else:
                await platform.reply_text(messages.MSG_VOICE_NO_TEXT)

        except Exception as e:
            logger.error(f"Error handling voice message. User: {platform_user_id}, Message ID: {message_id}, Error: {str(e)}")
            if platform:
                await platform.reply_text(messages.MSG_VOICE_PROCESSING_ERROR)
        finally:
            # Clean up the audio file if it exists
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Error removing temporary audio file {path}: {str(e)}")
