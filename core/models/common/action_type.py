from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class ActionTypes(str, Enum):
    """Defines possible actions."""
    SOCIAL_MESSAGE= "SocialMessage"
    QUESTION = "Question"
    TRANSACTION = "Transaction"
    UNKNOWN_MESSAGE = "UnknownMessage"

class Action(BaseModel):
    """Represents a detected action with its associated message."""
    action_type: ActionTypes = Field(description="Type of action detected")
    message: str = Field(description="The specific message related to this action")
