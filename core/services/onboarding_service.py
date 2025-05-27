import json
import logging
from typing import Optional

from config import config
from core import messages
from core.interfaces.cache_service import CacheService
from core.interfaces.messaging_platform import PlatformUser
from core.models.onboarding_status import OnboardingStatus
from core.services.message_service import MessageService
from core.user_data_manager import UserDataManager
from integrations.cache.redis_client import cache_client

logger = logging.getLogger(__name__)


class OnboardingService:
    """
    Service for managing the onboarding status of users, utilizing cache and messaging.
    """

    CACHE_PREFIX = "onboarding_status"
    CACHE_VERSION = 1
    CACHE_EXPIRY_SECONDS = 3600  # 1 hour expiry for onboarding status

    def __init__(
        self,
        message_service: MessageService,
        cache_service: CacheService = cache_client,
    ) -> None:
        """
        Initializes the onboarding service.

        Args:
            message_service (MessageService): The message service to use for sending messages.
            cache_service (CacheService): The cache service to use.
                                         Defaults to the global instance of RedisCacheClient.
        """
        self.cache_service = cache_service
        self.message_service = message_service
        self.user_manager = UserDataManager()

    def _generate_onboarding_key(self, user_id: str) -> str:
        """
        Generates a unique key for the onboarding status of a user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str: The generated cache key.
        """
        return f"{self.CACHE_PREFIX}:{user_id}:v{self.CACHE_VERSION}"

    def get_onboarding_status(self, user_id: str) -> Optional[OnboardingStatus]:
        """
        Retrieves the onboarding status of a user from the cache.
        If not found, it fetches from the database and caches it.

        Args:
            user_id (str): The ID of the user.

        Returns:
            Optional[OnboardingStatus]: The onboarding status if found, None otherwise.
        """
        cache_key = self._generate_onboarding_key(user_id)
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Onboarding status for user {user_id} retrieved from cache.")
            return OnboardingStatus(**json.loads(cached_data))
        else:
            logger.info(f"Onboarding status for user {user_id} not found from cache.")
            return None

    def save_onboarding_status(self, user_id: str, status: OnboardingStatus) -> bool:
        """
        Saves the onboarding status to the cache.

        Args:
            user_id (str): The ID of the user.
            status (OnboardingStatus): The OnboardingStatus object to save.

        Returns:
            bool: True if the status was saved successfully, False otherwise.
        """
        cache_key = self._generate_onboarding_key(user_id)
        try:
            data_to_save = json.dumps(status.__dict__)
            saved = self.cache_service.set(
                cache_key, data_to_save, expiry=self.CACHE_EXPIRY_SECONDS
            )
            if saved:
                logger.info(f"Onboarding status for user {user_id} saved to cache.")
                return True
            return False
        except Exception as e:
            logger.info(f"Error saving onboarding status to cache: {e}")
            return False

    def delete_onboarding_status(self, user_id: str) -> bool:
        """
        Deletes the onboarding status of a user from the cache.

        Args:
            user_id (str): The ID of the user.

        Returns:
            bool: True if the status was deleted successfully, False otherwise.
        """
        cache_key = self._generate_onboarding_key(user_id)
        deleted = self.cache_service.delete(cache_key)
        if deleted:
            logger.info(f"Onboarding status for user {user_id} deleted from cache.")
            return True
        return False

    async def handle_start_onboarding(self, user: PlatformUser) -> bool:
        """Maneja el inicio del proceso de onboarding"""
        if self.user_manager.is_onboarding_complete(int(user.platform_user_id)):
            logger.info(f"User {user.platform_user_id} is already onboarded.")
            await self.message_service.reply_to_current_message(
                messages.MSG_WELCOME_BACK
            )
            await self.show_user_info(user)
            return True

        user_exists = (
            self.user_manager.get_user_data(int(user.platform_user_id)) is not None
        )
        welcome_message = (
            messages.MSG_WELCOME_BACK if user_exists else messages.MSG_WELCOME
        )

        if not user_exists:
            self._create_user_from_platform_user(user)

        await self.message_service.reply_to_current_message(welcome_message)

        buttons = [
            (messages.BTN_GOOGLE_SHEET, "link_sheet"),
            (messages.BTN_WEBAPP, "link_webapp"),
        ]
        await self.message_service.reply_with_keyboard(
            messages.MSG_PRESENT_OPTIONS, buttons
        )

        return False  # Onboarding not complete yet

    async def handle_sheet_linking(self, user: PlatformUser) -> bool:
        """Maneja la vinculación con Google Sheets"""
        if self.user_manager.is_sheet_linked(int(user.platform_user_id)):
            await self.message_service.reply_to_current_message(
                messages.MSG_SHEET_ALREADY_LINKED
            )
            return True

        await self.message_service.reply_to_current_message(
            messages.MSG_SHEET_CHOICE_CONFIRM
        )

        template_msg = messages.MSG_SHEET_STEP_1_COPY.format(
            template_url=getattr(
                config, "GOOGLE_SHEET_TEMPLATE_URL", "https://example.com"
            )
        )
        await self.message_service.reply_to_current_message(
            template_msg, disable_preview=True
        )

        share_msg = messages.MSG_SHEET_STEP_2_SHARE.format(
            sa_email=getattr(
                config, "GOOGLE_SERVICE_ACCOUNT_EMAIL", "example@email.com"
            )
        )
        await self.message_service.reply_to_current_message(share_msg)

        return False

    async def handle_webapp_linking(self, user: PlatformUser) -> bool:
        """Maneja la vinculación con la aplicación web"""
        if self.user_manager.is_webapp_linked(int(user.platform_user_id)):
            msg = messages.MSG_WEBAPP_ALREADY_LINKED.format(
                url_link=config.WEBAPP_BASE_URL
            )
            await self.message_service.reply_to_current_message(
                msg, disable_preview=True
            )
            return True

        await self.message_service.reply_to_current_message(
            messages.MSG_WEBAPP_CHOICE_CONFIRM
        )

        steps_msg = messages.MSG_WEBAPP_STEPS.format(
            webapp_base_url=config.WEBAPP_BASE_URL
        )
        await self.message_service.reply_to_current_message(
            steps_msg, disable_preview=True
        )

        return False

    async def show_user_info(self, user: PlatformUser):
        """Muestra la información del usuario"""
        from integrations.spreadsheet.spreadsheet import SpreadsheetManager

        user_id = int(user.platform_user_id)
        status = self.user_manager.get_user_linking_status(user_id)

        # Prepare status and links
        has_sheet = status.get("sheet_id")
        has_webapp = status.get("webapp_user_id")

        # Prepare links if services are connected
        spreadsheet_manager = SpreadsheetManager()
        sheet_link = (
            spreadsheet_manager.get_sheet_url(status.get("sheet_id"))
            if has_sheet
            else ""
        )
        webapp_link = config.WEBAPP_BASE_URL

        # Prepare status messages
        sheet_status = (
            messages.STATUS_LINKED.format(url_link=sheet_link)
            if has_sheet
            else messages.STATUS_NOT_LINKED
        )
        webapp_status = (
            messages.STATUS_LINKED.format(url_link=webapp_link)
            if has_webapp
            else messages.STATUS_NOT_LINKED
        )

        # Prepare info message
        info_message = messages.MSG_INFO_STATUS.format(
            sheet_status=sheet_status, webapp_status=webapp_status
        )

        if not self.user_manager.is_onboarding_complete(user_id):
            info_message += messages.MSG_INFO_NOT_LINKED_ACTIONS
        else:
            info_message += messages.MSG_INFO_LINKED_ACTIONS

            # Add commands to link the other method if not already linked
            if not has_sheet or not has_webapp:
                info_message += messages.MSG_INFO_LINK_OTHER_METHOD
                if not has_sheet:
                    info_message += "\n" + messages.MSG_INFO_LINK_SHEET_CMD
                if not has_webapp:
                    info_message += "\n" + messages.MSG_INFO_LINK_WEBAPP_CMD

        await self.message_service.reply_to_current_message(
            info_message, disable_preview=True
        )

    def _create_user_from_platform_user(self, user: PlatformUser):
        """Crea un usuario desde un PlatformUser"""
        self.user_manager.create_user(
            telegram_user_id=int(user.platform_user_id),
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
