from enum import Enum
from pydantic import BaseModel, Field

class ActionTypes(str, Enum):
    """Defines possible actions in a forex transaction."""
    EXCHANGE = "Cambio de divisas"
    INVESTMENT = "Inversion"
    TRANSACTION = "Transaccion"
    TRANSFER = "Transferencia"

class Action(BaseModel):
    """Represents a financial bill."""
    action: ActionTypes = Field(description="Action")