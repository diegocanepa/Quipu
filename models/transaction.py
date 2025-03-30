from pydantic import BaseModel, Field
from datetime import datetime
from integrations.spreadsheet.spreadsheet import GoogleSheetsClient
from integrations.supabase.supabase import SupabaseManager

class Transaction(BaseModel):
    """Represents a financial bill."""
    description: str = Field(description="Description of the bill")
    amount: float = Field(description="Amount of the bill")
    currency: str = Field(description="Currency of the bill")
    category: str = Field(description="Category of the bill")
    date: datetime = Field(description="Actual Datetime")
    action: str = Field(description="Action (Ingreso or Gasto)")
    
    def to_formatted_string(self) -> str:
        action_emoji = "💸" if self.action.lower() == "expense" else "💰"
        return (
            f"*Transacción* {action_emoji}\n\n"
            f"📝 *Descripción:* {self._escape_markdown(self.description)}\n"
            f"🏷️ *Categoría:* {self._escape_markdown(self.category)}\n"
            f"➡️ *Tipo:* {self._escape_markdown(self.action)}\n"
            f"🔢 *Monto:* `{self.amount:.2f}` {self._escape_markdown(self.currency)}\n"
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
            self.currency,
            self.category,
            self.description,
        ]
        service.insert_row("FinMate", "Gastos&Ingresos", row)
        
    async def save_to_database(self, service: SupabaseManager):
        data = {
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "category": self.category,
            "date": self.date.date().isoformat(),
            "action": self.action,
        }
        await service.insert("transactions", data)