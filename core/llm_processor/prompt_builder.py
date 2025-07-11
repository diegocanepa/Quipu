from core.prompts import (
    TRANSACTION_PROMPT,
    HUMAN_PROMPT,
    SOCIAL_MESSAGE_RESPONSE_PROMPT,
    QUESTION_RESPONSE_PROMPT,
    UNKNOWN_MESSAGE_RESPONSE_PROMPT,
)
from core.models.common.action_type import ActionTypes
from core.models.common.financial_type import FinantialActions
from core.models.common.simple_message import SimpleStringResponse
from datetime import datetime
import pytz
from core.llm_processor.schemas import PromptBuilderException, RequestLLMModel

class PromptBuilder:
    """
    Builds the appropriate prompt for the LLM based on the detected action type.
    Raises PromptBuilderException for unknown action types.
    """
    def build_prompt(self, content: str, action) -> RequestLLMModel:
        """
        Returns a RequestLLMModel with the correct system and human prompt, and output model,
        depending on the action type.
        """
        if action.action_type == ActionTypes.TRANSACTION:
            return self._build_transaction_request(content)
        elif action.action_type == ActionTypes.QUESTION:
            return self._build_question_request(content)
        elif action.action_type == ActionTypes.SOCIAL_MESSAGE:
            return self._build_social_message_request(content)
        elif action.action_type == ActionTypes.UNKNOWN_MESSAGE:
            return self._build_unknown_message_request(content)
        else:
            raise PromptBuilderException(f"Unknown action type: {action.action_type}")

    def _build_transaction_request(self, content: str) -> RequestLLMModel:
        """
        Builds a prompt for a transaction action, including current date and day of week.
        """
        current_datetime = datetime.now(pytz.timezone("America/Argentina/Buenos_Aires"))
        day_of_week = current_datetime.strftime("%A")
        return RequestLLMModel(
            system_prompt=TRANSACTION_PROMPT,
            human_prompt=HUMAN_PROMPT.format(content=content, current_date=current_datetime, current_day_of_week=day_of_week),
            output_model=FinantialActions
        )

    def _build_question_request(self, content: str) -> RequestLLMModel:
        """
        Builds a prompt for a question action.
        """
        return RequestLLMModel(
            system_prompt=QUESTION_RESPONSE_PROMPT,
            human_prompt=content,
            output_model=SimpleStringResponse
        )

    def _build_social_message_request(self, content: str) -> RequestLLMModel:
        """
        Builds a prompt for a social message action.
        """
        return RequestLLMModel(
            system_prompt=SOCIAL_MESSAGE_RESPONSE_PROMPT,
            human_prompt=content,
            output_model=SimpleStringResponse
        )

    def _build_unknown_message_request(self, content: str) -> RequestLLMModel:
        """
        Builds a prompt for an unknown message action.
        """
        return RequestLLMModel(
            system_prompt=UNKNOWN_MESSAGE_RESPONSE_PROMPT,
            human_prompt=content,
            output_model=SimpleStringResponse
        ) 