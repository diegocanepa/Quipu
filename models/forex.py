from pydantic import BaseModel, Field
from datetime import datetime

class Forex(BaseModel):
    """Represents a financial bill."""
    description: str = Field(description="Description of the bill")
    amount: float = Field(description="Amount of the bill")
    currency_from: str = Field(description="Currency of the bill")
    currency_to: str = Field(description="Currency of the bill")
    price: float = Field(description="Price of change")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action")