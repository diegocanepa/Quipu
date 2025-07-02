import logging
from itertools import cycle
from threading import Lock

from langchain_openai import ChatOpenAI

from config import config
from core.models.common.action_type import Actions
from core.models.financial.forex import Forex
from core.models.financial.investment import Investment
from core.models.financial.transaction import Transaction
from core.models.financial.transfer import Transfer
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
            a = next(self._clients_cycle)
            return a

    def determinate_action(self, prompt: str) -> Actions:
        """
        Usa el siguiente cliente disponible para ejecutar un prompt
        que devuelve un enum `Actions` estructurado.
        """
        client = self._get_next_client().with_structured_output(Actions)
        return client.invoke(prompt)

    def generate_response(
        self, prompt: str, output
    ) -> Forex | Investment | Transaction | Transfer:
        """
        Sends a prompt to the Akash LLM and returns the generated response.
        Logs the request and any errors during the API call.
        """
        client = self._get_next_client().with_structured_output(output)
        return client.invoke(prompt)
