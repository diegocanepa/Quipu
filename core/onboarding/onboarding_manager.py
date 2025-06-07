from abc import ABC, abstractmethod
from typing import Optional, List, Tuple

from core.interfaces.platform_adapter import PlatformAdapter
from core.models.common.command_button import CommandButton
from core.user_data_manager import UserDataManager
from core.onboarding import states
from core import messages
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from config import config

class OnboardingManager:
    def __init__(self):
        self.user_manager = UserDataManager()
        self.spreadsheet_manager = SpreadsheetManager()

    async def start_onboarding(self, platform: PlatformAdapter) -> int:
        """Handles the start of onboarding process."""
        user_id = platform.get_user_id()
        user = platform.get_user()

        if self.user_manager.is_onboarding_complete(user_id):
            await platform.reply_text(messages.MSG_WELCOME_BACK)
            return states.FINISHED

        user_exists = self.user_manager.get_user_data(user_id) is not None
        welcome_message = messages.MSG_WELCOME_BACK if user_exists else messages.MSG_WELCOME

        if not user_exists:
            self.user_manager.create_user(
                telegram_user_id=user_id,
                username=user.username if hasattr(user, 'username') else None,
                first_name=user.first_name if hasattr(user, 'first_name') else None,
                last_name=user.last_name if hasattr(user, 'last_name') else None
            )

        await platform.reply_text(welcome_message)

        buttons = [
            CommandButton(messages.BTN_GOOGLE_SHEET, 'link_sheet'),
            CommandButton(messages.BTN_WEBAPP, 'link_webapp')
        ]
        await platform.reply_with_buttons(messages.MSG_PRESENT_OPTIONS, buttons)

        return states.CHOOSING_LINK_METHOD

    async def handle_sheet_choice(self, platform: PlatformAdapter) -> int:
        """Handles the user choosing Google Sheet linking."""
        user_id = platform.get_user_id()
        
        if self.user_manager.is_sheet_linked(user_id):
            await platform.reply_text(messages.MSG_SHEET_ALREADY_LINKED)
            return states.FINISHED
        
        await platform.reply_text(messages.MSG_SHEET_CHOICE_CONFIRM)
        await platform.reply_text(
            messages.MSG_SHEET_STEP_1_COPY.format(template_url=config.GOOGLE_SHEET_TEMPLATE_URL)
        )
        await platform.reply_text(
            messages.MSG_SHEET_STEP_2_SHARE.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL)
        )
        
        return states.GOOGLE_SHEET_AWAITING_URL

    async def handle_sheet_url(self, platform: PlatformAdapter) -> int:
        """Handles the user sending a sheet URL."""
        user_id = platform.get_user_id()
        sheet_url = platform.get_message_text().strip()

        sheet_id = self.spreadsheet_manager.get_sheet_id_from_url(sheet_url)
        if not sheet_id:
            error_buttons = self._get_error_keyboard(states.GOOGLE_SHEET_AWAITING_URL)
            await platform.reply_with_buttons(
                messages.MSG_SHEET_LINK_INVALID_URL,
                error_buttons
            )
            return states.GOOGLE_SHEET_AWAITING_URL

        processing_msg = await platform.reply_text(messages.MSG_SHEET_LINK_CHECKING)
        access_granted = self.spreadsheet_manager.check_access(sheet_id)
        await self._clean_up_processing_message(platform, processing_msg)

        if access_granted:
            self.user_manager.set_sheet_linked(user_id, sheet_id)
            await platform.reply_text(messages.MSG_SHEET_LINK_SUCCESS)
            return states.FINISHED
        
        error_buttons = self._get_error_keyboard(states.GOOGLE_SHEET_AWAITING_URL)
        await platform.reply_with_buttons(
            messages.MSG_SHEET_LINK_FAILED_ACCESS.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL),
            error_buttons
        )
        return states.GOOGLE_SHEET_AWAITING_URL

    async def handle_webapp_choice(self, platform: PlatformAdapter) -> int:
        """Handles the user choosing Webapp linking."""
        user_id = platform.get_user_id()

        if self.user_manager.is_webapp_linked(user_id):
            await platform.reply_text(
                messages.MSG_WEBAPP_ALREADY_LINKED.format(url_link=config.WEBAPP_BASE_URL)
            )
            return states.FINISHED

        await platform.reply_text(messages.MSG_WEBAPP_CHOICE_CONFIRM)
        await platform.reply_text(
            messages.MSG_WEBAPP_STEPS.format(webapp_base_url=config.WEBAPP_BASE_URL),
            disable_preview=True
        )

        return states.WEBAPP_SHOWING_INSTRUCTIONS

    async def handle_webapp_deeplink(self, platform: PlatformAdapter) -> int:
        """Handles webapp deep linking."""
        user_id = platform.get_user_id()
        message_text = platform.get_message_text()

        if not message_text:
            return states.FINISHED

        command_parts = message_text.split(" ", 1)
        if len(command_parts) < 2:
            return states.FINISHED

        payload = command_parts[1]
        if not payload.startswith("link_"):
            return states.FINISHED

        webapp_user_id = payload[5:]  # Remove "link_" prefix

        processing_msg = await platform.reply_text(messages.MSG_WEBAPP_DEEPLINK_TRIGGERED)

        if webapp_user_id:
            self.user_manager.set_webapp_linked(user_id, webapp_user_id)
            await self._clean_up_processing_message(platform, processing_msg)
            await platform.reply_text(messages.MSG_WEBAPP_LINK_SUCCESS)
            return states.FINISHED
        
        error_buttons = self._get_error_keyboard(states.WEBAPP_SHOWING_INSTRUCTIONS)
        await platform.reply_with_buttons(
            messages.MSG_WEBAPP_LINK_FAILED.format(webapp_base_url=config.WEBAPP_BASE_URL),
            error_buttons
        )
        return states.WEBAPP_SHOWING_INSTRUCTIONS

    async def handle_cancel(self, platform: PlatformAdapter) -> int:
        """Handles onboarding cancellation."""
        await platform.reply_text(messages.MSG_CANCEL_ONBOARDING_CONFIRM)
        return states.FINISHED

    async def handle_fallback(self, platform: PlatformAdapter, current_state: int) -> int:
        """Handles unrecognized messages during onboarding."""
        if current_state == states.FINISHED:
            return states.FINISHED

        state_messages = {
            states.GOOGLE_SHEET_AWAITING_URL: messages.MSG_SHEET_LINK_INVALID_URL,
            states.WEBAPP_SHOWING_INSTRUCTIONS: messages.MSG_WEBAPP_LINK_FAILED,
            states.CHOOSING_LINK_METHOD: messages.MSG_ONBOARDING_REQUIRED
        }

        message = state_messages.get(current_state, messages.MSG_ONBOARDING_ERROR)
        error_buttons = self._get_error_keyboard(current_state)
        
        if current_state == states.WEBAPP_SHOWING_INSTRUCTIONS:
            message = message.format(webapp_base_url=config.WEBAPP_BASE_URL)
        
        await platform.reply_with_buttons(message, error_buttons)
        return current_state or states.CHOOSING_LINK_METHOD

    def _get_error_keyboard(self, current_state: int) -> List[CommandButton]:
        """Returns appropriate keyboard for error states."""
        if current_state == states.GOOGLE_SHEET_AWAITING_URL:
            return [
                CommandButton("Retry", "retry_sheet_url"),
                CommandButton("Switch to Webapp", "switch_to_webapp"),
                CommandButton("Cancel", "cancel_onboarding")
            ]
        elif current_state == states.WEBAPP_SHOWING_INSTRUCTIONS:
            return [
                CommandButton("Switch to Sheet", "switch_to_sheet"),
                CommandButton("Cancel", "cancel_onboarding")
            ]
        return [CommandButton("Cancel", "cancel_onboarding")]

    async def _clean_up_processing_message(self, platform: PlatformAdapter, message):
        """Cleans up processing message if platform supports it."""
        if hasattr(platform, 'clean_up_processing_message'):
            await platform.clean_up_processing_message(message) 