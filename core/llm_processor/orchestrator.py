from core.llm_processor.action_detector import ActionDetector
from core.llm_processor.prompt_builder import PromptBuilder
from core.llm_processor.response_processor import ResponseProcessor
from core.llm_processor.validator import LLMResponseValidator
from typing import List
from core.llm_processor.schemas import ProcessingResult, LLMProcessorException
from core.messages import ERROR_PROCESSING_MESSAGE
import logging

class LLMOrchestrator:
    """
    Orchestrates the LLM processing pipeline: detects action, builds prompt, processes response, and validates results.
    Exceptions from each module are propagated.
    """
    def __init__(self):
        self.action_detector = ActionDetector()
        self.prompt_builder = PromptBuilder()
        self.response_processor = ResponseProcessor()
        self.validator = LLMResponseValidator()
        self.logger = logging.getLogger(__name__)
        self.logger.info("LLMProcessorV2 initialized.")

    async def process_content(self, content: str) -> List[ProcessingResult]:
        """
        Runs the full LLM processing pipeline for the given content.
        Returns a list with a ProcessingResult containing the error if an LLMProcessorException is raised.
        """
        try:
            self.logger.info(f"[LLMOrchestrator] Starting processing for content: {content}")
            action = self.action_detector.detect_action(content)
            prompt = self.prompt_builder.build_prompt(content, action)
            results = await self.response_processor.process_response(prompt)
            self.validator.validate(results)
            self.logger.info(f"[LLMOrchestrator] Results validated successfully.")
            return results
        except LLMProcessorException as e:
            self.logger.error(f"[LLMOrchestrator] LLMProcessorException occurred: {e}. Returning error to user.")
            return [ProcessingResult(error=ERROR_PROCESSING_MESSAGE)] 