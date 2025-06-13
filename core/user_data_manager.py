import logging
from datetime import datetime, timezone
from typing import Optional
import uuid

from integrations.supabase.supabase import SupabaseManager
from core.models.user import User

logger = logging.getLogger(__name__)

class UserDataManager:
    def __init__(self):
        self._client = SupabaseManager()
        self._users_table = self._client.get_table_name("users")

    def get_user_by_telegram_user_id(self, telegram_user_id: int) -> Optional[User]:
        """
        Retrieves a user by their Telegram user ID.

        Args:
            telegram_user_id: The Telegram user ID (integer).
        """
        try:
            response = self._client._client.table(self._users_table)\
                .select("*")\
                .eq("telegram_user_id", telegram_user_id)\
                .execute()
            
            if response and hasattr(response, 'data') and response.data:
                logger.info(f"Found user {telegram_user_id} in Supabase.")
                return User.from_dict(response.data[0])
            
            logger.info(f"No user found for ID: {telegram_user_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting user data from Supabase: {e}")
            return None
    
    def get_user_by_whatsapp_user_id(self, whatsapp_user_id: int) -> Optional[User]:
        """
        Retrieves a user by their WhatsApp user ID.

        Args:
            whatsapp_user_id: The WhatsApp user ID (integer).
        """
        try:
            response = self._client._client.table(self._users_table)\
                .select("*")\
                .eq("whatsapp_user_id", whatsapp_user_id)\
                .execute()
            
            if response and hasattr(response, 'data') and response.data:
                logger.info(f"Found user {whatsapp_user_id} in Supabase.")
                return User.from_dict(response.data[0])
            
            logger.info(f"No user found for ID: {whatsapp_user_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting user data from Supabase: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieves a user by their ID.

        Args:
            user_id: The user ID (string).
        """
        try:
            response = self._client._client.table(self._users_table)\
                .select("*")\
                .eq("id", user_id)\
                .execute()
            
            if response and hasattr(response, 'data') and response.data:
                logger.info(f"Found user {user_id} in Supabase.")
                return User.from_dict(response.data[0])
            
            logger.info(f"No user found for ID: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting user data from Supabase: {e}")
            return None

    def get_user_data(self, user_id: str) -> Optional[User]:
        """
        Retrieves all data for a specific user.

        Args:
            user_id: The Telegram user ID (integer).

        Returns:
            A User instance containing the user's data, or None if the user is not found.
        """
        return self.get_user_by_id(user_id)
    
    def update_last_interaction_time(self, user_id: str) -> None:
        """Updates the last interaction timestamp for an existing user."""
        try:
            now_utc = datetime.now(timezone.utc)
            self._client._client.table(self._users_table)\
                .update({"last_interaction_at": now_utc.isoformat()})\
                .eq("id", user_id)\
                .execute()
            logger.debug(f"Updated last interaction time for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Error updating last interaction time: {e}")

    def set_sheet_linked(self, user_id: str, sheet_id: str) -> None:
        """Sets Google Sheet ID for a user."""
        try:
            self._client._client.table(self._users_table)\
                .update({"google_sheet_id": sheet_id})\
                .eq("id", user_id)\
                .execute()
            logger.info(f"User {user_id} Google Sheet linked: {sheet_id}")
        except Exception as e:
            logger.error(f"Error setting sheet link: {e}")

    def set_webapp_linked(self, user_id: int, webapp_user_id: str) -> None:
        """Sets Webapp IDs for a user."""
        try:
            now_utc = datetime.now(timezone.utc)
            self._client._client.table(self._users_table)\
                .update({
                    "webapp_user_id": webapp_user_id,
                    "last_interaction_at": now_utc.isoformat()
                })\
                .eq("id", user_id)\
                .execute()
            logger.info(f"User {user_id} Webapp linked. User ID: {webapp_user_id}")
        except Exception as e:
            logger.error(f"Error setting webapp link: {e}")

    def is_sheet_linked(self, user_id: int) -> bool:
        """Checks if Google Sheet is linked for the user."""
        user = self.get_user_data(user_id)
        return user.is_sheet_linked if user else False

    def is_webapp_linked(self, user_id: int) -> bool:
        """Checks if Webapp is linked for the user."""
        user = self.get_user_data(user_id)
        return user.is_webapp_linked if user else False

    def is_onboarding_complete(self, user_id: int) -> bool:
        """
        Checks if at least one method is linked.
        Makes a single database call to check both linking methods.
        """
        user = self.get_user_data(user_id)
        return user.is_onboarding_complete if user else False

    def get_user_linking_status(self, user_id: int) -> dict:
        """Retrieves linking status for a user."""
        user = self.get_user_data(user_id)
        return user.linking_status if user else {'sheet_id': None, 'webapp_user_id': None}

    def get_linked_sheet_id(self, user_id: int) -> Optional[str]:
        """Returns the linked Google Sheet ID or None."""
        user = self.get_user_data(user_id)
        return user.google_sheet_id if user else None

    def get_linked_webapp_user_id(self, user_id: int) -> Optional[str]:
        """Returns the linked Webapp User ID or None."""
        user = self.get_user_data(user_id)
        return user.webapp_user_id if user else None

    def create_user(self, 
                   id: str,
                   telegram_user_id: Optional[int] = None,
                   webapp_user_id: Optional[str] = None,
                   whatsapp_user_id: Optional[str] = None,
                   google_sheet_id: Optional[str] = None,
                   webapp_integration_id: Optional[str] = None) -> Optional[User]:
        """
        Creates a new user with the specified parameters.
        If a user with the given ID already exists, returns the existing user.
        
        Args:
            id: The unique identifier for the user
            telegram_user_id: Optional Telegram user ID
            webapp_user_id: Optional webapp user ID
            whatsapp_user_id: Optional WhatsApp user ID
            google_sheet_id: Optional Google Sheet ID
            webapp_integration_id: Optional webapp integration ID
            
        Returns:
            The User instance if successful (either existing or newly created), None otherwise.
        """
        try:
            # First check if user already exists
            existing_user = self.get_user_by_id(id)
            if existing_user:
                logger.info(f"User with ID {id} already exists")
                return existing_user

            now_utc = datetime.now(timezone.utc)
            user_data = {
                "id": id,
                "telegram_user_id": telegram_user_id,
                "webapp_user_id": webapp_user_id,
                "whatsapp_user_id": whatsapp_user_id,
                "google_sheet_id": google_sheet_id,
                "webapp_integration_id": webapp_integration_id,
                "created_at": now_utc.isoformat(),
                "last_interaction_at": now_utc.isoformat()
            }
            
            # Remove None values to avoid storing nulls in the database
            user_data = {k: v for k, v in user_data.items() if v is not None}
            
            response = self._client._client.table(self._users_table)\
                .insert(user_data)\
                .execute()
            
            if response and hasattr(response, 'data') and response.data:
                logger.info(f"Created new user with ID: {id}")
                return User.from_dict(response.data[0])
            
            logger.error(f"Failed to create user with ID: {id}")
            return None
        except Exception as e:
            logger.error(f"Error creating user with ID: {e}")
            return None

    def update_user(self, user_id: str, **update_data) -> Optional[User]:
        """
        Updates specific fields for a user.
        
        Args:
            user_id: The ID of the user to update
            **update_data: Dictionary of fields to update and their new values
            
        Returns:
            The updated User instance if successful, None otherwise
        """
        try:
            # Remove None values to avoid storing nulls in the database
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if not update_data:
                logger.warning(f"No valid data provided for update for user {user_id}")
                return None
                
            # Add last_interaction_at timestamp
            now_utc = datetime.now(timezone.utc)
            update_data["last_interaction_at"] = now_utc.isoformat()
            
            response = self._client._client.table(self._users_table)\
                .update(update_data)\
                .eq("id", user_id)\
                .execute()
            
            if response and hasattr(response, 'data') and response.data:
                logger.info(f"Successfully updated user {user_id}")
                return User.from_dict(response.data[0])
            
            logger.error(f"Failed to update user {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return None