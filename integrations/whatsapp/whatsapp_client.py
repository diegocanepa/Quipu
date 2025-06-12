import requests
import logging
from config import config

logger = logging.getLogger(__name__)

class WhatsAppAPIClient:
    def __init__(self):
        self.access_token = config.WHATSAPP_ACCESS_TOKEN
        self.base_url = "https://graph.facebook.com/v18.0"

    def send_message(self, phone_number_id: str, to: str, message: str):
        """
        Sends a text message to a WhatsApp user.

        Args:
            phone_number_id (str): The phone number ID from WhatsApp Business API
            to (str): The recipient's phone number
            message (str): The message to send
        """
        url = f"{self.base_url}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": self._sanitize_number(to),
            "text": {"body": message}
        }

        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Message send response: {response.status_code} - {response.text}")
        return response

    def send_interactive_message(self, phone_number_id: str, to: str, body_text: str, buttons: list):
        """
        Sends an interactive message with buttons to a WhatsApp user.

        Args:
            phone_number_id (str): The phone number ID from WhatsApp Business API
            to (str): The recipient's phone number
            body_text (str): The main text of the message
            buttons (list): List of button dictionaries with 'id' and 'title'
        """
        url = f"{self.base_url}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Format buttons for WhatsApp API
        formatted_buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": button.get("id", f"btn_{i}"),
                    "title": button.get("title", button.get("text", f"Button {i+1}"))
                }
            }
            for i, button in enumerate(buttons)
        ]

        payload = {
            "messaging_product": "whatsapp",
            "to": self._sanitize_number(to),
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": formatted_buttons
                }
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        logger.info(f"Interactive message send response: {response.status_code} - {response.text}")
        return response

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
    
    
whatsapp_api_client = WhatsAppAPIClient()