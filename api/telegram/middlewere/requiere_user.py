import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from core.user_data_manager import UserDataManager
from core.messages import UNEXPECTED_ERROR, MSG_WEBAPP_NOT_REGISTERED_HTML
from config import config

logger = logging.getLogger(__name__)

# Initialize UserDataManager
user_manager = UserDataManager()

def require_user(handler_func):
    """
    Decorator to check if user exists in the database before running handler.
    Also stores the user object in context.user_data['current_user'].
    
    Usage:
    class MyHandler:
        @require_user
        async def handle_something(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
            user: User = context.user_data.get('current_user')
            # Use user data...
    """
    @wraps(handler_func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        telegram_user = update.effective_user
        
        if not telegram_user:
            logger.warning("No user found in update")
            await update.effective_message.reply_text(UNEXPECTED_ERROR)
            return
            
        try:
            # Get full user data from database
            user = user_manager.get_user_by_telegram_user_id(telegram_user.id)
            
            if not user:
                logger.info(f"User does not exist yet: {telegram_user.id}")
                await update.effective_message.reply_text(
                    MSG_WEBAPP_NOT_REGISTERED_HTML.format(webapp_signup_url=config.WEBAPP_BASE_URL), 
                    parse_mode='HTML'
                )
                return
            
            # Store full user object in context for easy access
            context.user_data['current_user'] = user
            return await handler_func(self, update, context)
                
        except Exception as e:
            logger.error(f"Error in require_user middleware: {str(e)}")
            await update.effective_message.reply_text(UNEXPECTED_ERROR)
            return
            
    return wrapper
