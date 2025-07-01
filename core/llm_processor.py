import logging
from datetime import datetime
from typing import List, Optional, Type, Union

import pytz
from pydantic import BaseModel

from core.feature_flag import FeatureFlagsEnum, is_feature_enabled
from core.models.common.action_type import Actions, ActionTypes
from core.models.financial.forex import Forex
from core.models.financial.investment import Investment
from core.models.financial.transaction import Transaction
from core.models.financial.transfer import Transfer
from core.prompts import (
    MULTI_ACTION_PROMPT,
    TRANSACTION_PROMPT,
    SOCIAL_MESSAGE_RESPONSE_PROMPT,
    QUESTION_RESPONSE_PROMPT,
    UNKNOWN_MESSAGE_RESPONSE_PROMPT,
)
from integrations.providers.llm_akash import RotatingLLMClientPool as LLMAgent

logger = logging.getLogger(__name__)

class RequestLLMModel(BaseModel):
    prompt: str
    output_model: Type[BaseModel]

class ProcessingResult(BaseModel):
    """
    Represents the result of processing and saving a data object.
    """

    data_object: Optional[Transaction] = None
    response_text: Optional[str] = None
    error: Optional[str] = None


class LLMProcessor:
    """
    Processor to handle interaction with the LLM client and extract structured data
    from the LLM's response.
    """

    def __init__(self):
        """
        Initializes the LLMProcessor with instances of the LLM, spreadsheet, and
        database clients. Logs the initialization.
        """
        self.llm_client = LLMAgent()
        logger.info("LLMProcessor initialized.")

    async def process_content(self, content: str) -> List[ProcessingResult]:
        """
        Processes the input content by determining the action type using the LLM,
        generating responses for each required step, and saving the data.

        Args:
            content: The input string to be processed.

        Returns:
            A list of ProcessingResult objects, each containing the processed data
            and the status of saving to spreadsheet and database.
        """
        logger.info(f"Processing content: '{content}'")
        processing_results: List[ProcessingResult] = []
        current_datetime = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))

        try:
            action = self.determine_action_type(content)
            if not action:
                logger.warning(
                    f"Could not determine action type for content: '{content}'."
                )
                processing_results.append(
                    ProcessingResult(
                        error='No se pudo determinar una acción para registrar en base al mensaje. \
                            \n Pobrá especificando el movimiento con "Gasté" o "Recibí" seguido del monto y la descripción del movimiento.'
                    )
                )
                return processing_results

            llm_request = self._process_action(action.message, action.action_type)

            if not llm_request:
                logger.warning(f"Failed to create LLM request models for action: {action}")
                processing_results.append(
                    ProcessingResult(
                        error=ERROR_PROCESSING_MESSAGE
                    )
                )
                return processing_results
            
            if action.action_type == ActionTypes.TRANSACTION:
                responses = self.llm_client.generate_response(prompt=llm_request.prompt, output=llm_request.output_model)
                for transaction in responses.actions:
                    transaction.date = current_datetime # :TODO Only when date is not provided by user
                    processing_results.append(
                        ProcessingResult(data_object=transaction)
                    )
                    logger.info(f"Processed: {transaction.model_dump_json()}")
            else:
                response = self.llm_client.generate_simple_response(prompt=llm_request.prompt)
                processing_results.append(
                        ProcessingResult(response_text=response.response)
                    )

        except Exception as e:
            logger.error(
                f"An unexpected error occurred during content processing: '{e}'",
                exc_info=True,
            )
            processing_results.append(
                ProcessingResult(
                    error=ERROR_PROCESSING_MESSAGE
                )
            )

        return processing_results

    def determine_action_type(self, content: str) -> Optional[Action]:
        """
        Determines the action type from the input content using the LLM.
        """
        prompt = MULTI_ACTION_PROMPT.format(content=content)
        action = self.llm_client.determinate_action(prompt)
        logger.info(
            f"Determined actions types for content: '{content}', actions: '{action}'."
        )
        return action

    def _process_action(
        self, content: str, action_type: ActionTypes
    ) -> RequestLLMModel:
        """
        Determines the necessary LLM calls based on the action type and returns
        a list of RequestLLMModel objects.

        Args:
            content: The input string.
            action_type: The determined ActionTypes.

        Returns:
            A list of RequestLLMModel objects, or None if no requests are needed.
        """
        if action_type == ActionTypes.TRANSACTION and is_feature_enabled(
            FeatureFlagsEnum.TRANSACTION
        ):
            return self._prepare_transaction_requests(content)
        elif action_type == ActionTypes.QUESTION:
            return self._prepare_question_requests(content)
        elif action_type == ActionTypes.SOCIAL_MESSAGE:
            return self._prepare_social_message_requests(content)
        elif action_type == ActionTypes.UNKNOWN_MESSAGE:
            return self._prepare_unknow_message_requests(content)
        else:
            logger.warning(f"No LLM requests prepared for action: {action_type}")
            return None

    def _prepare_transaction_requests(self, content: str) -> RequestLLMModel:
        """Prepares LLM request models for a Transaction action."""
        return RequestLLMModel(
                prompt=self._get_prompt(TRANSACTION_PROMPT, content),
                output_model=FinantialActions,
            )

    def _prepare_social_message_requests(self, content: str) -> RequestLLMModel:
        """Prepara el request para mensajes sociales."""
        return RequestLLMModel(
                prompt=self._get_prompt(SOCIAL_MESSAGE_RESPONSE_PROMPT, content),
                output_model=SimpleStringResponse,
            )
        

    def _prepare_question_requests(self, content: str) -> RequestLLMModel:
        """Prepara el request para preguntas de usuario."""
        return RequestLLMModel(
                prompt=self._get_prompt(QUESTION_RESPONSE_PROMPT, content),
                output_model=SimpleStringResponse,
            )

    def _prepare_unknow_message_requests(self, content: str) -> RequestLLMModel:
        """Prepara el request para mensajes desconocidos."""
        return  RequestLLMModel(
                prompt=self._get_prompt(UNKNOWN_MESSAGE_RESPONSE_PROMPT, content),
                output_model=SimpleStringResponse,
            )
        

    def _get_prompt(
        self, promp: str, content: str, reason: Optional[str] = None
    ) -> str:
        """
        Determines the appropriate prompt based on the action type and an optional reason.

        Args:
            promp: promp string.
            content: The input content to be formatted into the prompt.
            reason: An optional reason to include in the prompt. Defaults to None.

        Returns:
            The formatted prompt.
        """
        return promp.format(content=content, reason=reason if reason else "")
