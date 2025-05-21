from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from core.models.base_model import FinancialModel
from core.models.user import User

class Transfer(BaseModel, FinancialModel):
    """Represents a transfer operation."""
    description: str = Field(description="Description of the transfer")
    category: str = Field(description="Category of the transfer")
    date: datetime = Field(description="Operation datetime")
    action: str = Field(description="Action type")
    wallet_from: str = Field(description="Source wallet")
    wallet_to: Optional[str] = Field(default=None, description="Target wallet")
    initial_amount: float = Field(description="Initial amount before fees")
    final_amount: float = Field(description="Final amount after fees")
    currency: str = Field(description="Currency of the operation")

    def to_presentation_string(self) -> str:
        """Returns a formatted string representation for user presentation."""
        wallet_to_str = self._escape_markdown(self.wallet_to) if self.wallet_to is not None else "N/A"
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

    def to_sheet_row(self) -> List[Any]:
        """Returns data formatted for spreadsheet storage."""
        return [
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
        
    def to_storage_dict(self, user: User) -> Dict[str, Any]:
        """Returns data formatted for database storage."""
        return {
            "description": self.description,
            "category": self.category,
            "date": self.date.isoformat(),
            "action": self.action,
            "wallet_from": self.wallet_from,
            "wallet_to": self.wallet_to,
            "initial_amount": self.initial_amount,
            "final_amount": self.final_amount,
            "currency": self.currency,
            "webapp_user_id": user.webapp_user_id,
            "telegram_user_id": user.telegram_user_id,
            "whatsapp_user_id": user.whatsapp_user_id,
        }

    def get_base_table_name(self) -> str:
        """Returns the base table name without test prefix."""
        return "transfers"

    def get_worksheet_name(self) -> str:
        """Returns the worksheet name for Google Sheets."""
        return "Transferencias" 