import logging
from typing import Dict, Optional, Tuple
import re

from core import messages
from core.message_processor import MessageProcessor
from core.user_data_manager import UserDataManager
from integrations.platforms.whatsapp_adapter import WhatsAppAdapter
from config import config

logger = logging.getLogger(__name__)

class WhatsAppMessageHandler:
    """
    Main handler for WhatsApp messages.
    This class handles basic message processing and user verification.
    """
    
    def __init__(self):
        self.message_processor = MessageProcessor()
        self.user_manager = UserDataManager()

    def _extract_linking_code(self, message_text: str) -> Optional[str]:
        """
        Extracts the linking code from a WhatsApp message.
        
        Args:
            message_text: The text of the message
            
        Returns:
            Optional[str]: The linking code if found, None otherwise
        """
        # Pattern to match the linking code format
        pattern = r"Mi código de vinculación es:\s*(\w+)"
        match = re.search(pattern, message_text)
        return match.group(1) if match else None

    def _is_linking_message(self, message_text: str) -> bool:
        """
        Checks if a message is a linking code message.
        
        Args:
            message_text: The text of the message
            
        Returns:
            bool: True if it's a linking message, False otherwise
        """
        return "Hola Quipu!" in message_text and "Mi código de vinculación es:" in message_text

    async def _handle_linking_code(self, platform: WhatsAppAdapter, linking_code: str) -> None:
        """
        Handles the linking code message by creating or updating the user.
        
        Args:
            platform: The WhatsApp platform adapter
            linking_code: The linking code from the message
        """
        try:
            # Get the WhatsApp user ID
            whatsapp_user_id = platform.get_platform_user_id()
            
            # Try to find user by linking code
            user = self.user_manager.get_user_by_linking_code(linking_code)
            
            if not user:
                platform.reply_text("❌ Código de vinculación inválido. Por favor, verifica el código e intenta nuevamente.")
                return
            
            # Update user with WhatsApp ID
            user.whatsapp_user_id = whatsapp_user_id
            self.user_manager.update_user(user)
            
            platform.reply_text(
                "✅ ¡Cuenta vinculada exitosamente!\n\n"
                "Ahora puedes usar Quipu desde WhatsApp para:\n"
                "• Registrar tus gastos diarios 🛒\n"
                "• Mantener un registro de tus ingresos 💵\n"
                "• Y mucho más...\n\n"
                "¡Comienza a usar Quipu enviando un mensaje!"
            )
            
        except Exception as e:
            logger.error(f"Error handling linking code: {str(e)}", exc_info=True)
            platform.reply_text(messages.UNEXPECTED_ERROR_WPS)

    async def handle_message(self, message: Dict) -> None:
        """
        Main entry point for handling WhatsApp messages.
        
        Args:
            message: The raw WhatsApp message
        """
        try:
            #  We don't have user yet
            platform = WhatsAppAdapter(message, None)
            
            # Extract user information
            platform_user_id = platform.get_platform_user_id()
            message_id = platform.get_message_id()
            message_text = platform.get_message_text()
            
            logger.info(f"Processing WhatsApp message [ID: {message_id}] from user [ID: {platform_user_id}]")
            
            if not platform_user_id:
                logger.error("No user ID found in message", extra={"message_id": message_id})
                return

            # Check if it's a linking message
            if self._is_linking_message(message_text):
                linking_code = self._extract_linking_code(message_text)
                if linking_code:
                    await self._handle_linking_code(platform, linking_code)
                    return
                else:
                    platform.reply_text("❌ No se pudo encontrar el código de vinculación en el mensaje. Por favor, asegúrate de incluir el código correctamente.")
                    return

            # Check if user exists
            user = self.user_manager.get_user_by_whatsapp_user_id(platform_user_id)
            if not user:
                logger.info(f"New user registration required [WhatsApp ID: {platform_user_id}]")
                # Create new user
                user = self.user_manager.create_user_from_whatsapp(platform_user_id)
                if not user:
                    platform.reply_text(messages.UNEXPECTED_ERROR_WPS)
                    return
                platform.reply_text(messages.MSG_WELCOME)
                return
            
            # Update platform adapter with user
            platform = WhatsAppAdapter(message, user)

            # Process regular message
            logger.info(f"Processing message for user [ID: {user.id}, WhatsApp ID: {platform_user_id}]")
            user_message = platform.map_to_message()
            
            await self.message_processor.process_and_respond(
                user_message=user_message,
                platform=platform
            )

        except Exception as e:
            logger.error(
                f"Error handling WhatsApp message: {str(e)}",
                extra={
                    "error_type": type(e).__name__,
                    "platform_user_id": platform_user_id if 'platform_user_id' in locals() else None,
                    "message_id": message_id if 'message_id' in locals() else None
                },
                exc_info=True
            )
            platform.reply_text(messages.UNEXPECTED_ERROR_WPS)

# Initialize the main handler
message_handler = WhatsAppMessageHandler() 