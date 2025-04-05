from abc import ABC, abstractmethod
from typing import Dict, Any
from supabase import create_client, Client
from config import config

class SupabaseManagerService(ABC):
    @abstractmethod
    def insert(self, spreadsheet_name: str, sheet_name: str, row_data: list):
        pass
    
class SupabaseManager(SupabaseManagerService):
    def __init__(self):
        self._client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

    async def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Inserts a new record into the specified table."""
        if config.ENVIRONMENT == "TEST":
            table_name = '{}_test'.format(table_name)
        
        try:
            response = await self._client.table(table_name).insert(data).execute()
            if response.error:
                print(f"Error inserting into '{table_name}': {response.error}")
                return None
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"An error occurred while inserting into '{table_name}': {e}")
            return None