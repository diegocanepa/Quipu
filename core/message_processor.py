# core/message_processor.py
import logging
from typing import List

from core.data_server import DataSaver
from core.interfaces.platform_adapter import PlatformAdapter
from core.llm_processor import LLMProcessor, ProcessingResult
from core.messages import (
    CANCEL_BUTTON,
    CANCEL_MESSAGE,
    CONFIRM_BUTTON,
    MESSAGE_NOT_FOUND,
    SAVE_ERROR,
    SAVE_ERROR_CTA,
    SAVE_SUCCESS,
    SAVE_SUCCESS_CTA,
    UNEXPECTED_ERROR,
    USER_NOT_FOUND,
)
from core.models.common.command_button import CommandButton
from core.models.message import Message
from core.services.message_service import MessageService
from core.user_data_manager import UserDataManager

logger = logging.getLogger(__name__)

CONFIRM_SAVE = 1


class MessageProcessor:
    def __init__(self):
        # TODO: Implement dependency injection and singleton pattern.
        self.llm_processor = LLMProcessor()
        self.message_service = MessageService()
        self.data_saver = DataSaver()
        self.user_data_manager = UserDataManager()

    async def process_and_respond(
        self,
        user_message: Message,
        platform: PlatformAdapter,
    ) -> int:
        """
        Processes the user's message using the LLMProcessor and sends responses
        with confirmation options.

        Args:
            update: The Telegram Update object.
            context: The Telegram Context object.

        Returns:
            int: The state for the conversation handler (CONFIRM_SAVE).
        """
        results: List[ProcessingResult] = await self.llm_processor.process_content(
            user_message.message_text
        )

        if not results:
            await platform.reply_text(UNEXPECTED_ERROR)
            return -1  # Means conversations END but we have to check how whatsapp works

        for idx, result in enumerate(results):
            if result.error:
                await platform.reply_text(f"❌ {result.error}")
            else:
                response_text = result.data_object.to_presentation_string(
                    platform.get_platform_name()
                )
                callback_id = f"{platform.get_message_id()}_{idx}"

                buttons: List[CommandButton] = [
                    CommandButton(
                        text=CONFIRM_BUTTON, callback_data=f"confirm#{callback_id}"
                    ),
                    CommandButton(
                        text=CANCEL_BUTTON, callback_data=f"cancel#{callback_id}"
                    ),
                ]

                await platform.reply_with_buttons(text=response_text, buttons=buttons)

                response_message = Message(
                    user_id=user_message.user_id,
                    message_id=callback_id,
                    message_text=response_text,
                    message_object=result.data_object,
                    source=user_message.source,
                )

                self.message_service.save_message(message=response_message)

        return CONFIRM_SAVE

    def save_and_respond(
        self, user_id: str, message_id: str, platform: PlatformAdapter
    ) -> str:
        """
        Process and save a message for a specific user.

        Args:
            user_id (str): The ID of the user
            message_id (str): The ID of the message to process
            platform (PlatformAdapter): The platform adapter instance

        Returns:
            str: Response message
        """
        recovered_message = self.message_service.get_message(
            user_id=user_id,
            message_id=message_id,
            platform=platform.get_platform_name(),
        )
        user = self.user_data_manager.get_user_data(user_id)

        if not recovered_message:
            logger.warning(
                "Message not found",
                extra={
                    "user_id": user_id,
                    "message_id": message_id,
                    "platform": platform.get_platform_name(),
                },
            )
            return MESSAGE_NOT_FOUND

        if not user:
            logger.warning(
                "User not found",
                extra={
                    "user_id": user_id,
                    "message_id": message_id,
                    "platform": platform.get_platform_name(),
                },
            )
            return USER_NOT_FOUND

        success = self.data_saver.save_content(
            recovered_message.message_object, user=user
        )

        if success:
            logger.info(
                "Message saved successfully",
                extra={
                    "user_id": user_id,
                    "message_id": message_id,
                    "platform": platform.get_platform_name(),
                },
            )

            self._delete_message(recovered_message)

            return self._format_save_response(
                recovered_message.message_object.get_description(), True
            )
        else:
            logger.error(
                "Failed to save message",
                extra={
                    "user_id": user_id,
                    "message_id": message_id,
                    "platform": platform.get_platform_name(),
                },
            )

            self._delete_message(recovered_message)

            return self._format_save_response(
                recovered_message.message_object.get_description(), False
            )

    def cancel_and_respond(
        self, user_id: str, message_id: str, platform: PlatformAdapter
    ) -> str:
        """
        Process a cancellation request for a message. This function retrieves the message,
        deletes it if found, and returns a cancellation response.

        Args:
            user_id (str): The unique identifier of the user who owns the message
            message_id (str): The unique identifier of the message to cancel
            platform (PlatformAdapter): The platform adapter instance used to interact with the messaging platform

        Returns:
            str: A message indicating that the action was cancelled
        """
        recovered_message = self.message_service.get_message(
            user_id=user_id,
            message_id=message_id,
            platform=platform.get_platform_name(),
        )

        if recovered_message:
            self._delete_message(recovered_message)

        return CANCEL_MESSAGE

    def _delete_message(self, message: Message):
        """
        Delete a message from storage. This is an internal helper method that handles the
        actual deletion of messages from the message service.

        Args:
            message (Message): The message object to be deleted.

        """
        self.message_service.delete_message(
            user_id=message.user_id,
            message_id=message.message_id,
            platform=message.source,
        )

    def _format_save_response(self, message_text: str, success: bool) -> str:
        """
        Formats the response message for save operations.

        Args:
            message_text (str): The original message text
            success (bool): Whether the save operation was successful

        Returns:
            str: Formatted response message
        """
        status = SAVE_SUCCESS if success else SAVE_ERROR
        cta = SAVE_SUCCESS_CTA if success else SAVE_ERROR_CTA

        return f'"{message_text}" - {status} \n\n{cta}'
