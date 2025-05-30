from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from core.interfaces.platform_adapter import PlatformAdapter
from core.models.common.command_button import CommandButton


class TelegramAdapter(PlatformAdapter):
    """
    Adapter for Telegram platform to handle message replies and button interactions.
    Implements the PlatformAdapter interface.
    """

    def __init__(self, update):
        """
        Initializes the TelegramAdapter with the given update.

        Args:
            update: The Telegram Update object containing the message and context.
        """
        self.update = update

    def get_message_id(self) -> str:
        """
        Returns the unique identifier of the message.

        Returns:
            str: The message ID.
        """
        return str(self.update.message.message_id)

    def get_message_text(self) -> str:
        """
        Returns the text of the message from the update.

        Returns:
            str: The text of the message.
        """
        return self.update.message.text if self.update.message else ""

    def get_user_id(self) -> str:
        """
        Returns the unique identifier of the user.

        Returns:
            str: The user ID.
        """
        return str(self.update.effective_user.id)

    def get_user(self):
        """
        Returns the user object from the update.

        Returns:
            The user object or None if not present.
        """
        return self.update.effective_user if self.update.effective_user else None

    def get_voice_message(self):
        """
        Returns the voice message from the update if available.

        Returns:
            The voice message object or None if not present.
        """
        return self.update.message.voice if self.update.message else None

    def get_voice_file_id(self) -> str:
        """
        Returns the file ID of the voice message if available.

        Returns:
            str: The file ID of the voice message or None if not present.
        """
        voice = self.get_voice_message()
        return voice.file_id if voice else None

    def get_callback_query(self):
        """
        Returns the callback query from the update if available.

        Returns:
            The callback query object or None if not present.
        """
        return self.update.callback_query if self.update.callback_query else None

    def reply_text(self, text: str, **kwargs):
        """
        Sends a text reply to the user.

        Args:
            text (str): The text to be sent as a reply.
            *kwargs: Additional keyword arguments for platform-specific options.
        """
        return self.update.message.reply_text(text, **kwargs)

    def reply_with_buttons(self, text: str, buttons: list[CommandButton], **kwargs):
        """
        Sends a reply with buttons to the user.

        Args:
            text (str): The text to be sent as a reply.
            buttons (list): A list of CommandButton objects to be included in the reply.
            **kwargs: Additional keyword arguments for platform-specific options.
        """

        keyboard = self._button_to_keyboard(buttons)
        reply_markup = InlineKeyboardMarkup(keyboard)

        return self.update.message.reply_text(text, reply_markup=reply_markup, **kwargs)

    def _button_to_keyboard(self, buttons: list[CommandButton]):
        """
        Converts a list of CommandButton objects to a format suitable for Telegram's InlineKeyboardMarkup.

        Args:
            buttons (list): A list of CommandButton objects.

        Returns:
            list: A list of lists containing InlineKeyboardButton objects.
        """

        return [
            [InlineKeyboardButton(text=button.text, callback_data=button.callback_data)]
            for button in buttons
        ]
