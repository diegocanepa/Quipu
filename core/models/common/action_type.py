from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class ActionTypes(str, Enum):
    """Defines possible actions."""
    EXCHANGE = "Cambio de divisas"
    INVESTMENT = "Inversion"
    TRANSACTION = "Transaccion"
    TRANSFER = "Transferencia"

class DetectedAction(BaseModel):
    """Represents a detected action with its associated message."""
    action_type: ActionTypes = Field(description="Type of action detected")
    message: str = Field(description="The specific message related to this action")

class Actions(BaseModel):
    """Represents the result of processing a user message with detected actions."""
    actions: List[DetectedAction] = Field(description="List of detected actions and their messages") 