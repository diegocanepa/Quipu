from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Any, Dict
from enum import Enum
from core.models.base_model import FinancialModel
from core.models.user import User

class TransactionType(str, Enum):
    """Defines possible transaction types."""
    EXPENSE = "gasto"
    INCOME = "ingreso"

class Transaction(BaseModel, FinancialModel):
    """Represents a financial transaction."""
    description: str = Field(description="Description of the transaction")
    amount: float = Field(description="Amount of the transaction")
    currency: str = Field(description="Currency of the transaction")
    category: str = Field(description="Category of the transaction") # :TODO This could be an Enum. One for income and other for expenses. 
    date: datetime = Field(description="Transaction datetime")
    action: TransactionType = Field(description="Type of transaction (income/expense)")
    
    def to_presentation_string(self) -> str:
        """
        Returns a formatted string representation of the transaction for presentation.
        """
        action_emoji = "💸" if self.action == TransactionType.EXPENSE else "💰"
        return f"""
        <b>{action_emoji} Transacción</b>

        <b>📝 Descripción:</b> {self.description}
        <b>🏷️ Categoría:</b> {self.category}
        <b>➡️ Tipo:</b> {self.action.value}
        <b>🔢 Monto:</b> <code>{self.format_money_data(self.amount)}</code> {self.currency}
        <b>🗓️ Fecha:</b> <code>{self.date.strftime('%d/%m/%Y %H:%M')}</code>
        """

    def to_sheet_row(self) -> List[Any]:
        """
        Returns data formatted for spreadsheet storage.
        This is a pure transformation method.
        """
        return [
            self.date.date().isoformat(),
            self.action.value,
            self.amount,
            self.currency,
            self.category,
            self.description,
        ]
        
    def to_storage_dict(self, user: User) -> Dict[str, Any]:
        """
        Returns data formatted for database storage.
        This is a pure transformation method.
        """
        return {
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "category": self.category,
            "date": self.date.isoformat(),
            "action": self.action.value,
            "webapp_user_id": user.webapp_user_id,
            "telegram_user_id": user.telegram_user_id,
            "whatsapp_user_id": user.whatsapp_user_id,
        }

    def get_base_table_name(self) -> str:
        """Returns the base table name without test prefix."""
        return "transactions"

    def get_worksheet_name(self) -> str:
        """Returns the worksheet name for Google Sheets."""
        return "Gastos&Ingresos" 