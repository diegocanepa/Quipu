from pydantic import BaseModel, Field
from datetime import datetime

class Transaction(BaseModel):
    """Represents a financial bill."""
    description: str = Field(description="Description of the bill")
    amount: float = Field(description="Amount of the bill")
    currency: str = Field(description="Currency of the bill")
    category: str = Field(description="Category of the bill")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action (expense or income)")
    
    def to_formatted_string(self) -> str:
        action_emoji = "💸" if self.action.lower() == "expense" else "💰"
        return (
            f"*Transacción* {action_emoji}\n\n"
            f"📝 *Descripción:* {self.escape_markdown(self.description)}\n"
            f"🏷️ *Categoría:* {self.escape_markdown(self.category)}\n"
            f"➡️ *Tipo:* {self.escape_markdown(self.action)}\n"
            f"🔢 *Monto:* `{self.amount:.2f}` {self.escape_markdown(self.currency)}\n"
            f"🗓️ *Fecha:* `{self.date.strftime('%Y-%m-%d %H:%M')}`"
        )
        
    def escape_markdown(self, text: str) -> str:
        """Escapa caracteres especiales de MarkdownV2."""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in str(text))
