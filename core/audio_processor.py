import logging
from typing import Optional

from core.interfaces.platform_adapter import PlatformAdapter
from integrations.transcriptor.client import TranscriptionServiceClient, TranscriptionServiceError

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    A class to handle the processing of audio files, including transcription.
    The TranscriptionServiceClient is initialized once when the AudioProcessor is created.
    """
    def __init__(self, base_url: str = None):
        self.transcription_client = TranscriptionServiceClient(base_url=base_url)
        logger.info("AudioProcessor initialized.")

    async def process_audio(self, platform: PlatformAdapter, audio_file_path: str) -> Optional[str]:
        """
        Reads an audio file, calls the transcription service, and processes the result.

        Args:
            audio_file_path: The path to the audio file to transcribe.
        """
        logger.info(f"Starting audio processing for file: {audio_file_path}")
        try:
            await platform.react_message("🎧")
            
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()

            transcription_result = await self.transcription_client.transcribe(audio_data)
            return transcription_result.transcription

        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_file_path}")
            return None
        except TranscriptionServiceError as e:
            logger.error(f"Error during transcription: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return None
        finally:
            await platform.delete_reaction()
