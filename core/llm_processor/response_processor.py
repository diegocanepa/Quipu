from core.llm_processor.schemas import ProcessingResult, LLMModelRequest, ResponseProcessorException
from core.models.common.action_type import ActionTypes
from integrations.providers.llm_akash import RotatingLLMClientPool as LLMAgent
from typing import List, cast
from core.models.common.financial_type import FinantialActions
from core.models.common.simple_message import SimpleStringResponse
from logging_config import get_logger

class ResponseProcessor:
    """
    Handles the processing of LLM responses and maps them to ProcessingResult objects.
    """
    def __init__(self):
        self.llm_client = LLMAgent()
        self.logger = get_logger(__name__)

    async def process_response(self, prompt: LLMModelRequest) -> List[ProcessingResult]:
        """
        Processes the LLM response and returns a list of ProcessingResult objects.
        Raises ResponseProcessorException if the response type is not recognized or an error occurs.
        """
        try:
            self.logger.info(f"[ResponseProcessor] Processing response for prompt: {prompt.human_prompt}")
            response = self.llm_client.generate_response(
                system_template=prompt.system_prompt,
                human_template=prompt.human_prompt,
                output=prompt.output_model
            )
            self.logger.info(f"[ResponseProcessor] LLM response received: {response}")
            if self._is_finantial_actions(response):
                return self._build_finantial_actions_results(cast(FinantialActions, response))
            elif self._is_simple_string_response(response):
                return self._build_simple_string_response_results(cast(SimpleStringResponse, response))
            else:
                raise ResponseProcessorException(
                    f"[ResponseProcessor] Unexpected response type: {type(response)}. Response: {response}"
                )
        except Exception as e:
            raise ResponseProcessorException(f"[ResponseProcessor] Error processing response: {e}") from e

    def _is_finantial_actions(self, response) -> bool:
        """
        Checks if the response is a FinantialActions instance with actions.
        """
        return isinstance(response, FinantialActions) and hasattr(response, 'actions')

    def _is_simple_string_response(self, response) -> bool:
        """
        Checks if the response is a SimpleStringResponse instance with a response attribute.
        """
        return isinstance(response, SimpleStringResponse) and hasattr(response, 'response')

    def _build_finantial_actions_results(self, response: FinantialActions) -> List[ProcessingResult]:
        """
        Builds a list of ProcessingResult objects from a FinantialActions response.
        """
        results = [ProcessingResult(data_object=transaction) for transaction in getattr(response, 'actions', [])]
        self.logger.info(f"[ResponseProcessor] Built {len(results)} ProcessingResult(s) from FinantialActions.")
        return results

    def _build_simple_string_response_results(self, response: SimpleStringResponse) -> List[ProcessingResult]:
        """
        Builds a list of ProcessingResult objects from a SimpleStringResponse response.
        """
        results = [ProcessingResult(response_text=getattr(response, 'response', None))]
        self.logger.info(f"[ResponseProcessor] Built ProcessingResult from SimpleStringResponse: {results}")
        return results 