from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum
from core.models.base_model import FinancialModel
from core.models.user import User

class TransactionType(str, Enum):
    """Defines possible transaction types."""
    EXPENSE = "gasto"
    INCOME = "ingreso"

class Transaction(BaseModel, FinancialModel):
    """Represents a financial transaction."""
    amount: float = Field(description="Transaction amount")
    currency: str = Field(description="Transaction currency")
    description: str = Field(description="Transaction description")
    date: datetime = Field(description="Transaction datetime")
    category: str = Field(description="Transaction category") # :TODO This could be an Enum. One for income and other for expenses. 
    action: TransactionType = Field(description="Transaction action (income/expense)")
    
    def _to_telegram_presentation(self) -> str:
        """
        Returns a formatted string representation for Telegram.
        Uses HTML formatting and emojis.
        """
        emoji = "📥" if self.action == TransactionType.INCOME else "📤"
        return f"""
            <b>{emoji} {'Ingreso' if self.action == TransactionType.INCOME else 'Gasto'}</b>
            
        <b>📝 Descripción:</b> {self.description}
        <b>💰 Monto:</b> <code>{self.format_money_data(self.amount)}</code> {self.currency}
        <b>🏷️ Categoría:</b> {self.category}
        <b>🗓️ Fecha:</b> <code>{self.date.strftime('%d/%m/%Y %H:%M')}</code>
        """

    def _to_whatsapp_presentation(self) -> str:
        """
        Returns a formatted string representation for WhatsApp.
        Uses plain text and emojis.
        """
        emoji = "📥" if self.action == TransactionType.INCOME else "📤"
        return f"""{emoji} *{'Ingreso' if self.action == TransactionType.INCOME else 'Gasto'}*

        📝 *Descripción:* {self.description}
        💰 *Monto:* {self.format_money_data(self.amount)} {self.currency}
        🏷️ *Categoría:* {self.category}
        🗓️ *Fecha:* {self.date.strftime('%d/%m/%Y %H:%M')}"""

    def to_sheet_row(self) -> List[Any]:
        """Returns data formatted for spreadsheet storage."""
        return [
            self.date.date().isoformat(),
            self.action.value,
            self.amount,
            self.currency,
            self.category,
            self.description
        ]
        
    def to_storage_dict(self, user: User) -> Dict[str, Any]:
        """Returns data formatted for database storage."""
        return {
            "amount": self.amount,
            "currency": self.currency,
            "description": self.description,
            "date": self.date.isoformat(),
            "category": self.category,
            "action": self.action.value,
            "webapp_user_id": str(user.id) if user.id else None
        }

    def get_base_table_name(self) -> str:
        """Returns the base table name without test prefix."""
        return "transactions"

    def get_worksheet_name(self) -> str:
        """Returns the worksheet name for Google Sheets."""
        return "Gastos&Ingresos" 