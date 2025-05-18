import logging
from typing import Union

from integrations.spreadsheet.spreadsheet import GoogleSheetsClient as GSheetsClient
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
        self.spreadsheet_client = GSheetsClient()
        self.supabase_client = SupaManager()
        logger.info("DataSaver initialized.")

    def save_content(self, data: Union[Forex, Investment, Transaction, Transfer]) -> bool:
        """
        Saves the processed data to the Google Sheets spreadsheet and the
        Supabase database.

        Args:
            data: The processed financial data object.

        Returns:
            True if saving to both was successful, False otherwise.
        """
        success_spreadsheet = self._save_to_spreadsheet(data)
        success_database = self._save_to_database(data)
        return success_spreadsheet and success_database

    def _save_to_spreadsheet(self, data: Union[Forex, Investment, Transaction, Transfer]) -> bool:
        """
        Saves the processed data to the Google Sheets spreadsheet.

        Args:
            data: The processed financial data object.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            logger.info(f"Saving data to spreadsheet: '{data.__class__.__name__}'")
            data.save_to_sheet(self.spreadsheet_client)
            logger.info("Successfully saved to spreadsheet.")
            return True
        except Exception as e:
            logger.error(f"Error saving data to spreadsheet: '{e}'", exc_info=True)
            return False

    def _save_to_database(self, data: Union[Forex, Investment, Transaction, Transfer]) -> bool:
        """
        Saves the processed data to the Supabase database.

        Args:
            data: The processed financial data object.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            logger.info(f"Saving data to database: '{data.__class__.__name__}'")
            data.save_to_database(self.supabase_client)
            logger.info("Successfully saved to database.")
            return True
        except Exception as e:
            logger.error(f"Error saving data to database: '{e}'", exc_info=True)
            return False