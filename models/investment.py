from pydantic import BaseModel, Field
from datetime import datetime

class Investment(BaseModel):
    """Represents a financial transaction."""
    description: str = Field(description="Description of the investment")
    category: str = Field(description="Category of the investment")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action (sell or buy)")
    platform: str = Field(description="Platform where the investment was done")
    amout: float = Field(description="amount of the investment")
    price: float = Field(description="Price of the investment tool")
    currency: str = Field(description="Currency of the bill")
    
    def to_formatted_string(self) -> str:
        action_emoji = "📈" if self.action.lower() == "buy" else "📉"
        return (
            f"*Operación de Inversión* {action_emoji}\n\n"
            f"📝 *Descripción:* {self.escape_markdown(self.description)}\n"
            f"📂 *Categoría:* {self.escape_markdown(self.category)}\n"
            f"➡️ *Acción:* {self.escape_markdown(self.action)}\n"
            f"🏢 *Plataforma:* {self.escape_markdown(self.platform)}\n"
            f"🔢 *Cantidad:* `{self.amout:.4f}`\n"
            f"💲 *Precio por Unidad:* `{self.price:.4f}` {self.escape_markdown(self.currency)}\n"
            f"💸 *Monto Total:* `{self.amout * self.price:.2f}` {self.escape_markdown(self.currency)}\n"
            f"🗓️ *Fecha:* `{self.date.strftime('%Y-%m-%d %H:%M')}`"
        )
        
    def escape_markdown(self, text: str) -> str:
        """Escapa caracteres especiales de MarkdownV2."""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in str(text))
