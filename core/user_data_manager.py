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
    
    def create_user_from_whatsapp(self, whatsapp_user_id: str) -> Optional[User]:
        """
        Creates a new user from WhatsApp data.

        Args:
            whatsapp_user_id: The WhatsApp user ID (phone number).

        Returns:
            Optional[User]: The created user if successful, None otherwise.
        """
        try:
            # Check if user already exists
            existing_user = self.get_user_by_whatsapp_user_id(whatsapp_user_id)
            if existing_user:
                logger.info(f"User with WhatsApp ID {whatsapp_user_id} already exists.")
                return existing_user

            # Create new user
            now_utc = datetime.now(timezone.utc)
            new_user = User(
                id=uuid.uuid4(),
                created_at=now_utc,
                last_interaction_at=now_utc,
                whatsapp_user_id=whatsapp_user_id
            )
            
            result = self._client.insert(self._users_table, new_user.to_dict())
            if result:
                logger.info(f"New WhatsApp user {whatsapp_user_id} created in Supabase.")
                return new_user
            else:
                logger.error(f"Error creating WhatsApp user {whatsapp_user_id} in Supabase.")
                return None
                
        except Exception as e:
            logger.error(f"Error creating WhatsApp user: {e}")
            return None

    def create_user_from_telegram(
        self,
        telegram_user_id: int,
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
        existing_user = self.get_user_data(telegram_user_id)
        if not existing_user:
            now_utc = datetime.now(timezone.utc)
            new_user = User(
                id=uuid.uuid4(),
                telegram_user_id=telegram_user_id,
                telegram_username=username,
                telegram_first_name=first_name,
                telegram_last_name=last_name,
                created_at=now_utc,
                last_interaction_at=now_utc
            )
            
            result = self._client.insert(self._users_table, new_user.to_dict())
            if result:
                logger.info(f"New user {telegram_user_id} created in Supabase.")
            else:
                logger.error(f"Error creating user {telegram_user_id} in Supabase.")
        else:
            logger.info(f"User {telegram_user_id} already exists. Skipping creation.")

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
