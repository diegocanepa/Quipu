from pydantic import BaseModel, Field
from datetime import datetime

class Transfer(BaseModel):
    """Represents a financial transaction."""
    description: str = Field(description="Description of the bill")
    category: str = Field(description="Category of the bill")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action")
    wallet_from: str = Field(description="Wallet from")
    wallet_to: str = Field(description="Wallet to")
    initial_amount: float = Field(description="Initial mount of the bill")
    final_amount: float = Field(description="Final mount of the bill with the fees")
    currency: str = Field(description="Currency of the bill")