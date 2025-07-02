from abc import ABC, abstractmethod
from typing import List

from core.models.common.command_button import CommandButton
from core.models.message import Message
from core.models.user import User

class PlatformAdapter(ABC):
    """
    Abstract base class for platform adapters.
    This class defines the interface that all platform adapters must implement.
    """

    @abstractmethod
    def get_platform_name(self) -> str:
        """
        Return the name of the platform.

        Returns:
            str: The platform name
        """
        pass
    
    @abstractmethod
    def get_message_id(self) -> str:
        """
        Returns the unique identifier of the message.

        Returns:
            str: The message ID.
        """
        pass
    
    
    @abstractmethod
    def map_to_message(self, message_text: str = None) -> Message:
        """
        Returns message model

        Returns:
            Message model.
        """
        pass
    
    @abstractmethod
    def get_message_text(self) -> str:
        """
        Returns the text of the message from the update.

        Returns:
            str: The text of the message.
        """
        pass

    @abstractmethod
    def get_platform_user_id(self) -> str:
        """
        Returns the unique identifier of the user.

        Returns:
            str: The user ID.
        """
        pass

    @abstractmethod
    def get_user(self) -> User:
        """
        Returns the user object from the update.

        Returns:
            The user object or None if not present.
        """
        pass

    @abstractmethod
    def get_voice_message(self):
        """
        Returns the voice message from the update if available.

        Returns:
            The voice message object or None if not present.
        """
        pass

    @abstractmethod
    def get_voice_file_id(self) -> str:
        """
        Returns the file ID of the voice message if available.

        Returns:
            str: The file ID of the voice message.
        """
        pass

    @abstractmethod
    def get_callback_query(self):
        """
        Returns the callback query from the update if available.

        Returns:
            The callback query object or None if not present.
        """
        pass

    @abstractmethod
    def reply_text(self, text: str, **kwargs):
        """
        Sends a text reply to the user.

        Args:
            text (str): The text to be sent as a reply.
            **kwargs: Additional keyword arguments for platform-specific options.
        """
        pass

    @abstractmethod
    def reply_with_buttons(self, text: str, buttons: List[CommandButton], **kwargs):
        """
        Sends a reply with buttons to the user.

        Args:
            text (str): The text to be sent as a reply.
            buttons (list): A list of buttons to be included in the reply.
            **kwargs: Additional keyword arguments for platform-specific options.
        """
        pass

    @abstractmethod
    async def clean_up_processing_message(self, message):
        """
        Cleans up a processing message if the platform supports it.

        Args:
            message: The message to clean up.
        """
        pass
    
    @abstractmethod
    async def react_message(self, emoji):
        """
        Cleans up a processing message if the platform supports it.

        Args:
            message: The message to clean up.
        """
        pass
