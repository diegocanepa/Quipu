from pydantic import BaseModel, Field
from datetime import datetime
from integrations.spreadsheet.spreadsheet import GoogleSheetsClient
from integrations.supabase.supabase import SupabaseManager

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
        wallet_to_str = self._escape_markdown(self.wallet_to) if self.wallet_to is not None else ""
        lines = [
            "*Transferencia de Fondos*\n",
            f"📝 *Descripción:* {self._escape_markdown(self.description)}",
            f"📂 *Categoría:* {self._escape_markdown(self.category)}",
            f"➡️ *Acción:* {self._escape_markdown(self.action)}",
            f"🏦 *Desde:* {self._escape_markdown(self.wallet_from)}",
            f"➡️ *Hacia:* {wallet_to_str}",
            f"📤 *Monto Inicial:* `{self.initial_amount:.2f}` {self._escape_markdown(self.currency)}",
            f"📥 *Monto Final:* `{self.final_amount:.2f}` {self._escape_markdown(self.currency)}",
        ]

        if self.final_amount != 0:
            commission = self.initial_amount - self.final_amount
            lines.append(f"➖ *Comisión:* `{commission:.2f}` {self._escape_markdown(self.currency)}")

        lines.append(f"🗓️ *Fecha:* `{self.date.strftime('%Y-%m-%d %H:%M')}`")

        return "\n".join(lines)

            
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
        
    async def save_to_database(self, service: SupabaseManager):
        data = {
            "description": self.description,
            "category": self.category,
            "date": self.date.date().isoformat(),
            "action": self.action,
            "wallet_from": self.wallet_from,
            "wallet_to": self.wallet_to,
            "initial_amount": self.initial_amount,
            "final_amount": self.final_amount,
            "currency": self.currency,
        }
        await service.insert("transfers", data)