import gspread
from oauth2client.service_account import ServiceAccountCredentials
from abc import ABC, abstractmethod
from config import config
import base64
import json
import logging
import re
from typing import Optional, List

logger = logging.getLogger(__name__)

scopes = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

class SpreadsheetManager:
    def __init__(self):
        self.credentials_json = self._load_credentials()
        self.scopes = scopes
        self.client = self._authenticate()

    def _load_credentials(self):
        """Loads and decodes Google credentials from environment config."""
        decoded_bytes = base64.b64decode(config.GOOGLE_CREDENTIALS)
        decoded_string = decoded_bytes.decode('utf-8')
        return json.loads(decoded_string)
        
    def _authenticate(self):
        """Authenticates with Google Sheets API using service account credentials."""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(self.credentials_json, self.scopes)
            client = gspread.authorize(creds)
            logger.info("Successfully connected to Google Sheets API")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets API: {e}")
            raise

    @staticmethod
    def get_sheet_id_from_url(url: str) -> Optional[str]:
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
    
    @staticmethod
    def get_sheet_url(sheet_id: str) -> str:
        """
        Returns the full URL for a Google Sheet.
        
        Args:
            sheet_id: The ID of the spreadsheet
            
        Returns:
            The complete Google Sheets URL
        """
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}"


    def get_spreadsheet_by_id(self, sheet_id: str) -> Optional[gspread.Spreadsheet]:
        """
        Opens a spreadsheet by its ID.
        
        Args:
            sheet_id: The ID of the spreadsheet (from the URL)
            
        Returns:
            The spreadsheet object or None if not found
        """
        try:
            return self.client.open_by_key(sheet_id)
        except gspread.SpreadsheetNotFound:
            logger.error(f"Spreadsheet with ID '{sheet_id}' not found.")
            return None
        except Exception as e:
            logger.error(f"Error opening spreadsheet: {e}")
            return None

    def check_access(self, sheet_id: str) -> bool:
        """
        Checks if the Service Account has access to the given sheet ID by creating
        a temporary worksheet, writing to it, and then deleting it.
        
        Args:
            sheet_id: The ID of the spreadsheet to check
            
        Returns:
            True if access is granted, False otherwise
        """
        try:
            spreadsheet = self.get_spreadsheet_by_id(sheet_id)
            if not spreadsheet:
                return False
            
            # Crear una hoja temporal para prueba
            test_sheet_title = "temp_access_check"
            logger.info(f"Creating temporary worksheet '{test_sheet_title}' for access check")
            
            # Crear nueva hoja
            temp_worksheet = spreadsheet.add_worksheet(test_sheet_title, 1, 1)
            
            # Escribir datos de prueba
            test_row = ["TEST - Checking Access"]
            temp_worksheet.append_row(test_row)
            
            # Eliminar la hoja temporal
            spreadsheet.del_worksheet(temp_worksheet)
            
            logger.info(f"Successfully verified write access to sheet ID: {sheet_id}")
            return True
        except Exception as e:
            logger.error(f"Access check failed for spreadsheet '{sheet_id}': {e}")
            return False

    def insert_row_by_id(self, sheet_id: str, worksheet_name: str, row_data: List[str]) -> bool:
        """
        Inserts a row into a specific worksheet in a spreadsheet identified by ID.
        
        Args:
            sheet_id: The ID of the spreadsheet
            worksheet_name: The name of the worksheet
            row_data: The data to insert as a list
            
        Returns:
            True if successful, False otherwise
        """
        if config.ENVIRONMENT == "TEST":
            return True

        try:
            spreadsheet = self.get_spreadsheet_by_id(sheet_id)
            if not spreadsheet:
                return False

            worksheet = spreadsheet.worksheet(worksheet_name)
            worksheet.append_row(row_data)
            logger.info(f"Row inserted successfully into '{worksheet_name}' of spreadsheet '{sheet_id}'")
            return True
        except gspread.WorksheetNotFound:
            logger.error(f"Worksheet '{worksheet_name}' not found in spreadsheet '{sheet_id}'")
            return False
        except Exception as e:
            logger.error(f"Error inserting row: {e}")
            return False

