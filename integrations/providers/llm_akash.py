import logging
from itertools import cycle
from threading import Lock
from typing import List

from langchain_openai import ChatOpenAI

from config import config
from core.models.common.action_type import Action
from core.models.common.financial_type import FinantialActions
from core.models.common.simple_message import SimpleStringResponse
from integrations.llm_providers_interface import LLMClientInterface

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
        self.clients = []
        for key in config.AKASH_API_KEY:
            self.clients.append(
                ChatOpenAI(
                    base_url=config.AKASH_API_BASE_URL,
                    api_key=key.strip(),
                    model_name=config.LLM_MODEL_NAME,
                    temperature=config.LLM_TEMPERATURE,
                    timeout=config.LLM_TIMEOUT,
                    max_retries=config.LLM_MAX_RETRIES,
                )
            )

        self._clients_cycle = cycle(self.clients)
        self._lock = Lock()
        logger.info(
            f"Initialized {len(self.clients)} LLM clients with rotating API keys."
        )

    def _get_next_client(self) -> ChatOpenAI:
        """
        Returns the next available client in a thread-safe manner.
        """
        with self._lock:
            return next(self._clients_cycle)

    def determinate_action(self, prompt: str) -> Action:
        """
        Uses the next available client to execute a prompt
        that returns a structured `Actions` enum.
        """
        client = self._get_next_client().with_structured_output(Action)
        return client.invoke(prompt)

    def generate_simple_response(self, prompt: str) -> SimpleStringResponse:
        """
        Uses the next available client to execute the given prompt and returns a structured SimpleStringResponse object.
        """
        client = self._get_next_client().with_structured_output(SimpleStringResponse)
        return client.invoke(prompt)

    def generate_response(self, prompt: str, output) -> FinantialActions:
        """
        Sends a prompt to the Akash LLM and returns the generated response.
        Logs the request and any errors during the API call.
        """
        client = self._get_next_client().with_structured_output(output)
        return client.invoke(prompt)
