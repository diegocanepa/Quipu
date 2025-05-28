import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from api.telegram.handlers.command_handlers import show_info
from api.telegram.handlers.message_sender import MessageSender
from api.telegram.handlers.state_manager import StateManager
from core import messages
from core.onboarding import states
from core.user_data_manager import UserDataManager
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from config import config

logger = logging.getLogger(__name__)

# Initialize managers
user_manager = UserDataManager()
spreadsheet_manager = SpreadsheetManager()
message_sender = MessageSender()
state_manager = StateManager()

# --- Start Command Handlers ---
async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the /start command without a payload."""
    user = update.effective_user
    logger.info(f"User {user.id} initiated /start (no payload).")

    if user_manager.is_onboarding_complete(user.id):
        logger.info(f"User {user.id} is already onboarded. Showing status.")
        await message_sender.send_message(update, messages.MSG_WELCOME_BACK)
        await show_info(update, context)
        return ConversationHandler.END

    user_exists = user_manager.get_user_data(user.id) is not None
    welcome_message = messages.MSG_WELCOME_BACK if user_exists else messages.MSG_WELCOME

    if not user_exists:
        user_manager.create_user(
            telegram_user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )

    await message_sender.send_message(update, welcome_message)

    buttons = [
        (messages.BTN_GOOGLE_SHEET, 'link_sheet'),
        (messages.BTN_WEBAPP, 'link_webapp')
    ]
    await message_sender.send_message(
        update,
        messages.MSG_PRESENT_OPTIONS,
        keyboard=message_sender.create_keyboard(buttons)
    )

    state_manager.set_conversation_state(context, states.CHOOSING_LINK_METHOD)
    return states.CHOOSING_LINK_METHOD

# --- Google Sheet Handlers ---
async def choose_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user choosing Google Sheet linking."""
    user = update.effective_user
    logger.info(f"User {user.id} chose Google Sheet linking.")
    
    if update.callback_query:
        await update.callback_query.answer(messages.GOOGLE_SHEET_SELECTED)
        
    if user_manager.is_sheet_linked(user.id):
        return await state_manager.end_onboarding(update, context, messages.MSG_SHEET_ALREADY_LINKED)
    
    await message_sender.send_message(update, messages.MSG_SHEET_CHOICE_CONFIRM)
    
    await message_sender.send_message(
        update,
        messages.MSG_SHEET_STEP_1_COPY.format(template_url=config.GOOGLE_SHEET_TEMPLATE_URL)
    )
    await message_sender.send_message(
        update,
        messages.MSG_SHEET_STEP_2_SHARE.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL)
    )
    
    state_manager.set_conversation_state(context, states.GOOGLE_SHEET_AWAITING_URL)
    return states.GOOGLE_SHEET_AWAITING_URL

async def receive_sheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user sending a sheet URL."""
    user = update.effective_user
    sheet_url = update.message.text.strip()
    logger.info(f"User {user.id} provided potential sheet URL: {sheet_url}")

    sheet_id = spreadsheet_manager.get_sheet_id_from_url(sheet_url)
    if not sheet_id:
        logger.warning(f"User {user.id} provided invalid URL format: {sheet_url}")
        await message_sender.send_message(
            update,
            messages.MSG_SHEET_LINK_INVALID_URL,
            keyboard=message_sender.get_error_keyboard(states.GOOGLE_SHEET_AWAITING_URL)
        )
        return states.GOOGLE_SHEET_AWAITING_URL

    processing_msg = await message_sender.send_message(update, messages.MSG_SHEET_LINK_CHECKING)
    access_granted = spreadsheet_manager.check_access(sheet_id)
    await message_sender.clean_up_processing_message(processing_msg)

    if access_granted:
        user_manager.set_sheet_linked(user.id, sheet_id)
        logger.info(f"Sheet {sheet_id} linked successfully for user {user.id}.")
        return await state_manager.end_onboarding(update, context, messages.MSG_SHEET_LINK_SUCCESS)
    
    logger.warning(f"Access denied for sheet {sheet_id} for user {user.id}.")
    await message_sender.send_message(
        update,
        messages.MSG_SHEET_LINK_FAILED_ACCESS.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL),
        keyboard=message_sender.get_error_keyboard(states.GOOGLE_SHEET_AWAITING_URL)
    )
    return states.GOOGLE_SHEET_AWAITING_URL

# --- Webapp Handlers ---
async def choose_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the user choosing Webapp linking."""
    user = update.effective_user
    logger.info(f"User {user.id} chose Webapp linking.")

    if update.callback_query:
        await update.callback_query.answer(messages.WEBAPP_SELECTED)

    if user_manager.is_webapp_linked(user.id):
        return await state_manager.end_onboarding(
            update, 
            context, 
            messages.MSG_WEBAPP_ALREADY_LINKED.format(url_link=config.WEBAPP_BASE_URL)
        )

    await message_sender.send_message(update, messages.MSG_WEBAPP_CHOICE_CONFIRM)
    await message_sender.send_message(
        update,
        messages.MSG_WEBAPP_STEPS.format(webapp_base_url=config.WEBAPP_BASE_URL),
        disable_preview=True
    )

    state_manager.set_conversation_state(context, states.WEBAPP_SHOWING_INSTRUCTIONS)
    return states.WEBAPP_SHOWING_INSTRUCTIONS

async def handle_deeplink_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles webapp deep linking."""
    user = update.effective_user
    message = update.effective_message
    if not message or not message.text:
        logger.warning(f"Invalid deeplink message from user {user.id}")
        return ConversationHandler.END

    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        logger.warning(f"Invalid deeplink format from user {user.id}")
        return ConversationHandler.END

    payload = command_parts[1]
    if not payload.startswith("link_"):
        return ConversationHandler.END

    webapp_user_id = payload[5:]  # Remove "link_" prefix
    logger.info(f"Processing webapp linking for user {user.id} with ID: {webapp_user_id}")

    processing_msg = await message_sender.send_message(update, messages.MSG_WEBAPP_DEEPLINK_TRIGGERED)

    if webapp_user_id:
        user_manager.set_webapp_linked(user.id, webapp_user_id)
        await message_sender.clean_up_processing_message(processing_msg)
        logger.info(f"Webapp linked successfully for user {user.id}")
        return await state_manager.end_onboarding(update, context, messages.MSG_WEBAPP_LINK_SUCCESS)
    
    logger.warning(f"Webapp linking failed for user {user.id}")
    await message_sender.send_message(
        update,
        messages.MSG_WEBAPP_LINK_FAILED.format(webapp_base_url=config.WEBAPP_BASE_URL),
        keyboard=message_sender.get_error_keyboard(states.WEBAPP_SHOWING_INSTRUCTIONS)
    )
    state_manager.set_conversation_state(context, states.WEBAPP_SHOWING_INSTRUCTIONS)
    return states.WEBAPP_SHOWING_INSTRUCTIONS

# --- General Handlers ---
async def cancel_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles onboarding cancellation."""
    if update.callback_query:
        await update.callback_query.answer(messages.CANCEL_ONBOARDING_ANSWER)
    
    state_manager.set_conversation_state(context, states.FINISHED, False)
    await message_sender.send_message(update, messages.MSG_CANCEL_ONBOARDING_CONFIRM)
    return ConversationHandler.END

async def onboarding_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles unrecognized messages during onboarding."""
    user = update.effective_user
    current_state = state_manager.get_current_state(context)
    logger.warning(f"Unhandled message from user {user.id} in state {current_state}")

    if current_state == states.FINISHED:
        return ConversationHandler.END

    state_messages = {
        states.GOOGLE_SHEET_AWAITING_URL: messages.MSG_SHEET_LINK_INVALID_URL,
        states.WEBAPP_SHOWING_INSTRUCTIONS: messages.MSG_WEBAPP_LINK_FAILED,
        states.CHOOSING_LINK_METHOD: messages.MSG_ONBOARDING_REQUIRED
    }

    message = state_messages.get(current_state, messages.MSG_ONBOARDING_ERROR)
    keyboard = message_sender.get_error_keyboard(current_state)
    
    await message_sender.send_message(
        update,
        message.format(webapp_base_url=config.WEBAPP_BASE_URL) if current_state == states.WEBAPP_SHOWING_INSTRUCTIONS else message,
        keyboard=keyboard,
        disable_preview=True
    )
    return current_state or states.CHOOSING_LINK_METHOD

# --- Conversation Handler Definition ---
onboarding_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.TEXT & filters.Regex(r'^/start$'), start_onboarding),
        MessageHandler(filters.TEXT & filters.Regex(r'^/start link_.*'), handle_deeplink_start),
        CommandHandler('linksheet', choose_sheet),
        CommandHandler('linkweb', choose_webapp),
        CallbackQueryHandler(choose_sheet, pattern='^link_sheet$'),
        CallbackQueryHandler(choose_webapp, pattern='^link_webapp$'),
    ],
    states={
        states.CHOOSING_LINK_METHOD: [
            CallbackQueryHandler(choose_sheet, pattern='^link_sheet$'),
            CallbackQueryHandler(choose_webapp, pattern='^link_webapp$'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_fallback)
        ],
        states.GOOGLE_SHEET_AWAITING_URL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sheet_url),
            CallbackQueryHandler(cancel_onboarding, pattern='^cancel_onboarding$'),
            CallbackQueryHandler(choose_sheet, pattern='^retry_sheet_url$'),
            CallbackQueryHandler(choose_webapp, pattern='^switch_to_webapp$'),
        ],
        states.WEBAPP_SHOWING_INSTRUCTIONS: [
            MessageHandler(filters.TEXT & filters.Regex(r'^/start link_.*'), handle_deeplink_start),
            CallbackQueryHandler(cancel_onboarding, pattern='^cancel_onboarding$'),
            CallbackQueryHandler(choose_sheet, pattern='^switch_to_sheet$'),
            MessageHandler(filters.TEXT, onboarding_fallback)
        ]
    },
    fallbacks=[
        MessageHandler(filters.TEXT & filters.Regex(r'^/start link_.*'), handle_deeplink_start),
        CommandHandler('cancel', cancel_onboarding),
        MessageHandler(filters.ALL, onboarding_fallback)
    ]
)