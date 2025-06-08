from flask import Flask, request, jsonify
import logging
from integrations.platforms.whatsapp_adapter import WhatsAppAdapter
from integrations.whatsapp.whatsapp_client import WhatsAppAPIClient
from api.whatsapp.handlers.whatsapp_onboarding_handlers import WhatsAppOnboardingHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

VERIFY_TOKEN = "BDra5aZ4RIuPI3nXXVZs4MbHoJxvKJ4w"
ACCESS_TOKEN = "EAARqE6wSFykBO7ZBA1OTmucFJgsD1FfAdr65jGdnt6NbbpB3ulNpy6JAQYh4UkvgS467tb23nJTbcIKJzIgOpX3nUgIz41WyXxVaIJCNxO8X7fmGcABiG7ZBOjXpEhvH0TMf1ZC5jtgZBEBJUSXlVoKZAOwwO7iOYg7NqItFZBSwRtBPfhUlLXrMZBQdZCx2ZCzaXFXZBM5srZBWwzb3qYfXsCZBrK3InmHt1qYS"

# Initialize WhatsApp API client and onboarding handler
whatsapp_client = WhatsAppAPIClient(ACCESS_TOKEN)
onboarding_handler = WhatsAppOnboardingHandler()

def is_message_event(data: dict) -> bool:
    """
    Check if the webhook event is a message event and not a status event.
    
    Args:
        data (dict): The webhook data
        
    Returns:
        bool: True if it's a message event, False otherwise
    """
    try:
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Check if it's a message event by looking for messages array
        return "messages" in value and "statuses" not in value
    except (IndexError, KeyError):
        return False

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    logger.info(f"Received webhook verification request - Mode: {mode}, Token: {token}")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("WEBHOOK VERIFICADO")
        return challenge, 200
    else:
        logger.warning("Unauthorized webhook verification attempt")
        return "Unauthorized", 403

@app.route('/webhook', methods=['POST'])
async def receive_message():
    data = request.get_json()
    logger.info(f"Mensaje recibido: {data}")

    try:
        # Only process if it's a message event
        if not is_message_event(data):
            logger.info("Ignoring non-message event")
            return "EVENT_RECEIVED", 200

        # Create WhatsApp adapter with the webhook data
        adapter = WhatsAppAdapter(data, whatsapp_client)
        
        # Handle the message with the onboarding handler
        await onboarding_handler.handle_message(data, adapter)
        
    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")

    return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
