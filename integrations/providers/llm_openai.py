import logging
from langchain_openai import ChatOpenAI

from config import config
from integrations.llm_providers_interface import LLMClientInterface

logger = logging.getLogger(__name__)

class OpenAILLM(LLMClientInterface):
    """
    OpenAI LLM client implementation.

    This class is a placeholder for the actual OpenAI client implementation.
    It should be replaced with the actual OpenAI client code that interacts with
    the OpenAI API to generate responses based on prompts.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            temperature=0,
            model_name=config.OPENAI_CHAT_COMPLETIONS_MODEL,
        )

    def generate_response(self, prompt: str, output):
        """
        Sends a prompt to the Akash LLM and returns the generated response.
        Logs the request and any errors during the API call.
        """
        client = self.llm.with_structured_output(output)
        response = client.invoke(prompt)
        logger.info(f"Response from Open API: {response}")
        return response
