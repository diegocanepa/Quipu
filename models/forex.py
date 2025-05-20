from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from core.models.user import User
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from integrations.supabase.supabase import SupabaseManager

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
    
    def save_to_sheet(self, service: SpreadsheetManager, user: User) -> bool:
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
        return service.insert_row_by_id(user.google_sheet_id, "CambioDeDivisas", row)
        
    def save_to_database(self, service: SupabaseManager, user: User) -> bool:
        table_name = service.get_table_name("forex")
        data = {
            "webapp_user_id": user.webapp_user_id,
            "telegram_user_id": user.telegram_user_id,
            "whatsapp_user_id": user.whatsapp_user_id,
            "description": self.description,
            "amount": self.amount,
            "currency_from": self.currency_from,
            "currency_to": self.currency_to,
            "price": self.price,
            "date": self.date.isoformat(),
            "action": self.action,
         }
        return service.insert(table_name, data)
        
