import os
from dotenv import load_dotenv

load_dotenv()

AKASH_API_BASE_URL = os.getenv("AKASH_API_BASE_URL", "https://chatapi.akash.network/api/v1")
AKASH_API_KEY = os.getenv("AKASH_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "DeepSeek-R1")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))