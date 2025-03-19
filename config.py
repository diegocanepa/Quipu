import os
from dotenv import load_dotenv

load_dotenv(".env")  # Load environment variables from .env

class Config:
    """Class to store application settings."""

    AKASH_API_BASE_URL: str = os.getenv("AKASH_API_BASE_URL")
    AKASH_API_KEY: str = os.getenv("AKASH_API_KEY")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "default-model")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    def __init__(self):
        self._validate_configs()

    def _validate_configs(self):
        """Optional: Add validations to ensure required configs are present and valid."""
        if not self.AKASH_API_BASE_URL:
            raise ValueError("AKASH_API_BASE_URL must be set in the .env file.")
        if not self.AKASH_API_KEY:
            raise ValueError("AKASH_API_KEY must be set in the .env file.")
        try:
            float(self.LLM_TEMPERATURE)
        except ValueError:
            raise ValueError("LLM_TEMPERATURE must be a valid float in the .env file.")

# Create a global instance of the settings for easy access
config = Config()