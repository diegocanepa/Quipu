from pydantic import BaseModel, Field
from datetime import datetime

class Bills(BaseModel):
    """Represents a financial transaction."""
    description: str = Field(description="Description of the bill")
    amount: float = Field(description="Amount of the bill")
    category: str = Field(description="Category of the bill")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action")