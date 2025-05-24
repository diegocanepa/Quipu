# tu_proyecto/main.py
from datetime import datetime
import logging
import os
from core.models.financial.transaction import Transaction, TransactionType
from core.models.message import Message, Source
from core.models.onboarding_status import OnboardingStatus, State
from core.services.message_service import MessageService
from core.services.onboarding_service import OnboardingService
from integrations.cache.redis_client import cache_client  # Import the global cache client
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Initialize services
    message_service = MessageService(cache_service=cache_client)
    onboarding_service = OnboardingService(cache_service=cache_client)
    print(cache_client)
    # --- Test Message Service ---
    print("\n--- Testing Message Service ---")
    user_id_msg = "user_123"
    message_id_test = "msg_456"
    platform_test = Source.TELEGRAM

    # Try to get message (should not exist initially)
    retrieved_message_initial = message_service.get_message(user_id_msg, message_id_test, platform_test)
    print(f"Initial get_message: {retrieved_message_initial}")

    new_transaction = Transaction(
        description="Test Income",
        amount=100.0,
        currency="USD",
        category="Salary",
        date=datetime.now(),
        action=TransactionType.INCOME,
        transaction_id="transaction_id_test",
        user_id="user_id_msg"
    )

    # Create a new message
    new_message = Message(
        user_id=user_id_msg,
        message_id=message_id_test,
        message_text="Hello from test main!",
        message_object = new_transaction,
        source=platform_test
    )

    # Save the message
    saved_successfully = message_service.save_message(user_id_msg, new_message)
    print(f"save_message successful: {saved_successfully}")

    # Get the message again (should now exist in cache)
    retrieved_message_cached = message_service.get_message(user_id_msg, message_id_test, platform_test)
    print(f"get_message after saving: {retrieved_message_cached}")

    # Delete the message
    deleted_successfully = message_service.delete_message(user_id_msg, message_id_test, platform_test)
    print(f"delete_message successful: {deleted_successfully}")

    # Try to get the message again (should be deleted)
    retrieved_message_deleted = message_service.get_message(user_id_msg, message_id_test, platform_test)
    print(f"get_message after deleting: {retrieved_message_deleted}")

    # --- Test Onboarding Service ---
    print("\n--- Testing Onboarding Service ---")
    user_id_onboarding = "user_abc"

    # Try to get onboarding status (should not exist initially)
    initial_status = onboarding_service.get_onboarding_status(user_id_onboarding)
    print(f"Initial get_onboarding_status: {initial_status}")

    # Create a new onboarding status
    new_onboarding = OnboardingStatus(
        user_id=user_id_onboarding,
        state=State.CHOOSING_LINK_METHOD,
    )

    # Save the onboarding status
    saved_onboarding = onboarding_service.save_onboarding_status(user_id_onboarding, new_onboarding)
    print(f"save_onboarding_status successful: {saved_onboarding}")

    # Get the onboarding status again (should now exist in cache)
    cached_status = onboarding_service.get_onboarding_status(user_id_onboarding)
    print(f"get_onboarding_status after saving: {cached_status}")

    # Delete the onboarding status
    deleted_onboarding = onboarding_service.delete_onboarding_status(user_id_onboarding)
    print(f"delete_onboarding_status successful: {deleted_onboarding}")

    # Try to get the onboarding status again (should be deleted)
    status_after_deletion = onboarding_service.get_onboarding_status(user_id_onboarding)
    print(f"get_onboarding_status after deleting: {status_after_deletion}")

    print("\n--- End of Tests ---")