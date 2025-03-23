from langchain_openai import ChatOpenAI
from integrations.llm_providers_interface import LLMClientInterface
from config import config
import logging
from models.bills import Bills

logger = logging.getLogger(__name__)

class AkashLLMClient(LLMClientInterface):
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
            base_url=config.AKASH_API_BASE_URL,
            api_key=config.AKASH_API_KEY,
            model_name="DeepSeek-R1-Distill-Qwen-14B",
            temperature=config.LLM_TEMPERATURE
        )
        self.structured_llm = self.llm.with_structured_output(Bills)
        logger.info("Akash OpenAI client initialized successfully.")


    def generate_response(self, prompt: str) -> Bills:
        """
        Sends a prompt to the Akash LLM and returns the generated response.
        Logs the request and any errors during the API call.
        """
        return self.structured_llm.invoke(prompt)
