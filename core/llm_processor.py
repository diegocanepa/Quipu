from core.prompts import ACTION_TYPE_PROMPT, TRANSACTION_PROMPT, TRANSFER_PROMPT, FOREX_PROMP, INVESTMENT_PROMPT
from integrations.providers.llm_akash import AkashLLMClient
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from models.action_type import Action, ActionTypes
from models.forex import Forex
from models.investment import Investment
from models.transaction import Transaction
from models.transfer import Transfer
import pytz

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

    def process_content(self, content: str) -> Forex | Investment | Transaction | Transfer:
        """
        Processes the input content by sending it to the LLM and extracting
        the action, amount, and wallet from the response.
        Logs the processing steps and any errors.
        """
        logger.info(f"Processing content: '{content}'")
        action = self.determinate_action(content)
        
        llm_response = None
        if action == ActionTypes.TRANSFER:
            prompt = TRANSFER_PROMPT.format(content=content)
            llm_response = self.llm_client.generate_response(prompt=prompt, output=Transfer)
        if action == ActionTypes.TRANSACTION:
            prompt = TRANSACTION_PROMPT.format(content=content)
            llm_response = self.llm_client.generate_response(prompt=prompt, output=Transaction)
        if action == ActionTypes.INVESTMENT:
            prompt = INVESTMENT_PROMPT.format(content=content)
            llm_response = self.llm_client.generate_response(prompt=prompt, output=Investment)
        if action == ActionTypes.EXCHANGE:
            prompt = FOREX_PROMP.format(content=content)
            llm_response = self.llm_client.generate_response(prompt=prompt, output=Forex)
        
        llm_response.date = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
        return llm_response

    def determinate_action(self, content: str) -> Action:
        action_type_promp = ACTION_TYPE_PROMPT.format(content=content)
        llm_response = self.llm_client.determinate_action(action_type_promp)
        return llm_response.action
    