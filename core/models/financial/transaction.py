from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Any, Dict
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
    category: str = Field(description="Category of the transaction")
    date: datetime = Field(description="Transaction datetime")
    action: TransactionType = Field(description="Type of transaction (income/expense)")
    
    def to_presentation_string(self) -> str:
        """
        Returns a formatted string representation for user presentation.
        This is a pure domain method that doesn't depend on external services.
        """
        action_emoji = "💸" if self.action == TransactionType.EXPENSE else "💰"
        return (
            f"*Transacción* {action_emoji}\n\n"
            f"📝 *Descripción:* {self._escape_markdown(self.description)}\n"
            f"🏷️ *Categoría:* {self._escape_markdown(self.category)}\n"
            f"➡️ *Tipo:* {self._escape_markdown(self.action.value)}\n"
            f"🔢 *Monto:* `{self.amount:.2f}` {self._escape_markdown(self.currency)}\n"
            f"🗓️ *Fecha:* `{self.date.strftime('%Y-%m-%d %H:%M')}`"
        )

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
            "action": self.action,
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