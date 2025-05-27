import logging
from typing import Any, List, Optional

from core.interfaces.messaging_platform import (
    MessagingPlatformInterface,
    PlatformMessage,
    PlatformUpdate,
    PlatformUser,
)

logger = logging.getLogger(__name__)


class DiscordAdapter(MessagingPlatformInterface):
    """Adaptador específico para la plataforma Discord"""

    def __init__(self, bot_instance=None):
        self.bot = bot_instance

    def set_bot_context(self, bot_instance):
        """Establece el bot de Discord"""
        self.bot = bot_instance

    async def send_message(self, user_id: str, text: str, **kwargs) -> Any:
        """Envía un mensaje de texto al usuario en Discord"""
        # Discord implementation would go here
        # Example: await self.bot.get_user(int(user_id)).send(text)
        logger.info(f"Discord: Sending message to {user_id}: {text}")
        pass

    async def send_message_with_keyboard(
        self, user_id: str, text: str, buttons: List[tuple], **kwargs
    ) -> Any:
        """Envía un mensaje con botones en Discord"""
        # Discord implementation with components/buttons would go here
        logger.info(f"Discord: Sending message with buttons to {user_id}: {text}")
        pass

    async def edit_message(self, message_id: str, text: str, **kwargs) -> Any:
        """Edita un mensaje existente en Discord"""
        # Discord implementation would go here
        logger.info(f"Discord: Editing message {message_id}: {text}")
        pass

    async def answer_callback_query(
        self, callback_query_id: str, text: Optional[str] = None
    ) -> Any:
        """Responde a una interacción en Discord"""
        # Discord implementation for interaction responses would go here
        logger.info(f"Discord: Answering interaction {callback_query_id}: {text}")
        pass

    async def get_voice_file_data(self, voice_message_data: Any) -> Optional[bytes]:
        """Obtiene los datos de un archivo de voz de Discord"""
        # Discord implementation would go here
        logger.info("Discord: Getting voice file data")
        return None

    def convert_to_platform_update(self, discord_message) -> PlatformUpdate:
        """Convierte un mensaje de Discord a formato agnóstico"""
        platform_update = PlatformUpdate()

        # Discord implementation would convert discord_message to platform_update
        # This is just an example structure
        if hasattr(discord_message, "author"):
            platform_update.user = PlatformUser(
                platform_user_id=str(discord_message.author.id),
                username=discord_message.author.name,
                first_name=discord_message.author.display_name,
                platform_type="discord",
            )

        if hasattr(discord_message, "content"):
            platform_update.message = PlatformMessage(
                text=discord_message.content,
                user=platform_update.user,
                message_id=str(discord_message.id),
                is_voice=False,  # Discord voice handling would be different
            )

        return platform_update
