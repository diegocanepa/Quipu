from core.models.common.action_type import Action
from core.prompts import ACTION_PROMPT
from integrations.providers.llm_akash import RotatingLLMClientPool as LLMAgent
from logging_config import get_logger
from core.llm_processor.schemas import ActionDetectorException

class ActionDetector:
    """
    Detects the action type from a given message using the LLM client.
    Raises ActionDetectorException on error or unexpected response type.
    """
    def __init__(self):
        self.llm_client = LLMAgent()
        self.logger = get_logger(__name__)

    def detect_action(self, content: str) -> Action:
        """
        Detects and returns the Action for the given message content.
        """
        try:
            self.logger.info(f"[ActionDetector] Detecting action for message: {content}")
            action = self.llm_client.generate_response(
                system_template=ACTION_PROMPT,
                human_template=content,
                output=Action
            )
            return self._validate_action_result(action)
        except Exception as e:
            raise ActionDetectorException(f"[ActionDetector] Error detecting action: {e}") from e
    
    def _validate_action_result(self, action) -> Action:
        """
        Validates and converts the LLM response to an Action instance.
        Raises ActionDetectorException if the response is not a valid Action or cannot be converted.
        """
        if isinstance(action, dict):
            action = Action(**action)
        if isinstance(action, Action):
            self.logger.info(f"[ActionDetector] Action detected: {action}")
            return action
        else:
            raise ActionDetectorException(f"[ActionDetector] Unexpected action type: {type(action)}. Action: {action}")