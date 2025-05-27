import json
import logging
from typing import Any, List, Optional

from core.interfaces.cache_service import CacheService
from core.interfaces.messaging_platform import (
    MessagingPlatformInterface,
    PlatformMessage,
    PlatformUpdate,
    PlatformUser,
)
from core.models.message import (
    Message,
    Source,  # Assuming Source enum is in the same file
)
from integrations.cache.redis_client import cache_client

logger = logging.getLogger(__name__)


class MessageService:
    """
    Service for managing user messages, utilizing cache and considering the platform.
    """

    CACHE_PREFIX = "messages"
    CACHE_VERSION = 1
    CACHE_EXPIRY_SECONDS = 24 * 60 * 60  # 24 hours * 60 minutes * 60 seconds = 1 day

    def __init__(
        self,
        platform_adapter: MessagingPlatformInterface,
        cache_service: CacheService = cache_client,
    ):
        """
        Initializes the message service.

        Args:
            platform_adapter (MessagingPlatformInterface): The platform adapter for sending messages.
            cache_service (CacheService): The cache service by default is the global instance of RedisCacheClient.
        """
        self.cache_service = cache_service
        self.platform_adapter = platform_adapter
        self.current_platform_update = None
        self.current_context = None

    def _generate_message_key(
        self, user_id: str, message_id: str, platform: Source
    ) -> str:
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

    def get_message(
        self, user_id: str, message_id: str, platform: Source
    ) -> Optional[Message]:
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
            logger.info(
                f"Message (ID: {message_id}, User: {user_id}, Platform: {platform.value}) retrieved from cache."
            )
            return Message(**json.loads(cached_data))
        else:
            logger.info(
                f"Message (ID: {message_id}, User: {user_id}, Platform: {platform.value}) not found in cache."
            )
            # here we can implement a fallback logic (not needed for now)
            return None

    def save_message(self, user_id: str, message: Message) -> bool:
        """
        Saves a message to the cache.

        Args:
            user_id (str): The ID of the user who sent the message.
            message (Message): The Message object to save.

        Returns:
            bool: True if the message was saved to the cache successfully, False otherwise.
        """
        cache_key = self._generate_message_key(
            user_id, message.message_id, message.source
        )
        try:
            message_dict = message.__dict__.copy()
            message_dict["message_object"] = message.message_object.model_dump(
                mode="json"
            )
            data_to_save = json.dumps(message_dict)
            self.cache_service.set(
                cache_key, data_to_save, expiry=self.CACHE_EXPIRY_SECONDS
            )
            logger.info(
                f"Message (ID: {message.message_id}, User: {user_id}, Platform: {message.source.value}) saved to cache."
            )
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
            logger.info(
                f"Message (ID: {message_id}, User: {user_id}, Platform: {platform.value}) deleted from cache."
            )
            return True
        return False

    def set_current_update_context(
        self, platform_update: PlatformUpdate, context: Any = None
    ):
        """Establece el contexto actual de la actualización"""
        self.current_platform_update = platform_update
        self.current_context = context

    async def send_message(self, user_id: str, text: str, **kwargs) -> Any:
        """Envía un mensaje de texto al usuario"""
        return await self.platform_adapter.send_message(user_id, text, **kwargs)

    async def send_message_with_keyboard(
        self, user_id: str, text: str, buttons: List[tuple], **kwargs
    ) -> Any:
        """Envía un mensaje con teclado inline"""
        return await self.platform_adapter.send_message_with_keyboard(
            user_id, text, buttons, **kwargs
        )

    async def reply_to_current_message(self, text: str, **kwargs) -> Any:
        """Responde al mensaje actual usando el contexto guardado"""
        if not self.current_platform_update or not self.current_platform_update.user:
            raise ValueError("No hay contexto de mensaje actual establecido")

        return await self.send_message(
            self.current_platform_update.user.platform_user_id, text, **kwargs
        )

    async def reply_with_keyboard(
        self, text: str, buttons: List[tuple], **kwargs
    ) -> Any:
        """Responde al mensaje actual con teclado"""
        if not self.current_platform_update or not self.current_platform_update.user:
            raise ValueError("No hay contexto de mensaje actual establecido")

        return await self.send_message_with_keyboard(
            self.current_platform_update.user.platform_user_id, text, buttons, **kwargs
        )

    async def edit_message(self, message_id: str, text: str, **kwargs) -> Any:
        """Edita un mensaje existente"""
        return await self.platform_adapter.edit_message(message_id, text, **kwargs)

    async def answer_callback_query(
        self, callback_query_id: str, text: Optional[str] = None
    ) -> Any:
        """Responde a una consulta de callback"""
        return await self.platform_adapter.answer_callback_query(
            callback_query_id, text
        )

    async def get_voice_file_data(self, voice_message_data: Any) -> Optional[bytes]:
        """Obtiene los datos de un archivo de voz"""
        return await self.platform_adapter.get_voice_file_data(voice_message_data)

    def get_current_user(self) -> Optional[PlatformUser]:
        """Obtiene el usuario actual del contexto"""
        if self.current_platform_update:
            return self.current_platform_update.user
        return None

    def get_current_message(self) -> Optional[PlatformMessage]:
        """Obtiene el mensaje actual del contexto"""
        if self.current_platform_update:
            return self.current_platform_update.message
        return None

    def create_keyboard_buttons(self, buttons: List[tuple]) -> List[tuple]:
        """Helper para crear botones de teclado"""
        return buttons
