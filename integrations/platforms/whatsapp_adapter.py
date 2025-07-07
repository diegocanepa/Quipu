from typing import List
from pywa_async import WhatsApp, types

from core.interfaces.platform_adapter import PlatformAdapter
from core.models.common.command_button import CommandButton
from core.models.message import Message, Source
from core.models.user import User

class WhatsAppV2Adapter(PlatformAdapter):
    """
    Adapter for WhatsApp platform to handle message replies and button interactions.
    Implements the PlatformAdapter interface using PyWa library.
    """

    def __init__(self, wa: WhatsApp, update: types.Message, user: User = None):
        """
        Initializes the WhatsAppV2Adapter with the given update.

        Args:
            wa: The WhatsApp client instance
            update: The WhatsApp Message object containing the message and context
            user: The User object containing the user data from our database.
        """
        self.wa = wa
        self.update = update
        self.user = user
        self.name = Source.WHATSAPP

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
        return str(self.update.id)

    def map_to_message(self, message_text: str = None) -> Message:
        """
        Builds a Message object with the current message data.

        Args:
            message_text (str, optional): The text to use for the message. If None, uses the current message text.
                                          This is used for transcription where we pass the transcripted text from the audio.

        Returns:
            Message: A Message object containing the message data.
        """
        message = Message(
            user_id=self.user.id,
            message_id=self.get_message_id(),
            message_text=message_text if message_text is not None else self.get_message_text(),
            source=self.name
        )
        return message

    def get_message_text(self) -> str:
        """
        Returns the text of the message from the update.

        Returns:
            str: The text of the message.
        """
        return self.update.text if hasattr(self.update, 'text') else ""

    def get_platform_user_id(self) -> str:
        """
        Returns the unique identifier of the user depending on the platform.
        For WhatsApp, this is the wa_id which is the phone number with the country code.

        Returns:
            str: The WhatsApp ID (wa_id) of the user.
        """
        return str(self.update.from_user.wa_id)

    def get_user(self) -> User:
        """
        Returns the user object from the update.

        Returns:
            The user object or None if not present.
        """
        return self.user

    def get_voice_message(self):
        """
        Returns the voice message from the update if available.

        Returns:
            The voice message object or None if not present.
        """
        return self.update.voice if hasattr(self.update, 'voice') else None

    def get_voice_file_id(self) -> str:
        """
        Returns the file ID of the voice message if available.

        Returns:
            str: The file ID of the voice message or None if not present.
        """
        voice = self.get_voice_message()
        return voice.id if voice else None

    def get_callback_query(self):
        """
        Returns the callback query from the update if available.

        Returns:
            The callback query object or None if not present.
        """
        return self.update.callback_data if hasattr(self.update, 'callback_data') else None

    async def reply_text(self, text: str, **kwargs):
        """
        Sends a text reply to the user.

        Args:
            text (str): The text to be sent as a reply.
            **kwargs: Additional keyword arguments for platform-specific options.
        """
        return await self.wa.send_message(
            to=self._sanitize_number(self.get_platform_user_id()),
            text=text,
            **kwargs
        )

    async def reply_with_buttons(self, text: str, buttons: List[CommandButton], **kwargs):
        """
        Sends a reply with buttons to the user.

        Args:
            text (str): The text to be sent as a reply.
            buttons (list): A list of CommandButton objects to be included in the reply.
            **kwargs: Additional keyword arguments for platform-specific options.
        """
        keyboard = self._button_to_keyboard(buttons)
        return await self.wa.send_message(
            to=self._sanitize_number(self.get_platform_user_id()),
            text=text,
            buttons=keyboard,
            **kwargs
        )
    
    async def react_message(self, emoji):
        """
        Reacts to a WhatsApp message with the specified emoji.

        Args:
            emoji (str): The emoji to react with.

        Returns:
            The result of the WhatsApp API react_message call.
        """
        return await self.wa.send_reaction(
            to=self._sanitize_number(self.get_platform_user_id()),
            message_id=self.get_message_id(),
            emoji=emoji
        )
        
    async def delete_reaction(self):
        """
        Deletes the reaction from the message.
        """
        return await self.wa.send_reaction(
            to=self._sanitize_number(self.get_platform_user_id()),
            message_id=self.get_message_id(),
            emoji=""
        )
        
    def clean_up_processing_message(self, message):
        """
        Cleans up a processing message if the platform supports it.

        Args:
            message: The message to clean up.
        """
        # WhatsApp doesn't support message deletion
        pass
    
    

    def _button_to_keyboard(self, buttons: list[CommandButton]):
        """
        Converts a list of CommandButton objects to a format suitable for WhatsApp's button format.

        Args:
            buttons (list): A list of CommandButton objects.

        Returns:
            list: A list of Button objects for WhatsApp.
        """
        return [
            types.Button(
                title=button.text,
                callback_data=button.callback_data
            )
            for button in buttons
        ]
    
            
    def _sanitize_number(self, raw_number: str) -> str:
        """
        Sanitizes a phone number for WhatsApp API use.

        Args:
            raw_number (str): The raw phone number

        Returns:
            str: The sanitized phone number
        """
        # Argentina: if it starts with 549, remove the '9'
        if raw_number.startswith("549"):
            return "54" + raw_number[3:]
        return raw_number