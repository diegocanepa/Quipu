from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class State(str, Enum):
    """
    Class to represent the state of the onboarding process.
    """
    CHOOSING_LINK_METHOD = 1
    GOOGLE_SHEET_AWAITING_URL = 2
    WEBAPP_SHOWING_INSTRUCTIONS = 3

@dataclass
class OnboardingStatus:
    """
    Class to represent the onboarding status of a user.
    """
    user_id: str = field(metadata={"description": "User ID from Supabase. Not telegram, not whatsapp, not webapp"})
    state: State = field(metadata={"description": "State of the onboarding process"})