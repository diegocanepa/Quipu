from core.prompts import PROMPT
from integrations.providers.llm_akash import AkashLLMClient
import logging
from models.bills import Bills
from datetime import datetime
from zoneinfo import ZoneInfo

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

    def process_content(self, content: str) -> Bills:
        """
        Processes the input content by sending it to the LLM and extracting
        the action, amount, and wallet from the response.
        Logs the processing steps and any errors.
        """
        logger.info(f"Processing content: '{content}'")
        prompt = PROMPT.format(content=content)
        llm_response = self.llm_client.generate_response(prompt)
        llm_response.date = datetime.now()  
        return llm_response