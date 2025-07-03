from typing import List
from pydantic import BaseModel, Field

from core.models.financial.transaction import Transaction


class FinantialActions(BaseModel):
    """Represents the result of processing a user message with detected actions."""
    actions: List[Transaction] = Field(description="List of financtial Actions") 