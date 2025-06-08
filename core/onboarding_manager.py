import logging
from typing import List

from core.interfaces.platform_adapter import PlatformAdapter
from core.models.common.command_button import CommandButton
from core.user_data_manager import UserDataManager
from core import messages
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from config import config

logger = logging.getLogger(__name__)

class OnboardingManager:
    """
    Manages the onboarding process for users across different platforms.
    
    The onboarding flow consists of the following states:
    1. CHOOSING_LINK_METHOD (1): Initial state where user chooses between Google Sheet or Webapp
    2. GOOGLE_SHEET_AWAITING_URL (2): Waiting for user to provide Google Sheet URL
    3. WEBAPP_SHOWING_INSTRUCTIONS (3): Showing instructions for Webapp linking
    4. END (4): Final state indicating onboarding completion or cancellation
    
    Each method in this class handles a specific part of the onboarding flow and returns
    the next state in the conversation.
    """

    # States for the onboarding conversation handler
    CHOOSING_LINK_METHOD = 1
    GOOGLE_SHEET_AWAITING_URL = 2
    WEBAPP_SHOWING_INSTRUCTIONS = 3
    END = 4

    def __init__(self):
        self.user_manager = UserDataManager()
        self.spreadsheet_manager = SpreadsheetManager()

    async def start_onboarding(self, platform: PlatformAdapter) -> int:
        """
        Initiates the onboarding process.
        
        Flow:
        1. Checks if user is already onboarded
        2. Creates user if doesn't exist
        3. Presents linking options (Google Sheet or Webapp)
        
        Returns:
            int: Next state in the conversation
            - states.END if user is already onboarded
            - states.CHOOSING_LINK_METHOD if user needs to choose linking method
        """
        user_id = platform.get_user_id()
        user = platform.get_user()

        logger.info(f"Starting onboarding process for user {user_id}")

        if self.user_manager.is_onboarding_complete(user_id):
            logger.info(f"User {user_id} already onboarded, skipping process")
            await platform.reply_text(messages.MSG_WELCOME_BACK)
            return self.END

        user_exists = self.user_manager.get_user_data(user_id) is not None
        welcome_message = messages.MSG_WELCOME_BACK if user_exists else messages.MSG_WELCOME

        if not user_exists:
            logger.info(f"Creating new user {user_id}")
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

        logger.info(f"User {user_id} presented with linking options")
        return self.CHOOSING_LINK_METHOD

    async def handle_sheet_choice(self, platform: PlatformAdapter) -> int:
        """
        Handles the user's choice to link a Google Sheet.
        
        Flow:
        1. Checks if user already has a sheet linked
        2. Shows instructions for sheet linking
        3. Waits for sheet URL
        
        Returns:
            int: Next state in the conversation
            - states.END if sheet is already linked
            - states.GOOGLE_SHEET_AWAITING_URL to wait for sheet URL
        """
        user_id = platform.get_user_id()
        logger.info(f"User {user_id} chose Google Sheet linking")
        
        if self.user_manager.is_sheet_linked(user_id):
            logger.info(f"User {user_id} already has sheet linked")
            await platform.reply_text(messages.MSG_SHEET_ALREADY_LINKED)
            return self.END
        
        await platform.reply_text(messages.MSG_SHEET_CHOICE_CONFIRM)
        await platform.reply_text(
            messages.MSG_SHEET_STEP_1_COPY.format(template_url=config.GOOGLE_SHEET_TEMPLATE_URL)
        )
        await platform.reply_text(
            messages.MSG_SHEET_STEP_2_SHARE.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL)
        )
        
        logger.info(f"User {user_id} shown sheet linking instructions")
        return self.GOOGLE_SHEET_AWAITING_URL

    async def handle_sheet_url(self, platform: PlatformAdapter) -> int:
        """
        Processes the Google Sheet URL provided by the user.
        
        Flow:
        1. Validates the sheet URL
        2. Checks access permissions
        3. Links the sheet if access is granted
        
        Returns:
            int: Next state in the conversation
            - states.END if sheet is successfully linked
            - states.GOOGLE_SHEET_AWAITING_URL if URL is invalid or access is denied
        """
        user_id = platform.get_user_id()
        sheet_url = platform.get_message_text().strip()
        logger.info(f"Processing sheet URL for user {user_id}")

        sheet_id = self.spreadsheet_manager.get_sheet_id_from_url(sheet_url)
        if not sheet_id:
            logger.warning(f"Invalid sheet URL provided by user {user_id}")
            error_buttons = self._get_error_keyboard(self.GOOGLE_SHEET_AWAITING_URL)
            await platform.reply_with_buttons(
                messages.MSG_SHEET_LINK_INVALID_URL,
                error_buttons
            )
            return self.GOOGLE_SHEET_AWAITING_URL

        processing_msg = await platform.reply_text(messages.MSG_SHEET_LINK_CHECKING)
        access_granted = self.spreadsheet_manager.check_access(sheet_id)
        await platform.clean_up_processing_message(processing_msg)

        if access_granted:
            logger.info(f"Sheet access granted for user {user_id}")
            self.user_manager.set_sheet_linked(user_id, sheet_id)
            await platform.reply_text(messages.MSG_SHEET_LINK_SUCCESS)
            return self.END
        
        logger.warning(f"Sheet access denied for user {user_id}")
        error_buttons = self._get_error_keyboard(self.GOOGLE_SHEET_AWAITING_URL)
        await platform.reply_with_buttons(
            messages.MSG_SHEET_LINK_FAILED_ACCESS.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL),
            error_buttons
        )
        return self.GOOGLE_SHEET_AWAITING_URL

    async def handle_webapp_choice(self, platform: PlatformAdapter) -> int:
        """
        Handles the user's choice to link the Webapp.
        
        Flow:
        1. Checks if user already has webapp linked
        2. Shows instructions for webapp linking
        
        Returns:
            int: Next state in the conversation
            - states.END if webapp is already linked
            - states.WEBAPP_SHOWING_INSTRUCTIONS to show linking instructions
        """
        user_id = platform.get_user_id()
        logger.info(f"User {user_id} chose Webapp linking")

        if self.user_manager.is_webapp_linked(user_id):
            logger.info(f"User {user_id} already has webapp linked")
            await platform.reply_text(
                messages.MSG_WEBAPP_ALREADY_LINKED.format(url_link=config.WEBAPP_BASE_URL)
            )
            return self.END

        await platform.reply_text(messages.MSG_WEBAPP_CHOICE_CONFIRM)
        await platform.reply_text(
            messages.MSG_WEBAPP_STEPS.format(webapp_base_url=config.WEBAPP_BASE_URL),
            disable_web_page_preview=True
        )

        logger.info(f"User {user_id} shown webapp linking instructions")
        return self.WEBAPP_SHOWING_INSTRUCTIONS

    async def handle_webapp_deeplink(self, platform: PlatformAdapter) -> int:
        """
        Processes the webapp deep linking.
        
        Flow:
        1. Extracts webapp user ID from deep link
        2. Links the webapp if ID is valid
        
        Returns:
            int: Next state in the conversation
            - states.END if webapp is successfully linked or if deep link is invalid
            - states.WEBAPP_SHOWING_INSTRUCTIONS if linking fails
        """
        user_id = platform.get_user_id()
        message_text = platform.get_message_text()
        logger.info(f"Processing webapp deeplink for user {user_id}")

        if not message_text:
            logger.warning(f"Empty message text in deeplink for user {user_id}")
            return self.END

        command_parts = message_text.split(" ", 1)
        if len(command_parts) < 2:
            logger.warning(f"Invalid deeplink format for user {user_id}")
            return self.END

        payload = command_parts[1]
        if not payload.startswith("link_"):
            logger.warning(f"Invalid deeplink prefix for user {user_id}")
            return self.END

        webapp_user_id = payload[5:]  # Remove "link_" prefix

        processing_msg = await platform.reply_text(messages.MSG_WEBAPP_DEEPLINK_TRIGGERED)

        if webapp_user_id:
            logger.info(f"Webapp linking successful for user {user_id}")
            self.user_manager.set_webapp_linked(user_id, webapp_user_id)
            await platform.clean_up_processing_message(processing_msg)
            await platform.reply_text(messages.MSG_WEBAPP_LINK_SUCCESS)
            return self.END
        
        logger.warning(f"Webapp linking failed for user {user_id}")
        error_buttons = self._get_error_keyboard(self.WEBAPP_SHOWING_INSTRUCTIONS)
        await platform.reply_with_buttons(
            messages.MSG_WEBAPP_LINK_FAILED.format(webapp_base_url=config.WEBAPP_BASE_URL),
            error_buttons
        )
        return self.WEBAPP_SHOWING_INSTRUCTIONS

    async def handle_cancel(self, platform: PlatformAdapter) -> int:
        """
        Handles the cancellation of the onboarding process.
        
        Returns:
            int: Always returns states.END to terminate the conversation
        """
        user_id = platform.get_user_id()
        logger.info(f"User {user_id} cancelled onboarding")
        await platform.reply_text(messages.MSG_CANCEL_ONBOARDING_CONFIRM)
        return self.END

    async def handle_fallback(self, platform: PlatformAdapter, current_state: int) -> int:
        """
        Handles unrecognized messages during onboarding.
        
        Flow:
        1. Shows appropriate error message based on current state
        2. Provides relevant options to continue or cancel
        
        Returns:
            int: Next state in the conversation
            - states.END if conversation should end
            - current_state if user should retry current step
            - states.CHOOSING_LINK_METHOD if state is invalid
        """
        user_id = platform.get_user_id()
        if current_state == self.END:
            return self.END

        logger.warning(f"Unhandled message in state {current_state} for user {user_id}")
        state_messages = {
            self.GOOGLE_SHEET_AWAITING_URL: messages.MSG_SHEET_LINK_INVALID_URL,
            self.WEBAPP_SHOWING_INSTRUCTIONS: messages.MSG_WEBAPP_LINK_FAILED,
            self.CHOOSING_LINK_METHOD: messages.MSG_ONBOARDING_REQUIRED
        }

        message = state_messages.get(current_state, messages.MSG_ONBOARDING_ERROR)
        error_buttons = self._get_error_keyboard(current_state)
        
        if current_state == self.WEBAPP_SHOWING_INSTRUCTIONS:
            message = message.format(webapp_base_url=config.WEBAPP_BASE_URL)
        
        await platform.reply_with_buttons(message, error_buttons)
        return current_state or self.CHOOSING_LINK_METHOD

    def _get_error_keyboard(self, current_state: int) -> List[CommandButton]:
        """
        Returns appropriate keyboard buttons for error states.
        
        Args:
            current_state (int): The current state in the onboarding flow
            
        Returns:
            List[CommandButton]: List of buttons appropriate for the current state
        """
        if current_state == self.GOOGLE_SHEET_AWAITING_URL:
            return [
                CommandButton(messages.BTN_SWITCH_TO_WEBAPP, "switch_to_webapp"),
                CommandButton(messages.BTN_CANCEL_ONBOARDING, "cancel_onboarding")
            ]
        elif current_state == self.WEBAPP_SHOWING_INSTRUCTIONS:
            return [
                CommandButton(messages.BTN_SWITCH_TO_SHEET, "switch_to_sheet"),
                CommandButton(messages.BTN_CANCEL_ONBOARDING, "cancel_onboarding")
            ]
        elif current_state == self.CHOOSING_LINK_METHOD:
            return [
                CommandButton(messages.BTN_GOOGLE_SHEET, 'link_sheet'),
                CommandButton(messages.BTN_WEBAPP, 'link_webapp'),
                CommandButton(messages.BTN_CANCEL_ONBOARDING, "cancel_onboarding")
            ]
        return [CommandButton(messages.BTN_CANCEL_ONBOARDING, "cancel_onboarding")]