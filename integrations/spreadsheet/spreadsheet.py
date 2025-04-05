import gspread
from oauth2client.service_account import ServiceAccountCredentials
from abc import ABC, abstractmethod
from config import config
import base64
import json
import logging

logger = logging.getLogger(__name__)

scopes = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

# --- Google Sheets Service Interface ---
class GoogleSheetsService(ABC):
    @abstractmethod
    def insert_row(self, spreadsheet_name: str, sheet_name: str, row_data: list):
        pass

# --- Google Sheets Service Implementation ---
class GoogleSheetsClient(GoogleSheetsService):
    def __init__(self):
        self.credentials_json = self._load_credentials()
        self.scopes = scopes
        self.client = self._authenticate()

    def _load_credentials(self):
        decoded_bytes = base64.b64decode(config.GOOGLE_CREDENTIALS)
        decoded_string = decoded_bytes.decode('utf-8')
        # Parse the JSON string into a Python dictionary
        return json.loads(decoded_string)
        
    def _authenticate(self):
        creds = ServiceAccountCredentials.from_json_keyfile_dict(self.credentials_json, self.scopes)
        return gspread.authorize(creds)

    def insert_row(self, spreadsheet_name: str, sheet_name: str, row_data: list):
        if config.ENVIRONMENT == "TEST":
            return 
        
        try:
            spreadsheet = self.client.open(spreadsheet_name)
            sheet = spreadsheet.worksheet(sheet_name)
            sheet.append_row(row_data)
            logger.info(f"Row inserted successfully into '{sheet_name}' of '{spreadsheet_name}'.")
        except gspread.SpreadsheetNotFound:
            logger.error(f"Error: Spreadsheet '{spreadsheet_name}' not found.")
            raise 
        except gspread.WorksheetNotFound:
            logger.error(f"Error: Sheet '{sheet_name}' not found.")
            raise 
        except Exception as e:
            logger.error(f"An error occurred while inserting the row: {e}")
            raise 

