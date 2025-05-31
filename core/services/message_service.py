import logging
import pickle
from typing import Optional
from core.interfaces.cache_service import CacheService
from integrations.cache.redis_client import cache_client
from core.models.message import Message
from core.models.message import Source  # Assuming Source enum is in the same file

logger = logging.getLogger(__name__)

class MessageService:
    """
    Service for managing user messages, utilizing cache and considering the platform.
    """
    CACHE_PREFIX = "messages"
    CACHE_VERSION = 1
    CACHE_EXPIRY_SECONDS = 24 * 60 * 60  # 24 hours * 60 minutes * 60 seconds = 1 day

    def __init__(self, cache_service: CacheService = cache_client) -> None:
        """
        Initializes the message service.

        Args:
            cache_service (CacheService): The cache service by default is the global instance of RedisCacheClient.
        """
        self.cache_service = cache_service

    def _generate_message_key(self, user_id: str, message_id: str, platform: Source) -> str:
        """
        Generates a unique key for a message based on user ID, message ID, and platform.

        Args:
            user_id (str): The ID of the user.
            message_id (str): The ID of the message on the platform.
            platform (Source): The platform where the message originated.

        Returns:
            str: The generated cache key.
        """
        return f"{self.CACHE_PREFIX}:{user_id}:{platform.value}:{message_id}:v{self.CACHE_VERSION}"

    def get_message(self, user_id: str, message_id: str, platform: Source) -> Optional[Message]:
        """
        Retrieves a specific message of a user from the cache based on user ID, message ID, and platform.

        Args:
            user_id (str): The ID of the user.
            message_id (str): The ID of the message on the platform.
            platform (Source): The platform where the message originated.

        Returns:
            Optional[Message]: The message if found in the cache, None otherwise.
        """
        cache_key = self._generate_message_key(user_id, message_id, platform)
        cached_data = self.cache_service.get(cache_key)
        if cached_data:
            logger.info(f"Message (ID: {message_id}, User: {user_id}, Platform: {platform.value}) retrieved from cache.")
            return pickle.loads(cached_data) # TODO: pickle is not secure and fast, we could implement an alternative with pydantic or manual serialization.
        else:
            logger.info(f"Message (ID: {message_id}, User: {user_id}, Platform: {platform.value}) not found in cache.")
            # here we can implement a fallback logic (not needed for now)
            return None

    def save_message(self, message: Message) -> bool:
        """
        Saves a message to the cache.

        Args:
            message (Message): The Message object to save.

        Returns:
            bool: True if the message was saved to the cache successfully, False otherwise.
        """
        cache_key = self._generate_message_key(message.user_id, message.message_id, message.source)
        try:
            data_to_save = pickle.dumps(message)  # TODO: pickle is not secure and fast, we could implement an alternative with pydantic or manual serialization.
            self.cache_service.set(cache_key, data_to_save, expiry=self.CACHE_EXPIRY_SECONDS)
            logger.info(f"Message (ID: {message.message_id}, User: {message.user_id,}, Platform: {message.source.value}) saved to cache.")
            return True
        except Exception as e:
            logger.info(f"Error saving message to cache: {e}")
            return False

    def delete_message(self, user_id: str, message_id: str, platform: Source) -> bool:
        """
        Deletes a specific message of a user from the cache based on user ID, message ID, and platform.

        Args:
            user_id (str): The ID of the user.
            message_id (str): The ID of the message on the platform.
            platform (Source): The platform where the message originated.

        Returns:
            bool: True if the message was deleted from the cache successfully, False otherwise.
        """
        cache_key = self._generate_message_key(user_id, message_id, platform)
        deleted = self.cache_service.delete(cache_key)
        if deleted:
            logger.info(f"Message (ID: {message_id}, User: {user_id}, Platform: {platform.value}) deleted from cache.")
            return True
        return False