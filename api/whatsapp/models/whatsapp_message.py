from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class WhatsAppContact:
    name: str
    wa_id: str

@dataclass
class WhatsAppMetadata:
    display_phone_number: str
    phone_number_id: str

@dataclass
class WhatsAppText:
    body: str

@dataclass
class WhatsAppMessage:
    from_number: str
    message_id: str
    timestamp: str
    text: Optional[WhatsAppText]
    type: str

@dataclass
class WhatsAppWebhook:
    object: str
    entry_id: str
    metadata: WhatsAppMetadata
    contacts: List[WhatsAppContact]
    messages: List[WhatsAppMessage]

    @classmethod
    def from_json(cls, data: Dict) -> 'WhatsAppWebhook':
        """
        Creates a WhatsAppWebhook instance from the webhook JSON data.
        
        Args:
            data: The raw webhook data from WhatsApp
            
        Returns:
            WhatsAppWebhook: A structured representation of the webhook data
        """
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Extract metadata
        metadata = value.get("metadata", {})
        metadata_obj = WhatsAppMetadata(
            display_phone_number=metadata.get("display_phone_number", ""),
            phone_number_id=metadata.get("phone_number_id", "")
        )
        
        # Extract contacts
        contacts = []
        for contact in value.get("contacts", []):
            profile = contact.get("profile", {})
            contacts.append(WhatsAppContact(
                name=profile.get("name", ""),
                wa_id=contact.get("wa_id", "")
            ))
        
        # Extract messages
        messages = []
        for msg in value.get("messages", []):
            text_data = msg.get("text", {})
            messages.append(WhatsAppMessage(
                from_number=msg.get("from", ""),
                message_id=msg.get("id", ""),
                timestamp=msg.get("timestamp", ""),
                text=WhatsAppText(body=text_data.get("body", "")) if text_data else None,
                type=msg.get("type", "")
            ))
        
        return cls(
            object=data.get("object", ""),
            entry_id=entry.get("id", ""),
            metadata=metadata_obj,
            contacts=contacts,
            messages=messages
        )
        
    def is_message_event(self) -> bool:
        """
        Check if this webhook event is a message event and not a status event.
        
        Returns:
            bool: True if it's a message event, False otherwise
        """
        return len(self.messages) > 0 