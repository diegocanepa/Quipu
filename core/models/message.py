from dataclasses import dataclass, field
from enum import Enum
from typing import Any  # Assuming FinancialModel is a custom type, use Any if not defined here

class Source(str, Enum):
    """Defines possible message sources."""
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

@dataclass
class Message:
    """
    Represents a message answered by the bot.
    """
    user_id: str = field(metadata={"description": "User ID from Supabase. Not telegram, not whatsapp, not webapp"})
    message_id: str = field(metadata={"description": "Message ID"})
    message_text: str = field(metadata={"description": "Message text"})
    message_object: Any = field(metadata={"description": "Financial model associated with the message"})
    source: Source = field(metadata={"description": "Source of the message (Telegram, WhatsApp)"})