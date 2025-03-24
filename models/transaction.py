from pydantic import BaseModel, Field
from datetime import datetime

class Transaction(BaseModel):
    """Represents a financial bill."""
    description: str = Field(description="Description of the bill")
    amount: float = Field(description="Amount of the bill")
    currency: str = Field(description="Currency of the bill")
    category: str = Field(description="Category of the bill")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action (expense or income)")