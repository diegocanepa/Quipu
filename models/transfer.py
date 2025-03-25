from pydantic import BaseModel, Field
from datetime import datetime

class Transfer(BaseModel):
    """Represents a financial transaction."""
    description: str = Field(description="Description of the bill")
    category: str = Field(description="Category of the bill")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action")
    wallet_from: str = Field(description="Wallet from")
    wallet_to: str = Field(description="Wallet to")
    initial_amount: float = Field(description="Initial mount of the bill")
    final_amount: float = Field(description="Final mount of the bill with the fees")
    currency: str = Field(description="Currency of the bill")

    def to_formatted_string(self) -> str:
        return (
            f"*Transferencia de Fondos*\n\n"
            f"📝 *Descripción:* {self.escape_markdown(self.description)}\n"
            f"📂 *Categoría:* {self.escape_markdown(self.category)}\n"
            f"➡️ *Acción:* {self.escape_markdown(self.action)}\n"
            f"🏦 *Desde:* {self.escape_markdown(self.wallet_from)}\n"
            f"➡️ *Hacia:* {self.escape_markdown(self.wallet_to)}\n"
            f"📤 *Monto Inicial:* `{self.initial_amount:.2f}` {self.escape_markdown(self.currency)}\n"
            f"📥 *Monto Final:* `{self.final_amount:.2f}` {self.escape_markdown(self.currency)}\n"
            f"➖ *Comisión:* `{self.initial_amount - self.final_amount:.2f}` {self.escape_markdown(self.currency)}\n"
            f"🗓️ *Fecha:* `{self.date.strftime('%Y-%m-%d %H:%M')}`"
        )
        
    def escape_markdown(self, text: str) -> str:
        """Escapa caracteres especiales de MarkdownV2."""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in str(text))
