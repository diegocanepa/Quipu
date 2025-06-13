from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from core.models.base_model import FinancialModel 
from core.models.common.source import Source

@dataclass
class Message:
    """
    Represents a message answered by the bot.
    """
    user_id: str = field(metadata={"description": "User ID from Supabase. Not telegram, not whatsapp, not webapp"})
    message_id: str = field(metadata={"description": "Message ID"})
    message_text: str = field(metadata={"description": "Message text"})
    source: Source = field(metadata={"description": "Source of the message (Telegram, WhatsApp)"})
    message_object: Optional[FinancialModel] = field(default=None, metadata={"description": "Financial model associated with the message. It's optional because receive message don't have this attribute yet."})