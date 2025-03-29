from pydantic import BaseModel, Field
from datetime import datetime
from integrations.spreadsheet.spreadsheet import GoogleSheetsClient

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
            f"📝 *Descripción:* {self._escape_markdown(self.description)}\n"
            f"📂 *Categoría:* {self._escape_markdown(self.category)}\n"
            f"➡️ *Acción:* {self._escape_markdown(self.action)}\n"
            f"🏦 *Desde:* {self._escape_markdown(self.wallet_from)}\n"
            f"➡️ *Hacia:* {self._escape_markdown(self.wallet_to)}\n"
            f"📤 *Monto Inicial:* `{self.initial_amount:.2f}` {self._escape_markdown(self.currency)}\n"
            f"📥 *Monto Final:* `{self.final_amount:.2f}` {self._escape_markdown(self.currency)}\n"
            f"➖ *Comisión:* `{self.initial_amount - self.final_amount:.2f}` {self._escape_markdown(self.currency)}\n"
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
            self.category,
            self.wallet_from,
            self.wallet_to,
            self.initial_amount,
            self.final_amount,
            self.currency,
            self.description,
        ]
        service.insert_row("FinMate", "Transferencias", row)