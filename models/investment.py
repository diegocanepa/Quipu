from pydantic import BaseModel, Field
from datetime import datetime

class Investment(BaseModel):
    """Represents a financial transaction."""
    description: str = Field(description="Description of the investment")
    category: str = Field(description="Category of the investment")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action (sell or buy)")
    platform: str = Field(description="Platform where the investment was done")
    amout: float = Field(description="amount of the investment")
    price: float = Field(description="Price of the investment tool")
    currency: str = Field(description="Currency of the bill")