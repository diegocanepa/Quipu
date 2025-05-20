import logging
from typing import Union

from core.models.user import User
from core.models.base_model import FinancialModel
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from integrations.supabase.supabase import SupabaseManager as SupaManager

logger = logging.getLogger(__name__)

class DataSaver:
    """
    Handles the saving of processed financial data to spreadsheet and database.
    Acts as a facade for all data persistence operations.
    """

    def __init__(self):
        """
        Initializes the DataSaver with instances of the spreadsheet and
        database clients. Logs the initialization.
        """
        self.spreadsheet_client = SpreadsheetManager()
        self.supabase_client = SupaManager()
        logger.info("DataSaver initialized.")

    def save_content(self, data: FinancialModel, user: User) -> bool:
        """
        Saves the processed data to all configured storage methods for the user.
        Acts as a facade that coordinates saving to different storage systems based on user configuration.

        Args:
            data: The processed financial data object (must implement FinancialModel interface).
            user: The user who owns this data.

        Returns:
            True if saving to all configured storage methods was successful, False otherwise.
        """
        success = True
        
        # Save to spreadsheet if user has it configured
        if user.is_sheet_linked:
            success = success and self._save_to_spreadsheet(data, user)

        # Save to database if user has webapp configured
        if user.is_webapp_linked:
            success = success and self._save_to_database(data, user)

        return success

    def _save_to_spreadsheet(self, data: FinancialModel, user: User) -> bool:
        """
        Saves the processed data to the Google Sheets spreadsheet.

        Args:
            data: The financial data object (must implement FinancialModel interface).
            user: The user who owns this data.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            logger.info(f"Saving {data.__class__.__name__} to spreadsheet for user {user.id}")
            return self.spreadsheet_client.insert_row_by_id(
                user.google_sheet_id,
                data.get_worksheet_name(),
                data.to_sheet_row()
            )
        except Exception as e:
            logger.error(f"Error saving {data.__class__.__name__} to spreadsheet: {e}", exc_info=True)
            return False

    def _save_to_database(self, data: FinancialModel, user: User) -> bool:
        """
        Saves the processed data to the Supabase database.

        Args:
            data: The financial data object (must implement FinancialModel interface).
            user: The user who owns this data.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            logger.info(f"Saving {data.__class__.__name__} to database for user {user.id}")
            table_name = data.get_table_name()
            return self.supabase_client.insert(table_name, data.to_storage_dict(user))
        except Exception as e:
            logger.error(f"Error saving {data.__class__.__name__} to database: {e}", exc_info=True)
            return False