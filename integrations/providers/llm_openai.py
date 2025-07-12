from logging_config import get_logger
from typing import Type, Union
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from config import config
from core.models.common.action_type import Action
from core.models.common.financial_type import FinantialActions
from core.models.common.simple_message import SimpleStringResponse
from integrations.llm_providers_interface import LLMClientInterface

logger = get_logger(__name__)

class OpenAILLM(LLMClientInterface):
    """
    OpenAI LLM client implementation.

    This class is a placeholder for the actual OpenAI client implementation.
    It should be replaced with the actual OpenAI client code that interacts with
    the OpenAI API to generate responses based on prompts.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=SecretStr(config.OPENAI_API_KEY),
            temperature=0,
            model=config.OPENAI_CHAT_COMPLETIONS_MODEL,
        )

    def generate_response(self, prompt: str, output: Type[Union[Action, FinantialActions, SimpleStringResponse]]) -> Union[Action, FinantialActions, SimpleStringResponse]:
        """
        Sends a prompt to the Akash LLM and returns the generated response.
        Logs the request and any errors during the API call.
        """
        client = self.llm.with_structured_output(output)
        response = client.invoke(prompt)
        logger.info(f"Response from Open API: {response}")
        if isinstance(response, dict):
            return output(**response)
        return response
