# In your main bot file (e.g., api/bot.py)
import logging
import os
import requests
from telegram import Update
from telegram.ext import ContextTypes
from core.audio_processor import AudioProcessor
from core.message_processor import MessageProcessor
from api.middlewere.require_onboarding import require_onboarding

logger = logging.getLogger(__name__)

# Initialize the AudioProcessor when your bot application starts
audio_processor = AudioProcessor()
message_processor = MessageProcessor()

@require_onboarding
async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming voice messages and calls the audio processor."""
    user_id = update.effective_user.id
    voice = update.message.voice
    file_id = voice.file_id
    logger.info(f"Voice message received from user {user_id} with file ID: {file_id}")

    try:
        # Get the File object from Telegram
        file = await context.bot.get_file(file_id)
        filename = f"voice_{user_id}.ogg"

        # Download directly to local disk (avoiding requests and URL)
        await file.download_to_drive(custom_path=filename)

        # Process audio
        transcription_result = await audio_processor.process_audio(filename)
        os.remove(filename)

        if transcription_result:
            await message_processor.process_and_respond(user_message=transcription_result, update=update, context=context)
        else:
            await update.message.reply_text("Voice processed, but no transcription text was found in the result.")

    except Exception as e:
        logger.error(f"Error handling voice message: {e}")
        await update.message.reply_text("Sorry, there was an error processing the voice message.")
