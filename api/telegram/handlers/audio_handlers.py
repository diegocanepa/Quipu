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
from core.platforms.telegram_adapter import TelegramAdapter
from core.services.message_service import MessageService

logger = logging.getLogger(__name__)

# Initialize the AudioProcessor when your bot application starts
audio_processor = AudioProcessor()
message_processor = MessageProcessor()

# Create platform adapter and services
telegram_adapter = TelegramAdapter()
message_service = MessageService(telegram_adapter)


@require_onboarding
async def handle_audio_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles incoming voice messages and calls the audio processor."""

    if not is_feature_enabled(FeatureFlagsEnum.AUDIO_TRANSCRIPTION):
        # Configurar el adaptador con el contexto de Telegram
        telegram_adapter.set_bot_context(context.bot, context)

        # Convertir la actualización de Telegram a formato agnóstico
        platform_update = telegram_adapter.convert_to_platform_update(update)

        # Establecer el contexto en el servicio de mensajería
        message_service.set_current_update_context(platform_update, context)

        await message_service.reply_to_current_message(
            get_disabled_message(FeatureFlagsEnum.AUDIO_TRANSCRIPTION)
        )
        return

    user_id = update.effective_user.id
    voice = update.message.voice
    file_id = voice.file_id
    logger.info(f"Voice message received from user {user_id} with file ID: {file_id}")

    try:
        # Configurar el adaptador con el contexto de Telegram
        telegram_adapter.set_bot_context(context.bot, context)

        # Convertir la actualización de Telegram a formato agnóstico
        platform_update = telegram_adapter.convert_to_platform_update(update)

        # Establecer el contexto en el servicio de mensajería
        message_service.set_current_update_context(platform_update, context)

        # Get voice file data using the adapter
        voice_data = await telegram_adapter.get_voice_file_data(voice)

        if voice_data:
            # Save voice data to temporary file
            filename = f"voice_{user_id}.ogg"
            with open(filename, "wb") as f:
                f.write(voice_data)

            # Process audio
            transcription_result = await audio_processor.process_audio(filename)
            os.remove(filename)

            if transcription_result:
                await message_processor.process_and_respond(
                    user_message=transcription_result, update=update, context=context
                )
            else:
                await message_service.reply_to_current_message(
                    "Voice processed, but no transcription text was found in the result."
                )
        else:
            await message_service.reply_to_current_message(
                "Error downloading voice file."
            )

    except Exception as e:
        logger.error(f"Error handling voice message: {e}")
        await message_service.reply_to_current_message(
            "Sorry, there was an error processing the voice message."
        )
