import logging
from dataclasses import dataclass
from typing import Dict, Optional

from integrations.platforms.whatsapp_adapter import WhatsAppAdapter
from core.onboarding_manager import OnboardingManager
from core.models.common.command_button import CommandButton

logger = logging.getLogger(__name__)

# Constants for button callbacks
BUTTON_CALLBACKS = {
    'LINK_SHEET': 'link_sheet',
    'LINK_WEBAPP': 'link_webapp',
    'CANCEL': 'cancel_onboarding',
    'RETRY_SHEET': 'retry_sheet_url',
    'SWITCH_TO_WEBAPP': 'switch_to_webapp',
    'SWITCH_TO_SHEET': 'switch_to_sheet'
}

@dataclass
class OnboardingState:
    """
    Data class to hold onboarding state information for WhatsApp users.
    
    Attributes:
        state (int): The current state of the onboarding process
        in_progress (bool): Whether the user is currently in the onboarding process
        last_message_id (Optional[str]): ID of the last message sent to the user
    """
    state: int
    in_progress: bool = True
    last_message_id: Optional[str] = None

class WhatsAppOnboardingStateManager:
    """
    Manages the onboarding state for WhatsApp users.
    
    This class provides methods to get and set the onboarding state,
    ensuring consistent state management across different handlers.
    """
    
    def __init__(self, onboarding_manager: OnboardingManager):
        self.onboarding_manager = onboarding_manager
        self.user_states: Dict[str, OnboardingState] = {}
    
    def set_state(self, user_id: str, state: int, in_progress: bool = True, last_message_id: Optional[str] = None) -> None:
        """Sets the onboarding state for a user."""
        self.user_states[user_id] = OnboardingState(
            state=state,
            in_progress=in_progress,
            last_message_id=last_message_id
        )

    def get_state(self, user_id: str) -> OnboardingState:
        """Gets the current onboarding state for a user."""
        return self.user_states.get(
            user_id,
            OnboardingState(
                state=self.onboarding_manager.CHOOSING_LINK_METHOD,
                in_progress=True
            )
        )

    def clear_state(self, user_id: str) -> None:
        """Clears the onboarding state for a user."""
        if user_id in self.user_states:
            del self.user_states[user_id]

class BaseWhatsAppOnboardingHandler:
    """
    Base class for WhatsApp onboarding handlers with common functionality.
    """
    
    def __init__(self):
        self.onboarding_manager = OnboardingManager()
        self.state_manager = WhatsAppOnboardingStateManager(self.onboarding_manager)

    def _end_conversation(self, user_id: str, state: int) -> int:
        """Determines if the conversation should end based on the state."""
        if state == self.onboarding_manager.END:
            self.state_manager.clear_state(user_id)
        return state

class StartHandler(BaseWhatsAppOnboardingHandler):
    """
    Handles the start of the WhatsApp onboarding process.
    """

    async def handle_start(self, webhook_data: dict, adapter: WhatsAppAdapter) -> int:
        """Handles the initial message from a user."""
        user_id = adapter.get_user_id()
        state = await self.onboarding_manager.start_onboarding(adapter)
        self.state_manager.set_state(user_id, state)
        return self._end_conversation(user_id, state)

class SheetHandler(BaseWhatsAppOnboardingHandler):
    """
    Handles Google Sheet related onboarding steps for WhatsApp.
    """

    async def handle_sheet_choice(self, webhook_data: dict, adapter: WhatsAppAdapter) -> int:
        """Handles the user choosing Google Sheet linking."""
        user_id = adapter.get_user_id()
        state = await self.onboarding_manager.handle_sheet_choice(adapter)
        self.state_manager.set_state(user_id, state)
        return self._end_conversation(user_id, state)

    async def handle_sheet_url(self, webhook_data: dict, adapter: WhatsAppAdapter) -> int:
        """Handles the user sending a sheet URL."""
        user_id = adapter.get_user_id()
        state = await self.onboarding_manager.handle_sheet_url(adapter)
        self.state_manager.set_state(user_id, state)
        return self._end_conversation(user_id, state)

class WebappHandler(BaseWhatsAppOnboardingHandler):
    """
    Handles Webapp related onboarding steps for WhatsApp.
    """

    async def handle_webapp_choice(self, webhook_data: dict, adapter: WhatsAppAdapter) -> int:
        """Handles the user choosing Webapp linking."""
        user_id = adapter.get_user_id()
        state = await self.onboarding_manager.handle_webapp_choice(adapter)
        self.state_manager.set_state(user_id, state)
        return self._end_conversation(user_id, state)

    async def handle_webapp_deeplink(self, webhook_data: dict, adapter: WhatsAppAdapter) -> int:
        """Handles webapp deep linking."""
        user_id = adapter.get_user_id()
        state = await self.onboarding_manager.handle_webapp_deeplink(adapter)
        self.state_manager.set_state(user_id, state, state != self.onboarding_manager.END)
        return self._end_conversation(user_id, state)

class GeneralHandler(BaseWhatsAppOnboardingHandler):
    """
    Handles general onboarding operations for WhatsApp.
    """

    async def handle_cancel(self, webhook_data: dict, adapter: WhatsAppAdapter) -> int:
        """Handles onboarding cancellation."""
        user_id = adapter.get_user_id()
        state = await self.onboarding_manager.handle_cancel(adapter)
        self.state_manager.set_state(user_id, state, False)
        return self._end_conversation(user_id, state)

    async def handle_fallback(self, webhook_data: dict, adapter: WhatsAppAdapter) -> int:
        """Handles unrecognized messages during onboarding."""
        user_id = adapter.get_user_id()
        current_state = self.state_manager.get_state(user_id).state
        state = await self.onboarding_manager.handle_fallback(adapter, current_state)
        self.state_manager.set_state(user_id, state, state != self.onboarding_manager.END)
        return self._end_conversation(user_id, state)

class WhatsAppOnboardingHandler:
    """
    Main handler for WhatsApp onboarding process.
    Coordinates all the different handlers and manages the flow.
    """

    def __init__(self):
        self.start_handler = StartHandler()
        self.sheet_handler = SheetHandler()
        self.webapp_handler = WebappHandler()
        self.general_handler = GeneralHandler()

    async def handle_message(self, webhook_data: dict, adapter: WhatsAppAdapter) -> None:
        """
        Main entry point for handling WhatsApp messages.
        Routes messages to appropriate handlers based on current state and message content.
        """
        user_id = adapter.get_user_id()
        message_text = adapter.get_message_text()
        current_state = self.start_handler.state_manager.get_state(user_id)

        # Handle button responses
        if message_text in BUTTON_CALLBACKS.values():
            await self._handle_button_response(webhook_data, adapter, message_text, current_state)
            return

        # Handle regular messages based on state
        if current_state.state == self.start_handler.onboarding_manager.CHOOSING_LINK_METHOD:
            await self.start_handler.handle_start(webhook_data, adapter)
        elif current_state.state == self.start_handler.onboarding_manager.GOOGLE_SHEET_AWAITING_URL:
            await self.sheet_handler.handle_sheet_url(webhook_data, adapter)
        elif current_state.state == self.start_handler.onboarding_manager.WEBAPP_SHOWING_INSTRUCTIONS:
            if message_text.startswith("/start link_"):
                await self.webapp_handler.handle_webapp_deeplink(webhook_data, adapter)
            else:
                await self.general_handler.handle_fallback(webhook_data, adapter)
        else:
            await self.general_handler.handle_fallback(webhook_data, adapter)

    async def _handle_button_response(self, webhook_data: dict, adapter: WhatsAppAdapter, 
                                    callback_data: str, current_state: OnboardingState) -> None:
        """Handles button responses from the user."""
        if callback_data == BUTTON_CALLBACKS['LINK_SHEET']:
            await self.sheet_handler.handle_sheet_choice(webhook_data, adapter)
        elif callback_data == BUTTON_CALLBACKS['LINK_WEBAPP']:
            await self.webapp_handler.handle_webapp_choice(webhook_data, adapter)
        elif callback_data == BUTTON_CALLBACKS['CANCEL']:
            await self.general_handler.handle_cancel(webhook_data, adapter)
        elif callback_data == BUTTON_CALLBACKS['RETRY_SHEET']:
            await self.sheet_handler.handle_sheet_choice(webhook_data, adapter)
        elif callback_data == BUTTON_CALLBACKS['SWITCH_TO_WEBAPP']:
            await self.webapp_handler.handle_webapp_choice(webhook_data, adapter)
        elif callback_data == BUTTON_CALLBACKS['SWITCH_TO_SHEET']:
            await self.sheet_handler.handle_sheet_choice(webhook_data, adapter)
        else:
            await self.general_handler.handle_fallback(webhook_data, adapter) 