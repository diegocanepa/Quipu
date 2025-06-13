from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class WhatsAppContact:
    """Minimal contact information needed for WhatsApp messages."""
    name: str
    wa_id: str

@dataclass
class WhatsAppMetadata:
    """Metadata needed for sending messages."""
    phone_number_id: str

@dataclass
class WhatsAppText:
    """Text message content."""
    body: str

@dataclass
class WhatsAppButtonReply:
    """Button reply information."""
    id: str
    title: str

@dataclass
class WhatsAppInteractive:
    """Interactive message (button) information."""
    type: str
    button_reply: WhatsAppButtonReply

@dataclass
class WhatsAppMessage:
    """Core message information needed for processing."""
    from_number: str
    message_id: str
    text: Optional[WhatsAppText]
    type: str
    interactive: Optional[WhatsAppInteractive] = None

    def is_text_message(self) -> bool:
        """Check if this is a text message."""
        return self.type == "text" and self.text is not None

    def is_button_reply(self) -> bool:
        """Check if this is a button reply message."""
        return self.type == "interactive" and self.interactive is not None and self.interactive.type == "button_reply"

    def get_button_id(self) -> Optional[str]:
        """Get the button ID if this is a button reply."""
        if self.is_button_reply():
            return self.interactive.button_reply.id
        return None

    def get_button_title(self) -> Optional[str]:
        """Get the button title if this is a button reply."""
        if self.is_button_reply():
            return self.interactive.button_reply.title
        return None

@dataclass
class WhatsAppWebhook:
    """Simplified webhook structure containing only necessary data."""
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
            # Handle text messages
            text_data = msg.get("text", {})
            text_obj = WhatsAppText(body=text_data.get("body", "")) if text_data else None
            
            # Handle interactive messages (button replies)
            interactive_data = msg.get("interactive", {})
            interactive_obj = None
            if interactive_data:
                button_reply = interactive_data.get("button_reply", {})
                if button_reply:
                    interactive_obj = WhatsAppInteractive(
                        type=interactive_data.get("type", ""),
                        button_reply=WhatsAppButtonReply(
                            id=button_reply.get("id", ""),
                            title=button_reply.get("title", "")
                        )
                    )
            
            messages.append(WhatsAppMessage(
                from_number=msg.get("from", ""),
                message_id=msg.get("id", ""),
                text=text_obj,
                type=msg.get("type", ""),
                interactive=interactive_obj
            ))
        
        return cls(
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