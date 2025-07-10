import logging
from itertools import cycle
from threading import Lock
from typing import List

from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from pydantic import SecretStr

from config import config
from core.models.common.action_type import Action
from core.models.common.financial_type import FinantialActions
from core.models.common.simple_message import SimpleStringResponse
from integrations.llm_providers_interface import LLMClientInterface
from integrations.providers.llm_openai import OpenAILLM

logger = logging.getLogger(__name__)

class RotatingLLMClientPool(LLMClientInterface):
    """
    LLM client pool with rotating API keys to bypass per-key rate limits.

    - Rotates between multiple ChatOpenAI instances on each invocation.
    - Uses `itertools.cycle` to maintain a consistent round-robin strategy.
    - Thread-safe: access to the client cycle is protected by a Lock.

    Expected configuration:
        The environment variable `AKASH_API_KEYS` must contain the API keys separated by commas.

    :TODO Error fallback:
        If an API key fails (e.g., `RateLimitError` or `AuthenticationError`), catch the exception
        and retry using another key from the pool, up to a maximum number of attempts.

    :TODO Per-key usage control:
        Track counters or timestamps per API key to avoid hitting limits proactively instead of waiting for errors.
    """

    def __init__(self):
        self.fallback_llm = OpenAILLM()
        self.clients = []
        for key in config.AKASH_API_KEY:
            self.clients.append(
                ChatOpenAI(
                    base_url=config.AKASH_API_BASE_URL,
                    api_key=SecretStr(key.strip()),
                    model=config.LLM_MODEL_NAME,
                    temperature=config.LLM_TEMPERATURE,
                    timeout=config.LLM_TIMEOUT,
                    max_retries=config.LLM_AKASH_RETRIES
                )
            )
            logger.info(
                f"Initialized timeout:{config.LLM_TIMEOUT} retries: {config.LLM_AKASH_RETRIES}"
            )

        self._clients_cycle = cycle(self.clients)
        self._lock = Lock()
        logger.info(
            f"Initialized {len(self.clients)} LLM clients with rotating API keys"
        )

    def _get_next_client(self) -> ChatOpenAI:
        """
        Returns the next available client in a thread-safe manner.
        """
        with self._lock:
            return next(self._clients_cycle)

    def determinate_action(self, system_template: str,  human_template: str,):
        """
        Uses the next available client to execute a prompt
        that returns a structured `Actions` enum.
        """
        chat_prompt = self._get_chat_prompt(system_template, human_template)
        return self._generate_fallbacked_response(chat_prompt, Action)

    def generate_simple_response(self, system_template: str,  human_template: str):
        """
        Uses the next available client to execute the given prompt and returns a structured SimpleStringResponse object.
        """
        chat_prompt = self._get_chat_prompt(system_template, human_template)
        return self._generate_fallbacked_response(chat_prompt, SimpleStringResponse)

    def generate_response(self, system_template: str,  human_template: str, output):
        """
        Sends a prompt to the Akash LLM and returns the generated response.
        Logs the request and any errors during the API call.
        """
        chat_prompt = self._get_chat_prompt(system_template, human_template)
        return self._generate_fallbacked_response(chat_prompt, output)
    
    def _get_chat_prompt(self, system_template: str,  human_template: str):
        system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
        return chat_prompt.format()

    def _generate_fallbacked_response(self, prompt, output):
        """
        Attempts to generate a response using the rotating LLM client pool.
        If it fails, falls back to the OpenAI LLM client.
        """
        try:
            client = self._get_next_client().with_structured_output(output)
            response =  client.invoke(prompt)
            logger.info(f"Answer from akash: {response}")
            return response
        except Exception as e:
            logger.error(
                f"Failed to generate response with rotating clients. Falling back to OpenAI LLM."
            )
            return self.fallback_llm.generate_response(prompt, output)
