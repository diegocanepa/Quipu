from enum import Enum

class Source(str, Enum):
    """Defines possible message sources."""
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp" 