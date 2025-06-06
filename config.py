import os

from dotenv import load_dotenv

load_dotenv(".env")  # Load environment variables from .env


class Config:
    """Class to store application settings."""

    AKASH_API_BASE_URL: str = os.getenv("AKASH_API_BASE_URL")
    AKASH_API_KEY: str = os.getenv("AKASH_API_KEY")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "DeepSeek-R1-Distill-Qwen-32B")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    GOOGLE_CREDENTIALS: str = os.getenv("GOOGLE_CREDENTIALS")
    GOOGLE_SHEET_TEMPLATE_URL: str = os.getenv("GOOGLE_SHEET_TEMPLATE_URL")
    GOOGLE_SERVICE_ACCOUNT_EMAIL: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_EMAIL")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL")
    TRANSCRIPTION_API_BASE_URL: str = os.getenv("TRANSCRIPTION_API_BASE_URL")
    FF_AUDIO_TRANSCRIPTION: bool = (
        os.getenv("FF_AUDIO_TRANSCRIPTION", "true").lower() == "true"
    )
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    FF_TRANSFER: bool = os.getenv("FF_TRANSFER", "true").lower() == "true"
    FF_EXCHANGE: bool = os.getenv("FF_EXCHANGE", "true").lower() == "true"
    FF_TRANSACTION: bool = os.getenv("FF_TRANSACTION", "true").lower() == "true"
    FF_INVESTMENT: bool = os.getenv("FF_INVESTMENT", "true").lower() == "true"
    WEBAPP_BASE_URL: str = os.getenv("WEBAPP_BASE_URL")

    def __init__(self):
        self._validate_configs()

    def _validate_configs(self):
        """Optional: Add validations to ensure required configs are present and valid."""
        if not self.AKASH_API_BASE_URL:
            raise ValueError("AKASH_API_BASE_URL must be set in the .env file.")
        if not self.AKASH_API_KEY:
            raise ValueError("AKASH_API_KEY must be set in the .env file.")
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN must be set in the .env file.")
        if not self.GOOGLE_CREDENTIALS:
            raise ValueError("GOOGLE_CREDENTIALS must be set in the .env file.")
        if not self.GOOGLE_SHEET_TEMPLATE_URL:
            raise ValueError("GOOGLE_SHEET_TEMPLATE_URL must be set in the .env file.")
        if not self.GOOGLE_SERVICE_ACCOUNT_EMAIL:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_EMAIL must be set in the .env file.")
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL must be set in the .env file.")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY must be set in the .env file.")
        if not self.TRANSCRIPTION_API_BASE_URL:
            raise ValueError("TRANSCRIPTION_API_BASE_URL must be set in the .env file.")
        if not self.WEBAPP_BASE_URL:
            raise ValueError("WEBAPP_BASE_URL must be set in the .env file.")
        if not self.WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL must be set in the .env file.")
        try:
            float(self.LLM_TEMPERATURE)
        except ValueError:
            raise ValueError("LLM_TEMPERATURE must be a valid float in the .env file.")


# Create a global instance of the settings for easy access
config = Config()