import logging
import asyncio

from pywa_async import WhatsApp, types, filters
from api.whatsapp.handlers.message_handler import WhatsAppV2MessageHandler
from api.whatsapp.handlers.callback_handler import WhatsAppV2CallbackHandler
from api.whatsapp.handlers.audio_hanlder import WhatsAppV2AudioHandler

logger = logging.getLogger(__name__)

class WhatsAppV2Handlers:
    """
    Main handler for WhatsApp v2 that acts as a middleware to distribute messages to specific handlers.
    This class manages all the specific handlers and routes messages accordingly.
    """
    
    def __init__(self, wa: WhatsApp):
        """
        Initialize the main handler with a WhatsApp client instance.

        Args:
            wa: The WhatsApp client instance
        """
        self.wa = wa
        self.message_handler = WhatsAppV2MessageHandler(wa)
        self.callback_handler = WhatsAppV2CallbackHandler(wa)
        self.audio_handler = WhatsAppV2AudioHandler(wa)

    def register_handlers(self) -> None:
        """
        Register all the handlers with the WhatsApp client.
        This method sets up all the necessary event handlers.
        """
        # Register message handler for text messages
        @self.wa.on_message(filters=filters.text)
        async def on_message(client: WhatsApp, msg: types.Message):
            logger.info(f"[WhatsApp][Text] Received message from webhook | Message ID: {msg.id}")
            asyncio.create_task(self.message_handler.handle_message(msg))
            logger.info(f"[WhatsApp][Text] Message processing task created | Message ID: {msg.id}")

        # Register audio handler
        @self.wa.on_message(filters=filters.audio)
        async def on_audio(client: WhatsApp, msg: types.Message):
            logger.info(f"[WhatsApp][Audio] Received audio message from webhook | Message ID: {msg.id}")
            asyncio.create_task(self.audio_handler.handle_audio_message(msg))
            logger.info(f"[WhatsApp][Audio] Audio message processing task created | Message ID: {msg.id}")
            

        # Register voice handler
        @self.wa.on_message(filters=filters.voice)
        async def on_voice(client: WhatsApp, msg: types.Message):
            logger.info(f"[WhatsApp][Voice] Received voice message from webhook | Message ID: {msg.id}")
            asyncio.create_task(self.audio_handler.handle_audio_message(msg))
            logger.info(f"[WhatsApp][Voice] Voice message processing task created | Message ID: {msg.id}")

        # Register callback handler
        @self.wa.on_callback_button()
        async def on_callback(client: WhatsApp, callback: types.CallbackButton):
            logger.info(f"[WhatsApp][Callback] Received callback event | Callback ID: {callback.id}")
            asyncio.create_task(self.callback_handler.handle_callback(callback))
            logger.info(f"[WhatsApp][Callback] Callback processing task created | Callback ID: {callback.id}")

        logger.info("WhatsApp v2 handlers registered successfully")
