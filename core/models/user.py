from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID
from core.utils.datetime_utils import parse_datetime

@dataclass
class User:
    """
    Represents a user in the system with all their attributes.
    Uses dataclass for automatic implementation of __init__, __repr__, etc.
    """
    id: UUID
    telegram_user_id: int
    telegram_first_name: str
    created_at: datetime
    last_interaction_at: datetime
    telegram_username: Optional[str] = None
    telegram_last_name: Optional[str] = None
    google_sheet_id: Optional[str] = None
    webapp_user_id: Optional[str] = None
    webapp_integration_id: Optional[str] = None
    whatsapp_user_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """
        Creates a User instance from a dictionary (e.g., database response).
        Handles datetime conversion from ISO strings and UUID conversion.
        """
        # Convert ISO datetime strings to datetime objects
        created_at = parse_datetime(data['created_at'])
        last_interaction = parse_datetime(data['last_interaction_at'])
        
        # Convert string to UUID if it's a string
        id_value = UUID(data['id']) if isinstance(data['id'], str) else data['id']
        
        return cls(
            id=id_value,
            telegram_user_id=data['telegram_user_id'],
            telegram_username=data.get('telegram_username'),
            telegram_first_name=data['telegram_first_name'],
            telegram_last_name=data.get('telegram_last_name'),
            google_sheet_id=data.get('google_sheet_id'),
            webapp_user_id=data.get('webapp_user_id'),
            webapp_integration_id=data.get('webapp_integration_id'),
            whatsapp_user_id=data.get('whatsapp_user_id'),
            created_at=created_at,
            last_interaction_at=last_interaction
        )

    def to_dict(self) -> dict:
        """
        Converts the User instance to a dictionary for database storage.
        Handles datetime conversion to ISO strings and UUID to string.
        """
        return {
            'id': str(self.id),
            'telegram_user_id': self.telegram_user_id,
            'telegram_username': self.telegram_username,
            'telegram_first_name': self.telegram_first_name,
            'telegram_last_name': self.telegram_last_name,
            'google_sheet_id': self.google_sheet_id,
            'webapp_user_id': self.webapp_user_id,
            'webapp_integration_id': self.webapp_integration_id,
            'whatsapp_user_id': self.whatsapp_user_id,
            'created_at': self.created_at.isoformat(),
            'last_interaction_at': self.last_interaction_at.isoformat()
        }

    @property
    def is_sheet_linked(self) -> bool:
        """Check if user has linked a Google Sheet."""
        return self.google_sheet_id is not None

    @property
    def is_webapp_linked(self) -> bool:
        """Check if user has linked a Webapp account."""
        return self.webapp_user_id is not None

    @property
    def is_onboarding_complete(self) -> bool:
        """Check if user has completed onboarding by linking at least one method."""
        return self.is_sheet_linked or self.is_webapp_linked

    @property
    def linking_status(self) -> dict:
        """Get the current linking status for both methods."""
        return {
            'sheet_id': self.google_sheet_id,
            'webapp_user_id': self.webapp_user_id
        } 