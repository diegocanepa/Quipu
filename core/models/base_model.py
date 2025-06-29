import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from core.models.common.source import Source
from core.models.user import User


class FinancialModel(ABC):
    """Base interface for all financial models."""

    def to_presentation_string(self, source: str = Source.TELEGRAM) -> str:
        """
        Returns a formatted string representation for user presentation.

        Args:
            source: The source platform (telegram or whatsapp)

        Returns:
            str: Formatted string for the specified platform
        """
        if source == Source.TELEGRAM:
            return self._to_telegram_presentation()
        elif source == Source.WHATSAPP:
            return self._to_whatsapp_presentation()
        else:
            raise ValueError(f"Unsupported source: {source}")

    @abstractmethod
    def _to_telegram_presentation(self) -> str:
        """
        Returns a formatted string representation for Telegram.
        Uses HTML formatting and emojis.
        """
        pass

    @abstractmethod
    def _to_whatsapp_presentation(self) -> str:
        """
        Returns a formatted string representation for WhatsApp.
        Uses plain text and emojis.
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Returns a description of the financial model.
        This is used for user understanding and documentation.
        """
        pass

    @abstractmethod
    def to_sheet_row(self) -> List[Any]:
        """Returns data formatted for spreadsheet storage."""
        pass

    @abstractmethod
    def to_storage_dict(self, user: User) -> Dict[str, Any]:
        """Returns data formatted for database storage."""
        pass

    @abstractmethod
    def get_base_table_name(self) -> str:
        """Returns the base table name without test prefix."""
        pass

    @abstractmethod
    def get_worksheet_name(self) -> str:
        """Returns the worksheet name for Google Sheets."""
        pass

    def get_table_name(self) -> str:
        """
        Returns the table name for database storage.
        Handles test environment by adding 'test_' prefix.
        """
        base_name = self.get_base_table_name()
        is_test = os.getenv("ENVIRONMENT", "prod").lower() == "test"
        return f"{base_name}_test" if is_test else base_name

    def format_money_data(self, number: float) -> str:
        return f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
