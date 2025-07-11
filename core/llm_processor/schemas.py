from typing import Optional, Type, Union
from pydantic import BaseModel
from core.models.common.action_type import Action
from core.models.common.financial_type import FinantialActions
from core.models.common.simple_message import SimpleStringResponse
from core.models.financial.transaction import Transaction

class LLMModelRequest(BaseModel):
    system_prompt: str
    human_prompt: str
    output_model:  Type[Union[Action, FinantialActions, SimpleStringResponse]]

class ProcessingResult(BaseModel):
    data_object: Optional[Transaction] = None
    response_text: Optional[str] = None
    error: Optional[str] = None

# Custom exceptions for LLM Processor
class LLMProcessorException(Exception):
    """Generic exception for LLM Processor errors."""
    pass

class ResponseProcessorException(LLMProcessorException):
    """Exception for errors in the ResponseProcessor."""
    pass

class ActionDetectorException(LLMProcessorException):
    """Exception for errors in the ActionDetector."""
    pass 

class PromptBuilderException(LLMProcessorException):
    """Exception for errors in the ActionDetector."""
    pass 