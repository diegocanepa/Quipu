import logging
from typing import Union

from core.models.user import User
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from integrations.supabase.supabase import SupabaseManager as SupaManager
from models.forex import Forex
from models.investment import Investment
from models.transaction import Transaction
from models.transfer import Transfer

logger = logging.getLogger(__name__)

class DataSaver:
    """
    Handles the saving of processed financial data to spreadsheet and database.
    """

    def __init__(self):
        """
        Initializes the DataSaver with instances of the spreadsheet and
        database clients. Logs the initialization.
        """
        self.spreadsheet_client = SpreadsheetManager()
        self.supabase_client = SupaManager()
        logger.info("DataSaver initialized.")

    def save_content(self, data: Union[Forex, Investment, Transaction, Transfer], user: User) -> bool:
        """
        Saves the processed data to the Google Sheets spreadsheet and the
        Supabase database.

        Args:
            data: The processed financial data object.

        Returns:
            True if saving to both was successful, False otherwise.
        """
        success_spreadsheet = True
        success_database = True
        
        if user.is_sheet_linked:
            success_spreadsheet = self._save_to_spreadsheet(data, user)

        if user.is_webapp_linked:
            success_database = self._save_to_database(data, user)

        return success_spreadsheet and success_database

    def _save_to_spreadsheet(self, data: Union[Forex, Investment, Transaction, Transfer], user: User) -> bool:
        """
        Saves the processed data to the Google Sheets spreadsheet.

        Args:
            data: The processed financial data object.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            logger.info(f"Saving data to spreadsheet: '{data.__class__.__name__}' from user {user.id}")
            return data.save_to_sheet(self.spreadsheet_client, user)
        except Exception as e:
            logger.error(f"Error saving data to spreadsheet: '{e}'", exc_info=True)
            return False

    def _save_to_database(self, data: Union[Forex, Investment, Transaction, Transfer], user: User) -> bool:
        """
        Saves the processed data to the Supabase database.

        Args:
            data: The processed financial data object.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            logger.info(f"Saving data to database: '{data.__class__.__name__}' from user {user.id}")
            return data.save_to_database(self.supabase_client, user)
        except Exception as e:
            logger.error(f"Error saving data to database: '{e}'", exc_info=True)
            return False