# google_sheet_linker.py
import gspread # Using gspread for simplicity over raw google-api-python-client
from google.oauth2.service_account import Credentials
import re
import logging
from config import config
import os
from typing import Optional

from integrations.spreadsheet.spreadsheet import GoogleSheetsClient

logger = logging.getLogger(__name__)

class GoogleSheetLinker:
    def __init__(self):
        self._client = GoogleSheetsClient()

    @staticmethod
    def get_sheet_id_from_url(url: str) -> str | None:
        """
        Extracts the sheet ID from a Google Sheet URL.

        Args:
            url: The full Google Sheet URL.

        Returns:
            The extracted sheet ID string or None if the URL format is invalid.
        """
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
        if match:
            sheet_id = match.group(1)
            logger.debug(f"Extracted sheet ID '{sheet_id}' from URL: {url}")
            return sheet_id
        logger.warning(f"Could not extract sheet ID from URL: {url}")
        return None

    def check_sheet_access(self, sheet_id: str) -> bool:
        """
        Checks if the Service Account has access to the given sheet ID by creating
        a temporary worksheet, writing to it, and then deleting it.

        Args:
            sheet_id: The ID of the Google Sheet.

        Returns:
            True if access is confirmed, False otherwise.
        """
        try:
            # Try to open the sheet by ID using the underlying gspread client
            spreadsheet = self._client.client.open_by_key(sheet_id)
            
            # Crear una hoja temporal para prueba
            test_sheet_title = "temp_access_check"
            logger.info(f"Creating temporary worksheet '{test_sheet_title}' for access check")
            
            # Crear nueva hoja
            temp_worksheet = spreadsheet.add_worksheet(test_sheet_title, 1, 1)
            
            # Escribir datos de prueba usando el cliente
            test_row = ["TEST - Checking Access"]
            temp_worksheet.append_row(test_row)
            
            # Eliminar la hoja temporal
            spreadsheet.del_worksheet(temp_worksheet)
            
            logger.info(f"Successfully verified write access to sheet ID: {sheet_id}")
            return True

        except gspread.exceptions.APIError as e:
            logger.error(f"API Error checking access to sheet ID '{sheet_id}': {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking access to sheet ID '{sheet_id}': {e}")
            return False

    def get_sheet_url(self, sheet_id: str) -> str:
        """
        Returns the full URL for a Google Sheet.
        """
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}"