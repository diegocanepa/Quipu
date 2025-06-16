import logging
from typing import Optional

from pywa_async import WhatsApp, types
from core.message_processor import MessageProcessor
from core.user_data_manager import UserDataManager
from integrations.platforms.whatsapp_v2_adapter import WhatsAppV2Adapter
from api.whatsapp.messages import messages
from config import config

logger = logging.getLogger(__name__)

class WhatsAppV2CallbackHandler:
    """
    Handler for WhatsApp button callbacks using PyWa library.
    This class handles button interactions like confirm and cancel actions.
    """
    
    def __init__(self, wa: WhatsApp):
        """
        Initialize the handler with a WhatsApp client instance.

        Args:
            wa: The WhatsApp client instance
        """
        self.wa = wa
        self.message_processor = MessageProcessor()
        self.user_manager = UserDataManager()

    def _extract_message_id_from_button(self, button_id: str) -> Optional[str]:
        """
        Extracts the message ID from a button ID.
        Example: from 'cancel#message_id'
        returns 'message_id'
        
        Args:
            button_id: The button ID containing the message ID
            
        Returns:
            Optional[str]: The extracted message ID if found, None otherwise
        """
        try:
            if '#' in button_id:
                return button_id.split('#')[1]
            return None
        except Exception as e:
            logger.error(f"Error extracting message ID from button: {str(e)}")
            return None

    async def handle_callback(self, callback: types.CallbackButton) -> None:
        """
        Handle button callbacks from WhatsApp.
        """
        platform = None
        try:
            # Extraer el tipo de callback y el ID del mensaje
            callback_type, message_id = callback.data.split('#')
            user = self.user_manager.get_user_by_whatsapp_user_id(callback.from_user.wa_id)
            platform= WhatsAppV2Adapter(self.wa, callback, user)
        

            if callback_type == "confirm":
                response = self.message_processor.save_and_respond(
                    user_id=user.id,
                    message_id=message_id,
                    platform=platform
                )
            elif callback_type == "cancel":
                response = self.message_processor.cancel_and_respond(
                    user_id=user.id,
                    message_id=message_id,
                    platform=platform
                )
            else:
                response = "Invalid callback type"

            # Enviar la respuesta
            await platform.reply_text(response)

        except Exception as e:
            logger.error(
                f"Error handling WhatsApp button response. User: {callback.from_user.wa_id}, "
                f"Message ID: {callback.data}, Error: {str(e)}"
            )
            if platform:
                await platform.reply_text(messages.MSG_UNEXPECTED_ERROR)
