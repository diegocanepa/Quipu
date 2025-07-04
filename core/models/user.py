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
    telegram_user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    last_interaction_at: Optional[datetime] = None
    google_sheet_id: Optional[str] = None
    webapp_user_id: Optional[UUID] = None
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
        webapp_user_id = UUID(data['webapp_user_id']) if data.get('webapp_user_id') and isinstance(data['webapp_user_id'], str) else data.get('webapp_user_id')
        
        return cls(
            id=id_value,
            telegram_user_id=data['telegram_user_id'],
            google_sheet_id=data.get('google_sheet_id'),
            webapp_user_id=webapp_user_id,
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
            'google_sheet_id': self.google_sheet_id,
            'webapp_user_id': str(self.webapp_user_id) if self.webapp_user_id else None,
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