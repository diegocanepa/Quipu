from typing import List, Dict, Optional
from core.interfaces.platform_adapter import PlatformAdapter
from core.models.common.command_button import CommandButton
from core.models.message import Message, Source
from core.models.user import User
from integrations.whatsapp.whatsapp_client import whatsapp_api_client

class WhatsAppAdapter(PlatformAdapter):
    """
    Adapter for WhatsApp platform to handle message replies and interactions.
    Implements the PlatformAdapter interface.
    """

    def __init__(self, webhook_data: dict, api_client=None):
        """
        Initializes the WhatsAppAdapter with the given webhook data.

        Args:
            webhook_data (dict): The webhook data containing the message and context.
            api_client: Optional WhatsApp API client instance. If not provided, uses the default client.
        """
        self.webhook_data = webhook_data
        self.api_client = api_client if api_client else whatsapp_api_client
        self.name = Source.WHATSAPP
        self._extract_message_data()

    def _extract_message_data(self):
        """Extracts relevant message data from the webhook payload."""
        self.entry = self.webhook_data.get("entry", [{}])[0]
        self.changes = self.entry.get("changes", [{}])[0]
        self.value = self.changes.get("value", {})
        self.messages = self.value.get("messages", [{}])[0]
        self.metadata = self.value.get("metadata", {})
        
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
        return self.messages.get("id", "")

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
        return self.messages.get("text", {}).get("body", "")

    def get_user_id(self) -> str:
        """
        Returns the unique identifier of the user.

        Returns:
            str: The user ID.
        """
        return self.messages.get("from", "")

    def get_user(self):
        """
        WhatsApp doesn't provide detailed user information in webhooks.
        Returns None as this information is not available.
        """
        return None

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
        phone_number_id = self.metadata.get("phone_number_id")
        to = self.get_user_id()
        return self.api_client.send_message(phone_number_id, to, text)

    def reply_with_buttons(self, text: str, buttons: List[CommandButton], **kwargs):
        """
        Send a message with buttons.
        
        Args:
            text: The message text
            buttons: List of buttons to include
        """
        phone_number_id = self.metadata.get("phone_number_id")
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
        return self.messages.get("from", "")
