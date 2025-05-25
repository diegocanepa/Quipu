import json
import logging
from typing import Optional
from core.interfaces.cache_service import CacheService
from integrations.cache.redis_client import cache_client
from core.models.onboarding_status import OnboardingStatus

logger = logging.getLogger(__name__)

class OnboardingService:
    """
    Service for managing the onboarding status of users, utilizing cache.
    """
    CACHE_PREFIX = "onboarding_status"
    CACHE_VERSION = 1
    CACHE_EXPIRY_SECONDS = 3600  # 1 hour expiry for onboarding status

    def __init__(self, cache_service: CacheService = cache_client) -> None:
        """
        Initializes the onboarding service.

        Args:
            cache_service (CacheService): The cache service to use.
                                         Defaults to the global instance of RedisCacheClient.
        """
        self.cache_service = cache_service

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
            saved = self.cache_service.set(cache_key, data_to_save, expiry=self.CACHE_EXPIRY_SECONDS)
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