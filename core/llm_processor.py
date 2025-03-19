from integrations.llm_akash import AkashLLMClient
import re
import json
import logging
from typing import Optional


logger = logging.getLogger(__name__)


class LLMProcessor:
    """
    Processor to handle interaction with the LLM client and extract structured data
    from the LLM's response.
    """

    def __init__(self):
        """
        Initializes the LLMProcessor with an instance of the AkashLLMClient.
        Logs the initialization.
        """
        self.llm_client = AkashLLMClient()

    def process_content(self, content: str) -> Optional[dict]:
        """
        Processes the input content by sending it to the LLM and extracting
        the action, amount, and wallet from the response.
        Logs the processing steps and any errors.
        """
        logger.info(f"Processing content: '{content}'")
        prompt = f"Analiza el siguiente texto y extrae la acción, la cantidad (si la hay) y la billetera (si la hay). Devuelve un diccionario JSON con las claves 'action', 'ammount' y 'wallet'. Texto: {content}"
        llm_response = self.llm_client.generate_response(prompt)
        return self._extract_data(llm_response)

    def _extract_data(self, llm_response: str) -> Optional[dict]:
        """
        Attempts to extract the action, amount, and wallet from the LLM response.
        Tries to parse as JSON first, then falls back to regex.
        Logs the extraction attempts and results.
        """
        try:
            return json.loads(llm_response)
        except json.JSONDecodeError:
            logger.info(f"LLM response is not valid JSON. Falling back to regex extraction. llm_response: '{llm_response}'")

            action_match = re.search(r"acción:\s*([a-zA-Z]+)", llm_response, re.IGNORECASE)
            ammount_match = re.search(r"cantidad:\s*([0-9.]+)", llm_response, re.IGNORECASE)
            wallet_match = re.search(r"billetera:\s*([a-zA-Z0-9]+)", llm_response, re.IGNORECASE)

            if action_match and ammount_match and wallet_match:
                return {
                    "action": action_match.group(1),
                    "ammount": float(ammount_match.group(1)),
                    "wallet": wallet_match.group(1),
                }
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during data extraction: {e}")
            return None