from pydantic import BaseModel, Field
from datetime import datetime
from integrations.spreedsheet.spreedsheet import GoogleSheetsClient

class Forex(BaseModel):
    """Represents a financial bill."""
    description: str = Field(description="Description of the bill")
    amount: float = Field(description="Amount of the bill")
    currency_from: str = Field(description="Currency of the bill")
    currency_to: str = Field(description="Currency of the bill")
    price: float = Field(description="Price of change")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action")
    
    def to_formatted_string(self) -> str:
        return (
            f"*Operación Cambio de Divisas*\n\n"
            f"📝 *Descripción:* {self._escape_markdown(self.description)}\n"
            f"🔄 *Acción:* {self._escape_markdown(self.action)}\n"
            f"📤 *Cantidad Enviada:* `{self.amount:.2f}` {self._escape_markdown(self.currency_from)}\n"
            f"📥 *Cantidad Recibida:* `{self.amount * self.price:.2f}` {self._escape_markdown(self.currency_to)}\n"
            f"💰 *Precio de Cambio:* `{self.price:.4f}` {self._escape_markdown(f'{self.currency_from}/{self.currency_to}')}\n"
            f"🗓️ *Fecha:* `{self.date.strftime('%Y-%m-%d %H:%M')}`"
        )
        
    def _escape_markdown(self, text: str) -> str:
        """Escapa caracteres especiales de MarkdownV2."""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in str(text))
    
    def save_to_sheet(self, service: GoogleSheetsClient):
        row = [
            self.date.date().isoformat(),
            self.action,
            self.amount,
            self.currency_from,
            self.currency_to,
            self.price,
            self.price * self.amount,
            self.description
        ]
        print(f"row: {row}")
        service.insert_row("FinMate", "CambioDeDivisas", row)
