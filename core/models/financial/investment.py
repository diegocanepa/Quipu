from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum
from core.models.base_model import FinancialModel
from core.models.user import User
from core.models.common.source import Source

class InvestmentAction(str, Enum):
    """Defines possible investment actions."""
    BUY = "compra"
    SELL = "venta"

class Investment(BaseModel, FinancialModel):
    """Represents an investment operation."""
    description: str = Field(description="Description of the investment")
    category: str = Field(description="Category of the investment")
    date: datetime = Field(description="Operation datetime")
    action: InvestmentAction = Field(description="Action (buy or sell)")
    platform: str = Field(description="Platform where the investment was done")
    amount: float = Field(description="Amount of the investment")
    price: float = Field(description="Price of the investment tool")
    currency: str = Field(description="Currency of the operation")
    
    def _to_telegram_presentation(self) -> str:
        """
        Returns a formatted string representation for Telegram.
        Uses HTML formatting and emojis.
        """
        action_emoji = "📈" if self.action == InvestmentAction.BUY else "📉"
        return f"""
            <b>{action_emoji} Inversión</b>
            <b>📝 Descripción:</b> {self.description}
            <b>🏷️ Categoría:</b> {self.category}
            <b>➡️ Acción:</b> {self.action.value}
            <b>🏢 Plataforma:</b> {self.platform}
            <b>🔢 Cantidad:</b> <code>{self.format_money_data(self.amount)}</code>
            <b>💲 Precio por Unidad:</b> <code>{self.format_money_data(self.price)}</code> {self.currency}
            <b>💸 Monto Total:</b> <code>{self.format_money_data(self.amount * self.price)}</code> {self.currency}
            <b>🗓️ Fecha:</b> <code>{self.date.strftime('%d/%m/%Y %H:%M')}</code>
        """

    def _to_whatsapp_presentation(self) -> str:
        """
        Returns a formatted string representation for WhatsApp.
        Uses plain text and emojis.
        """
        action_emoji = "📈" if self.action == InvestmentAction.BUY else "📉"
        return f"""{action_emoji} *Inversión*

        📝 *Descripción:* {self.description}
        🏷️ *Categoría:* {self.category}
        ➡️ *Acción:* {self.action.value}
        🏢 *Plataforma:* {self.platform}
        🔢 *Cantidad:* {self.format_money_data(self.amount)}
        💲 *Precio por Unidad:* {self.format_money_data(self.price)} {self.currency}
        💸 *Monto Total:* {self.format_money_data(self.amount * self.price)} {self.currency}
        🗓️ *Fecha:* {self.date.strftime('%d/%m/%Y %H:%M')}"""

    def to_sheet_row(self) -> List[Any]:
        """Returns data formatted for spreadsheet storage."""
        return [
            self.date.date().isoformat(),
            self.action.value,
            self.category,
            self.platform,
            self.amount,
            self.price,
            self.currency,
            self.description,
        ]
        
    def to_storage_dict(self, user: User) -> Dict[str, Any]:
        """Returns data formatted for database storage."""
        return {
            "description": self.description,
            "category": self.category,
            "date": self.date.isoformat(),
            "action": self.action.value,
            "platform": self.platform,
            "amount": self.amount,
            "price": self.price,
            "currency": self.currency,
            "webapp_user_id": user.id,
        }

    def get_base_table_name(self) -> str:
        """Returns the base table name without test prefix."""
        return "investments"

    def get_worksheet_name(self) -> str:
        """Returns the worksheet name for Google Sheets."""
        return "Inversiones" 