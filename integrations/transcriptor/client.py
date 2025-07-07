from dataclasses import dataclass
from logging_config import get_logger
from config import config

import aiohttp

# Configure logging
logger = get_logger(__name__)

class TranscriptionServiceError(Exception):
    """Custom exception for errors during transcription service interaction."""
    pass

class HttpRequestError(TranscriptionServiceError):
    """Exception for errors during HTTP requests."""
    pass

class InvalidApiResponseError(TranscriptionServiceError):
    """Exception for invalid or unexpected API responses."""
    pass

@dataclass
class TranscriptionResponse:
    """
    Represents the expected JSON response from the /transcribe endpoint.
    """
    transcription: str

class TranscriptionServiceClient:
    """
    Client for interacting with a transcription service.
    """
    def __init__(self, base_url: str = None):
        self._base_url = base_url or config.TRANSCRIPTION_API_BASE_URL
        logger.info(f"TranscriptionServiceClient initialized with base URL: {self._base_url}")

    async def transcribe(self, audio_file: bytes) -> TranscriptionResponse:
        """
        Calls the /transcribe endpoint to upload and transcribe audio.

        Args:
            audio_file: The audio file content as bytes.

        Returns:
            TranscriptionResponse: A dictionary containing the transcription.
                                     Example: {"transcription": "..."}

        Raises:
            HttpRequestError: If there's an issue with the HTTP request.
            InvalidApiResponseError: If the API response is invalid or unexpected.
            TranscriptionServiceError: For other service-specific errors.
        """
        endpoint = "transcribe"
        # Add max_duration as a query param
        max_duration = config.MAX_DURATION_AUDIO_IN_SECS
        url = f"{self._base_url}/{endpoint}?max_duration={max_duration}"
        data = {'file': audio_file}
        logger.info(f"Sending POST request to: {url}, with form data keys: {list(data.keys())}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    if not response.ok:
                        error_message = await response.text()
                        logger.error(f"HTTP error {response.status} at {url}: {error_message}")
                        raise HttpRequestError(f"HTTP error {response.status} at {url}: {error_message}")
                    try:
                        response_data = await response.json()
                        logger.debug(f"Received API response from {url}: {response_data}")
                        # Type check the response data
                        if "transcription" in response_data and isinstance(response_data["transcription"], str):
                            logger.info(response_data)
                            return TranscriptionResponse(transcription=response_data["transcription"])
                        else:
                            logger.error(f"Invalid API response format: {response_data}")
                            raise InvalidApiResponseError(f"Invalid API response format: {response_data}")
                    except aiohttp.ContentTypeError:
                        response_text = await response.text()
                        logger.error(f"Invalid JSON response received from {url}: {response_text}")
                        raise InvalidApiResponseError(f"Invalid JSON response received from {url}: {response_text}")
        except aiohttp.ClientError as e:
            logger.error(f"AIOHTTP client error during POST to {url}: {e}")
            raise HttpRequestError(f"AIOHTTP client error during POST to {url}: {e}")

    async def close(self) -> None:
        """No explicit closing needed as sessions are created per request."""
        logger.info("TranscriptionServiceClient.close() called - no explicit action needed.")
        pass
