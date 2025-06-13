from typing import List, Dict, Optional
from core.interfaces.platform_adapter import PlatformAdapter
from core.models.common.command_button import CommandButton
from core.models.message import Message, Source
from core.models.user import User
from integrations.whatsapp.whatsapp_client import whatsapp_api_client
from api.whatsapp.models.whatsapp_message import WhatsAppWebhook, WhatsAppMessage, WhatsAppContact

class WhatsAppAdapter(PlatformAdapter):
    """
    Adapter for WhatsApp platform to handle message replies and interactions.
    Implements the PlatformAdapter interface.
    """

    def __init__(self, webhook_data: WhatsAppWebhook, user: Optional[User] = None):
        """
        Initializes the WhatsAppAdapter with the given webhook data.

        Args:
            webhook_data (WhatsAppWebhook): The structured webhook data containing the message and context.
            user (Optional[User]): The user associated with this message, if any.
        """
        self.webhook_data = webhook_data
        self.api_client = whatsapp_api_client
        self.name = Source.WHATSAPP
        self.user = user
        self._extract_message_data()

    def _extract_message_data(self):
        """Extracts relevant message data from the webhook payload."""
        # Get the first message and contact
        self.message = self.webhook_data.messages[0] if self.webhook_data.messages else None
        self.contact = self.webhook_data.contacts[0] if self.webhook_data.contacts else None
        self.metadata = self.webhook_data.metadata
        
    def get_platform_name(self) -> str:
        """
        Returns the platform name.

        Returns:
            str: Platform name.
        """
        return self.name

    def get_message_id(self) -> str:
        """
        Returns the unique identifier of the message.

        Returns:
            str: The message ID.
        """
        return self.message.message_id if self.message else ""

    def map_to_message(self, message_text: str = None) -> Message:
        """
        Builds a Message object with the current message data.

        Args:
            message_text (str, optional): The text to use for the message. If None, uses the current message text.

        Returns:
            Message: A Message object containing the message data.
        """
        message = Message(
            user_id=self.get_user_id(),
            message_id=self.get_message_id(),
            message_text=message_text if message_text is not None else self.get_message_text(),
            source=self.name
        )
        return message

    def get_message_text(self) -> str:
        """
        Returns the text of the message from the webhook data.

        Returns:
            str: The text of the message.
        """
        return self.message.text.body if self.message and self.message.text else ""

    def get_user_id(self) -> str:
        """
        Returns the unique identifier of the user.

        Returns:
            str: The user ID.
        """
        return self.message.from_number if self.message else ""

    def get_user(self):
        """
        Returns the user associated with this message, if any.
        """
        return self.user

    def get_voice_message(self):
        """
        WhatsApp voice messages are not implemented in this version.
        Returns None.
        """
        return None

    def get_voice_file_id(self) -> str:
        """
        WhatsApp voice messages are not implemented in this version.
        Returns empty string.
        """
        return ""

    def get_callback_query(self):
        """
        WhatsApp doesn't have a direct equivalent to callback queries.
        Returns None.
        """
        return None

    def reply_text(self, text: str) -> None:
        """
        Send a text message.
        
        Args:
            text: The message text
        """
        phone_number_id = self.metadata.phone_number_id
        to = self.get_user_id()
        return self.api_client.send_message(phone_number_id, to, text)

    def reply_with_buttons(self, text: str, buttons: List[CommandButton], **kwargs):
        """
        Send a message with buttons.
        
        Args:
            text: The message text
            buttons: List of buttons to include
        """
        phone_number_id = self.metadata.phone_number_id
        to = self.get_user_id()
        
        # Convert CommandButton objects to WhatsApp button format
        whatsapp_buttons = [
            {
                "id": button.callback_data,
                "title": button.text
            }
            for button in buttons
        ]
        
        return self.api_client.send_interactive_message(
            phone_number_id=phone_number_id,
            to=to,
            body_text=text,
            buttons=whatsapp_buttons
        )

    async def clean_up_processing_message(self, message):
        """
        WhatsApp doesn't support message deletion.
        This is a no-op implementation.
        """
        pass

    def get_platform_user_id(self) -> str:
        """
        Returns the unique identifier of the user in the WhatsApp platform.
        This is the phone number of the user.

        Returns:
            str: The WhatsApp user ID (phone number)
        """
        return self.message.from_number if self.message else ""
