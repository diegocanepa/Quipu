import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from core.user_data_manager import UserDataManager
from core.models.user import User
from core.messages import UNEXPECTED_ERROR

logger = logging.getLogger(__name__)

# Initialize UserDataManager
user_manager = UserDataManager()

def get_user(handler_func):
    """
    Decorator to extract user information from Telegram updates and get the full User object from database.
    This middleware can be used with class methods to get user data.
    
    Usage:
    @get_user
    async def handle_something(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user: User = context.user_data.get('current_user')  # Access user from context
        # Use user data...
        if user.is_sheet_linked:
            # Do something with sheet data
        if user.is_webapp_linked:
            # Do something with webapp data
    """
    @wraps(handler_func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        telegram_user = update.effective_user
        
        if not telegram_user:
            logger.warning("No user found in update")
            await update.effective_message.reply_text(UNEXPECTED_ERROR)
            return
            
        try:
            # Get full user data from database
            user = user_manager.get_user_by_telegram_user_id(telegram_user.id)
            
            if not user:
                logger.info(f"Creating new user for telegram_id: {telegram_user.id}")
                # Create new user if doesn't exist
                user_manager.create_user_from_telegram(
                    telegram_user_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name
                )
                
                # Get the newly created user
                user = user_manager.get_user_by_telegram_user_id(telegram_user.id)
                
                if not user:
                    logger.error(f"Failed to create or retrieve user for telegram_id: {telegram_user.id}")
                    await update.effective_message.reply_text(UNEXPECTED_ERROR)
                    return
                
                logger.info(f"Successfully created new user for telegram_id: {telegram_user.id}")
            
            # Update last interaction time
            user_manager.update_last_interaction_time(user.id)
                
            # Store full user object in context for easy access
            context.user_data['current_user'] = user
            
            logger.debug(f"User data loaded for user {telegram_user.id}")
            return await handler_func(self, update, context, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in get_user middleware: {str(e)}")
            await update.effective_message.reply_text(UNEXPECTED_ERROR)
            return
        
    return wrapper 