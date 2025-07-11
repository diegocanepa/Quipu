from logging_config import get_logger
from datetime import datetime
from typing import List, Optional, Type, Union

import pytz
from pydantic import BaseModel

from core.feature_flag import FeatureFlagsEnum, is_feature_enabled
from core.messages import ERROR_PROCESSING_MESSAGE
from core.models.common.financial_type import FinantialActions
from core.models.common.simple_message import SimpleStringResponse
from core.prompts import (
    ACTION_PROMPT,
    TRANSACTION_PROMPT,
    HUMAN_PROMPT,
    SOCIAL_MESSAGE_RESPONSE_PROMPT,
    QUESTION_RESPONSE_PROMPT,
    UNKNOWN_MESSAGE_RESPONSE_PROMPT,
)
from integrations.providers.llm_akash import RotatingLLMClientPool as LLMAgent
from core.models.common.action_type import Action, ActionTypes
from core.models.financial.transaction import Transaction

logger = get_logger(__name__)

class LLMModelRequest(BaseModel):
    system_prompt: str
    human_prompt: str
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
        current_datetime = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires")) # :TODO: Consider different timezones for events features
        day_of_week = current_datetime.strftime("%A")

        try:
            action = self.determine_action_type(content)
            if not action:
                logger.warning(
                    f"Could not determine action type for content: '{content}'."
                )
                processing_results.append(
                    ProcessingResult(
                        error=ERROR_PROCESSING_MESSAGE
                    )
                )
                return processing_results

            llm_request = self._process_action(action.message, action.action_type, current_datetime, day_of_week)

            if not llm_request:
                logger.warning(f"Failed to create LLM request models for action: {action}")
                processing_results.append(
                    ProcessingResult(
                        error=ERROR_PROCESSING_MESSAGE
                    )
                )
                return processing_results
            
            if action.action_type == ActionTypes.TRANSACTION:
                responses = self.llm_client.generate_response(system_template=llm_request.system_prompt, human_template=llm_request.human_prompt, output=llm_request.output_model)
                for transaction in responses.actions:
                    processing_results.append(
                        ProcessingResult(data_object=transaction)
                    )
                    logger.info(f"Processed: {transaction.model_dump_json()}")
            else:
                response = self.llm_client.generate_simple_response(system_template=llm_request.system_prompt, human_template=llm_request.human_prompt)
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
        action_request = self._prepare_determinate_action_requests(content)
        action = self.llm_client.determinate_action(system_template=action_request.system_prompt, human_template=action_request.human_prompt)
        logger.info(
            f"Determined actions types for content: '{content}', actions: '{action}'."
        )
        return action

    def _process_action(
        self, content: str, action_type: ActionTypes, current_datetime: datetime, day_of_week: str
    ) -> Optional[LLMModelRequest]:
        """
        Determines the necessary LLM calls based on the action type and returns
        a list of LLMModelRequest objects.

        Args:
            content: The input string.
            action_type: The determined ActionTypes.

        Returns:
            A list of LLMModelRequest objects, or None if no requests are needed.
        """
        if action_type == ActionTypes.TRANSACTION and is_feature_enabled(
            FeatureFlagsEnum.TRANSACTION
        ):
            return self._prepare_transaction_requests(content, current_datetime, day_of_week)
        elif action_type == ActionTypes.QUESTION:
            return self._prepare_question_requests(content)
        elif action_type == ActionTypes.SOCIAL_MESSAGE:
            return self._prepare_social_message_requests(content)
        elif action_type == ActionTypes.UNKNOWN_MESSAGE:
            return self._prepare_unknow_message_requests(content)
        else:
            logger.warning(f"No LLM requests prepared for action: {action_type}")
            return None

    def _prepare_determinate_action_requests(self, content: str) -> LLMModelRequest:
        """Prepares LLM request models for a Transaction action."""
        return LLMModelRequest(
                system_prompt=ACTION_PROMPT,
                human_prompt=content,
                output_model=Action,
            )
    
    def _prepare_transaction_requests(self, content: str, current_datetime: datetime, day_of_week: str) -> LLMModelRequest:
        """Prepares LLM request models for a Transaction action."""
        return LLMModelRequest(
                system_prompt=TRANSACTION_PROMPT,
                human_prompt=HUMAN_PROMPT.format(content=content, current_date=current_datetime, current_day_of_week=day_of_week),
                output_model=FinantialActions,
            )

    def _prepare_social_message_requests(self, content: str) -> LLMModelRequest:
        """Prepara el request para mensajes sociales."""
        return LLMModelRequest(
                system_prompt=SOCIAL_MESSAGE_RESPONSE_PROMPT,
                human_prompt=content,
                output_model=SimpleStringResponse,
            )

    def _prepare_question_requests(self, content: str) -> LLMModelRequest:
        """Prepara el request para preguntas de usuario."""
        return LLMModelRequest(
                system_prompt=QUESTION_RESPONSE_PROMPT,
                human_prompt=content,
                output_model=SimpleStringResponse,
            )

    def _prepare_unknow_message_requests(self, content: str) -> LLMModelRequest:
        """Prepara el request para mensajes desconocidos."""
        return  LLMModelRequest(
                system_prompt=UNKNOWN_MESSAGE_RESPONSE_PROMPT,
                human_prompt=content,
                output_model=SimpleStringResponse,
            )