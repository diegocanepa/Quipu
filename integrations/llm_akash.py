from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config import AKASH_API_BASE_URL, AKASH_API_KEY, LLM_MODEL_NAME, LLM_TEMPERATURE
import logging

logger = logging.getLogger(__name__)


class AkashLLMClient:
    """
    Client to interact with the Akash LLM API.
    Encapsulates the connection details and request logic.
    """
    def __init__(self):
        """
        Initializes the AkashLLMClient with the configuration from the config module.
        Logs the initialization process.
        """
        self.llm = ChatOpenAI(
            base_url=AKASH_API_BASE_URL,
            api_key=AKASH_API_KEY,
            model_name=LLM_MODEL_NAME,
            temperature=LLM_TEMPERATURE
        )
        logger.info("Akash OpenAI client initialized successfully.")


    def generate_response(self, prompt: str) -> str:
        """
        Sends a prompt to the Akash LLM and returns the generated response.
        Logs the request and any errors during the API call.
        """
        messages = [
            HumanMessage(content=prompt)
        ]
        return self.llm.invoke(prompt)