import logging
from typing import Dict, Optional
import re
from datetime import datetime
import json

from core.message_processor import MessageProcessor
from core.user_data_manager import UserDataManager
from integrations.platforms.whatsapp_adapter import WhatsAppAdapter
from config import config
from api.whatsapp.messages import messages
from api.whatsapp.models.whatsapp_message import WhatsAppWebhook

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
        try:
            # Pattern to match everything after "Mi código de vinculación es:"
            # :TODO I don't like using regex. I think it could be a good change in a future
            pattern = r"Mi código de vinculación es:\s*(.+)"
            match = re.search(pattern, message_text)
            linking_code = match.group(1).strip() if match else None
            
            if linking_code:
                logger.debug(f"Successfully extracted linking code: {linking_code}")
            else:
                logger.debug("No linking code found in message")
                
            return linking_code
            
        except Exception as e:
            logger.error(f"Error extracting linking code: {str(e)}", exc_info=True)
            return None

    def _is_linking_message(self, message_text: str) -> bool:
        """
        Checks if a message is a linking code message.
        
        Args:
            message_text: The text of the message
            
        Returns:
            bool: True if it's a linking message, False otherwise
        """
        logger.debug(f"Checking linking message. Received text: '{message_text}'")
        is_linking = "Hola Quipu!" in message_text and "Mi código de vinculación es:" in message_text
        logger.debug(f"Message is linking message: {is_linking}")
        return is_linking

    async def _handle_linking_code(self, platform: WhatsAppAdapter, linking_code: str) -> None:
        """
        Handles the linking code message by updating existing user or creating a new one.
        
        Args:
            platform: The WhatsApp platform adapter
            linking_code: The linking code from the message
        """
        whatsapp_user_id = platform.get_platform_user_id()
        logger.info(f"Processing linking code for WhatsApp user {whatsapp_user_id}")
        
        try:
            # Check if user exists with this linking code
            existing_user = self.user_manager.get_user_by_id(user_id=linking_code)
            
            if existing_user:
                # Update existing user with WhatsApp ID
                updated_user = self.user_manager.update_user(
                    user_id=linking_code,
                    whatsapp_user_id=whatsapp_user_id
                )
                
                if not updated_user:
                    logger.error(f"Failed to update user with WhatsApp ID. User: {whatsapp_user_id}, Code: {linking_code}")
                    platform.reply_text(messages.MSG_LINKING_INVALID)
                    return
                
                logger.info(f"Successfully updated user with WhatsApp ID. User: {whatsapp_user_id}, ID: {updated_user.id}, Code: {linking_code}")
                platform.reply_text(messages.MSG_LINKING_SUCCESS)
                return
            
            # Create new user with linking code
            user = self.user_manager.create_user(
                id=linking_code,
                webapp_integration_id=linking_code,
                whatsapp_user_id=whatsapp_user_id
            )
            
            if not user:
                logger.error(f"Failed to create user with linking code. User: {whatsapp_user_id}, Code: {linking_code}")
                platform.reply_text(messages.MSG_LINKING_INVALID)
                return
            
            logger.info(f"Successfully created new user with WhatsApp ID. User: {whatsapp_user_id}, ID: {user.id}, Code: {linking_code}")
            platform.reply_text(messages.MSG_LINKING_SUCCESS)
            
        except Exception as e:
            logger.error(f"Error handling linking code. User: {whatsapp_user_id}, Code: {linking_code}, Error: {str(e)}")
            platform.reply_text(messages.MSG_UNEXPECTED_ERROR)

    async def handle_message(self, webhook_data: WhatsAppWebhook) -> None:
        """
        Main entry point for handling WhatsApp messages.
        
        Args:
            webhook_data: The structured WhatsApp webhook data
        """
        platform = None
        platform_user_id = None
        message_id = None
        
        try:
            # Get the first message and contact from the webhook data
            message = webhook_data.messages[0]
            contact = webhook_data.contacts[0]
            
            # Initialize platform adapter without user
            platform = WhatsAppAdapter(webhook_data, None)
            
            # Extract basic message info
            platform_user_id = message.from_number
            message_id = message.message_id
            message_text = message.text.body if message.text else ""
            
            logger.info(f"Processing WhatsApp message. ID: {message_id}, User: {platform_user_id}, Text: {message_text}")
            
            if not platform_user_id:
                logger.error(f"No user ID found in message. Message ID: {message_id}")
                return

            # Handle linking message
            if self._is_linking_message(message_text):
                linking_code = self._extract_linking_code(message_text)
                if linking_code:
                    await self._handle_linking_code(platform, linking_code)
                    return
                else:
                    logger.warning(f"Linking code not found in message. ID: {message_id}, User: {platform_user_id}, Text: {message_text}")
                    platform.reply_text(messages.MSG_LINKING_CODE_NOT_FOUND)
                    return

            # Get or create user
            user = self.user_manager.get_user_by_whatsapp_user_id(platform_user_id)
            if not user:
                logger.info(f"New user registration required. User: {platform_user_id}")
                               
                platform.reply_text(messages.MSG_WELCOME.format(webapp_url=config.WEBAPP_BASE_URL))
                return
            
            # Update platform adapter with user
            platform = WhatsAppAdapter(webhook_data, user)

            # Process regular message
            logger.info(f"Processing regular message. User: {user.id}, Platform User: {platform_user_id}, Message ID: {message_id}")
            
            user_message = platform.map_to_message()
            await self.message_processor.process_and_respond(
                user_message=user_message,
                platform=platform
            )

        except Exception as e:
            logger.error(f"Error handling WhatsApp message. User: {platform_user_id}, Message ID: {message_id}, Error: {str(e)}")
            platform.reply_text(messages.MSG_UNEXPECTED_ERROR)

# Initialize the main handler
message_handler = WhatsAppMessageHandler() 