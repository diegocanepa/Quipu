import logging
from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from core.user_data_manager import UserDataManager
from telegram.ext import ContextTypes
from core.messages import MSG_ONBOARDING_REQUIRED, BTN_GOOGLE_SHEET, BTN_WEBAPP, UNEXPECTED_ERROR
from core.models.user import User

logger = logging.getLogger(__name__)

# Initialize UserDataManager
user_manager = UserDataManager()

def require_onboarding(handler_func):
    """
    Decorator to check if user is onboarded before running handler.
    Also stores the user object in context.user_data['current_user'].
    
    Usage:
    @require_onboarding
    async def handle_something(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user: User = context.user_data.get('current_user')  # Access user from context
        # Use user data...
    """
    @wraps(handler_func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            
            # Store full user object in context for easy access
            context.user_data['current_user'] = user
            
            # Check if user is onboarded
            if user_manager.is_onboarding_complete(telegram_user.id):
                logger.debug(f"User {telegram_user.id} is onboarded. Proceeding with handler {handler_func.__name__}.")
                return await handler_func(update, context)
            else:
                logger.info(f"User {telegram_user.id} is NOT onboarded. Blocking handler {handler_func.__name__}.")
                
                keyboard = [
                    [InlineKeyboardButton(BTN_GOOGLE_SHEET, callback_data='link_sheet')],
                    [InlineKeyboardButton(BTN_WEBAPP, callback_data='link_webapp')]
                ]
                await update.effective_message.reply_text(
                    MSG_ONBOARDING_REQUIRED, 
                    parse_mode='HTML', 
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
                
        except Exception as e:
            logger.error(f"Error in require_onboarding middleware: {str(e)}")
            await update.effective_message.reply_text(UNEXPECTED_ERROR)
            return
            
    return wrapper

def create_user_if_not_exists(user_id, username, first_name, last_name):
    user_exists = user_manager.get_user_data(user_id) is not None
    if not user_exists:
        user_manager.create_user_from_telegram(
            telegram_user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )