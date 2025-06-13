import logging
from flask import Flask, request, jsonify
from api.whatsapp.handlers.message_handler import message_handler
from api.whatsapp.models.whatsapp_message import WhatsAppWebhook
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    logger.info(f"Received webhook verification request - Mode: {mode}, Token: {token}")

    if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
        logger.info("WEBHOOK VERIFICADO")
        return challenge, 200
    else:
        logger.warning("Unauthorized webhook verification attempt")
        return "Unauthorized", 403

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming WhatsApp messages."""
    try:
        data = request.get_json()
        
        # Parse the webhook data first
        webhook_data = WhatsAppWebhook.from_json(data)
        
        # Check if it's a message event
        if webhook_data.is_message_event():
            message = webhook_data.messages[0]
            contact = webhook_data.contacts[0]
            
            if message.is_text_message():
                logger.info(f"Received text message from {contact.name} ({message.from_number}): {message.text.body}")
                await message_handler.handle_message(webhook_data)
            elif message.is_button_reply():
                logger.info(f"Received button reply from {contact.name} ({message.from_number}): {message.get_button_title()} (ID: {message.get_button_id()})")
                await message_handler.handle_response(webhook_data)
            else:
                logger.info(f"Received unknown message type from {contact.name} ({message.from_number}): {message.type}")

            logger.info("Message processed successfully")
        else:
            logger.info("Skipping non-message event")
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)