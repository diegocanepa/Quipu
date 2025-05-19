import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from integrations.supabase.supabase import SupabaseManager

logger = logging.getLogger(__name__)

class UserDataManager:
    def __init__(self):
        self._client = SupabaseManager()
        self._users_table = self._client.get_table_name("users")

    def _get_user_from_supabase(self, user_id: int) -> Dict[str, Any] | None:
        """Internal method to get user data from Supabase."""
        try:
            response = self._client._client.table(self._users_table)\
                .select("*")\
                .eq("telegram_user_id", user_id)\
                .execute()
            
            if response and hasattr(response, 'data') and response.data:
                logger.info(f"Found user {user_id} in Supabase.")
                return response.data[0]
            
            logger.info(f"No user found for ID: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting user data from Supabase: {e}")
            return None

    def get_user_data(self, user_id: int) -> dict | None:
        """
        Retrieves all data for a specific user.

        Args:
            user_id: The Telegram user ID (integer).

        Returns:
            A dictionary containing the user's data, or None if the user is not found.
        """
        return self._get_user_from_supabase(user_id)

    def create_user(
        self,
        user_id: int,
        username: str | None,
        first_name: str,
        last_name: str | None
    ) -> None:
        """
        Creates a new user entry if they do not already exist.

        Args:
            user_id: The Telegram user ID (integer).
            username: The user's Telegram username (string, can be None).
            first_name: The user's Telegram first name (string).
            last_name: The user's Telegram last name (string, can be None).
        """
        existing_user = self.get_user_data(user_id)
        if not existing_user:
            now_utc_iso = self.get_now_utc()
            user_data = {
                "telegram_user_id": user_id,
                "google_sheet_id": None,
                "webapp_user_id": None,
                "webapp_integration_id": None,
                "created_at": now_utc_iso,
                "last_interaction_at": now_utc_iso,
                "telegram_username": username,
                "telegram_first_name": first_name,
                "telegram_last_name": last_name,
            }
            result = self._client.insert(self._users_table, user_data)
            if result:
                logger.info(f"New user {user_id} created in Supabase.")
            else:
                logger.error(f"Error creating user {user_id} in Supabase.")
        else:
            logger.info(f"User {user_id} already exists. Skipping creation.")

    def update_last_interaction_time(self, user_id: int) -> None:
        """Updates the last interaction timestamp for an existing user."""
        try:
            now_utc_iso = self.get_now_utc()
            self._client._client.table(self._users_table)\
                .update({"last_interaction_at": now_utc_iso})\
                .eq("telegram_user_id", user_id)\
                .execute()
            logger.debug(f"Updated last interaction time for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Error updating last interaction time: {e}")

    def set_sheet_linked(self, user_id: int, sheet_id: str) -> None:
        """Sets Google Sheet ID for a user."""
        try:
            self._client._client.table(self._users_table)\
                .update({"google_sheet_id": sheet_id})\
                .eq("telegram_user_id", user_id)\
                .execute()
            logger.info(f"User {user_id} Google Sheet linked: {sheet_id}")
        except Exception as e:
            logger.error(f"Error setting sheet link: {e}")

    def set_webapp_linked(self, user_id: int, webapp_user_id: str) -> None:
        """Sets Webapp IDs for a user."""
        try:
            self._client._client.table(self._users_table)\
                .update({
                    "webapp_user_id": webapp_user_id,
                    "last_interaction_at": self.get_now_utc()
                })\
                .eq("telegram_user_id", user_id)\
                .execute()
            logger.info(f"User {user_id} Webapp linked. User ID: {webapp_user_id}")
        except Exception as e:
            logger.error(f"Error setting webapp link: {e}")

    def is_sheet_linked(self, user_id: int) -> bool:
        """Checks if Google Sheet is linked for the user."""
        user_data = self.get_user_data(user_id)
        return user_data is not None and user_data.get("google_sheet_id") is not None

    def is_webapp_linked(self, user_id: int) -> bool:
        """Checks if Webapp is linked for the user."""
        user_data = self.get_user_data(user_id)
        return user_data is not None and user_data.get("webapp_user_id") is not None

    def is_onboarding_complete(self, user_id: int) -> bool:
        """
        Checks if at least one method is linked.
        Makes a single database call to check both linking methods.
        """
        user_data = self.get_user_data(user_id)
        if not user_data:
            return False
            
        has_sheet = user_data.get("google_sheet_id") is not None
        has_webapp = user_data.get("webapp_user_id") is not None
        
        return has_sheet or has_webapp

    def get_user_linking_status(self, user_id: int) -> dict:
        """Retrieves linking status for a user."""
        sheet_id = self.get_linked_sheet_id(user_id)
        webapp_user_id = self.get_linked_webapp_user_id(user_id)
        return {
            "sheet_id": sheet_id,
            "webapp_user_id": webapp_user_id
        }

    def get_linked_sheet_id(self, user_id: int) -> Optional[str]:
        """Returns the linked Google Sheet ID or None."""
        user_data = self.get_user_data(user_id)
        return user_data.get("google_sheet_id") if user_data else None

    def get_linked_webapp_user_id(self, user_id: int) -> Optional[str]:
        """Returns the linked Webapp User ID or None."""
        user_data = self.get_user_data(user_id)
        return user_data.get("webapp_user_id") if user_data else None

    @staticmethod
    def get_now_utc() -> str:
        """Gets the current time in UTC and formats it as an ISO 8601 string."""
        return datetime.now(timezone.utc).isoformat()
