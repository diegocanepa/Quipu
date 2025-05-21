from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any
from core.models.base_model import FinancialModel
from core.models.user import User

class Forex(BaseModel, FinancialModel):
    """Represents a forex operation."""
    description: str = Field(description="Description of the operation")
    amount: float = Field(description="Amount to exchange")
    currency_from: str = Field(description="Source currency")
    currency_to: str = Field(description="Target currency")
    price: float = Field(description="Exchange rate")
    date: datetime = Field(description="Operation datetime")
    action: str = Field(description="Action type")
    
    def to_presentation_string(self) -> str:
        """Returns a formatted string representation for user presentation."""
        return (
            f"*Operación Cambio de Divisas*\n\n"
            f"📝 *Descripción:* {self._escape_markdown(self.description)}\n"
            f"🔄 *Acción:* {self._escape_markdown(self.action)}\n"
            f"📤 *Cantidad Enviada:* `{self.amount:.2f}` {self._escape_markdown(self.currency_from)}\n"
            f"📥 *Cantidad Recibida:* `{self.amount * self.price:.2f}` {self._escape_markdown(self.currency_to)}\n"
            f"💰 *Precio de Cambio:* `{self.price:.4f}` {self._escape_markdown(f'{self.currency_from}/{self.currency_to}')}\n"
            f"🗓️ *Fecha:* `{self.date.strftime('%Y-%m-%d %H:%M')}`"
        )

    def to_sheet_row(self) -> List[Any]:
        """Returns data formatted for spreadsheet storage."""
        return [
            self.date.date().isoformat(),
            self.action,
            self.amount,
            self.currency_from,
            self.currency_to,
            self.price,
            self.price * self.amount,
            self.description
        ]
        
    def to_storage_dict(self, user: User) -> Dict[str, Any]:
        """Returns data formatted for database storage."""
        return {
            "description": self.description,
            "amount": self.amount,
            "currency_from": self.currency_from,
            "currency_to": self.currency_to,
            "price": self.price,
            "date": self.date.isoformat(),
            "action": self.action,
            "webapp_user_id": user.webapp_user_id,
            "telegram_user_id": user.telegram_user_id,
            "whatsapp_user_id": user.whatsapp_user_id,
        }

    def get_base_table_name(self) -> str:
        """Returns the base table name without test prefix."""
        return "forex"

    def get_worksheet_name(self) -> str:
        """Returns the worksheet name for Google Sheets."""
        return "CambioDeDivisas" 