from abc import ABC, abstractmethod
from typing import Any, List, Dict
import os

from core.models.user import User

class FinancialModel(ABC):
    """Base interface for all financial models."""
    
    @abstractmethod
    def to_presentation_string(self) -> str:
        """Returns a formatted string representation for user presentation."""
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
        is_test = os.getenv('ENVIRONMENT', 'prod').lower() == 'test'
        return f"{base_name}_test" if is_test else base_name

    def _escape_markdown(self, text: str) -> str:
        """Escapes special characters for MarkdownV2."""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join('\\' + char if char in escape_chars else char for char in str(text)) 