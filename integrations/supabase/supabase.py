import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from supabase import create_client, Client
from config import config

logger = logging.getLogger(__name__)

class SupabaseManagerService(ABC):
    @abstractmethod
    def insert(self, spreadsheet_name: str, sheet_name: str, row_data: list):
        pass
    
class SupabaseManager(SupabaseManagerService):
    def __init__(self):
        self._client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

    def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Inserts a new record into the specified table."""        
        try:
            response = self._client.table(table_name).insert(data).execute()
            
            if hasattr(response, 'data') and response.data:
                return response.data[0]
            if hasattr(response, 'error') and response.error:
                logger.error(f"Error inserting into '{table_name}': {response.error}")
                return None
            return None
        except Exception as e:
            logger.error(f"An error occurred while inserting into '{table_name}': {e}")
            return None
        
    def get_table_name(self, table_name: str) -> str:
        if config.ENVIRONMENT == "TEST":
            return '{}_test'.format(table_name)
        return table_name