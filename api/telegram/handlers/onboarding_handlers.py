import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from api.telegram.handlers.command_handlers import show_info

from core import messages
from core.onboarding import states
from core.user_data_manager import UserDataManager
from core.onboarding.google_sheet_linker import GoogleSheetLinker
from config import config

logger = logging.getLogger(__name__)

# Initialize UserDataManager
user_manager = UserDataManager()
sheet_linker = GoogleSheetLinker()

# --- Onboarding Start Handler (Entry point for ConversationHandler) ---
async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the /start command without a payload.
    Sends the welcome message and presents linking options if not onboarded.
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated /start (no payload).")

    # Check if already onboarded
    if user_manager.is_onboarding_complete(user.id):
        logger.info(f"User {user.id} is already onboarded. Showing status.")
        await update.effective_message.reply_text(messages.MSG_WELCOME_BACK, parse_mode='HTML') # TODO: Add to a message where they can see the data they have linked
        # Also show info using the info handler logic
        await show_info(update, context)
        return ConversationHandler.END # End the onboarding conversation if already done


    user_exists = user_manager.get_user_data(user.id) is not None

    if not user_exists:
        user_manager.create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        await update.effective_message.reply_text(messages.MSG_WELCOME, parse_mode='HTML')
    else:
        await update.effective_message.reply_text(messages.MSG_WELCOME_BACK, parse_mode='HTML')


    # Present linking options with inline buttons
    keyboard = [
        [InlineKeyboardButton(messages.BTN_GOOGLE_SHEET, callback_data='link_sheet')],
        [InlineKeyboardButton(messages.BTN_WEBAPP, callback_data='link_webapp')]
    ]

    await update.effective_message.reply_text(
        messages.MSG_PRESENT_OPTIONS,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # If not onboarded, start the process. This flag is used to indicate user is in the flow.
    context.user_data['onboarding_in_progress'] = True 
    context.user_data['onboarding_state'] = states.CHOOSING_LINK_METHOD
    return states.CHOOSING_LINK_METHOD

# --- Handler for user choosing Google Sheet ---
async def choose_sheet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user choosing Google Sheet linking.
    Can be triggered by both callback query and command.
    """
    user = update.effective_user
    logger.info(f"User {user.id} chose Google Sheet linking.")
    
    message = update.effective_message
    
    # If it's a callback query, answer it to remove loading indicator
    if update.callback_query:
        await update.callback_query.answer("✅ Seleccionaste Google Sheet")
        
    if user_manager.is_sheet_linked(user.id):
        await message.reply_text(messages.MSG_SHEET_ALREADY_LINKED, parse_mode='HTML')
        context.user_data['onboarding_in_progress'] = False
        context.user_data['onboarding_state'] = states.FINISHED
        return ConversationHandler.END
    
    base_message = await message.reply_text(messages.MSG_SHEET_CHOICE_CONFIRM)

    # Send the steps as new messages
    await base_message.reply_text(
        messages.MSG_SHEET_STEP_1_COPY.format(template_url=config.GOOGLE_SHEET_TEMPLATE_URL),
        parse_mode='HTML'
    )

    await base_message.reply_text(
        messages.MSG_SHEET_STEP_2_SHARE.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL),
        parse_mode='HTML'
    )
    
    context.user_data['onboarding_in_progress'] = True
    context.user_data['onboarding_state'] = states.GOOGLE_SHEET_AWAITING_URL
    return states.GOOGLE_SHEET_AWAITING_URL

# --- Handler for user providing Sheet URL ---
async def receive_sheet_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user sending a message when in the state of waiting for a sheet URL.
    Validates the URL, checks Service Account access, and links the sheet.
    """
    
    user = update.effective_user
    sheet_url = update.message.text.strip() # Get text and remove leading/trailing whitespace
    logger.info(f"User {user.id} provided potential sheet URL: {sheet_url}")

    # Validate if it looks like a URL and extract the ID
    sheet_id = sheet_linker.get_sheet_id_from_url(sheet_url)

    if not sheet_id:
        logger.warning(f"User {user.id} provided text not matching URL format: {sheet_url}")
        
        keyboard = [
            [InlineKeyboardButton(messages.BTN_SWITCH_TO_WEBAPP, callback_data='switch_to_webapp')], # Option to switch
            [InlineKeyboardButton(messages.BTN_CANCEL_ONBOARDING, callback_data='cancel_onboarding')] # Option to cancel
        ]
        
        await update.message.reply_text(messages.MSG_SHEET_LINK_INVALID_URL, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        
        context.user_data['onboarding_in_progress'] = True
        context.user_data['onboarding_state'] = states.GOOGLE_SHEET_AWAITING_URL
        return states.GOOGLE_SHEET_AWAITING_URL

    # Check access using the extracted sheet_id
    # This might take a few seconds, consider showing a "processing" message
    processing_message = await update.message.reply_text(messages.MSG_SHEET_LINK_CHECKING, parse_mode='HTML')

    access_granted = sheet_linker.check_sheet_access(sheet_id)

    # Delete the processing message
    try:
        await processing_message.delete()
    except Exception as e:
         logger.warning(f"Failed to delete processing message: {e}")

    if access_granted:
        user_manager.set_sheet_linked(user.id, sheet_id) # Store the sheet ID in user_data_manager
        logger.info(f"Google Sheet ID {sheet_id} linked successfully for user {user.id}.")
        await update.message.reply_text(messages.MSG_SHEET_LINK_SUCCESS, parse_mode='HTML')

        context.user_data['onboarding_in_progress'] = False # Mark the conversation path as complete

        # If this was the first linked method, onboarding is complete!
        # If they already had webapp linked, great! They have both.
        # We don't need explicit state transitions based on having both,
        # the `is_onboarding_complete` check handles it.
        context.user_data['onboarding_in_progress'] = False
        context.user_data['onboarding_state'] = states.FINISHED
        return ConversationHandler.END # End the onboarding conversation

    else:
        # Access was not granted (sheet not found, permission denied, etc.)
        logger.warning(f"Access denied for sheet ID {sheet_id} for user {user.id}. Providing options.")
        keyboard = [
            [InlineKeyboardButton(messages.BTN_SWITCH_TO_WEBAPP, callback_data='switch_to_webapp')], # Option to switch
            [InlineKeyboardButton(messages.BTN_CANCEL_ONBOARDING, callback_data='cancel_onboarding')] # Option to cancel
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            messages.MSG_SHEET_LINK_FAILED_ACCESS.format(sa_email=config.GOOGLE_SERVICE_ACCOUNT_EMAIL),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        context.user_data['onboarding_in_progress'] = True
        context.user_data['onboarding_state'] = states.GOOGLE_SHEET_AWAITING_URL
        return states.GOOGLE_SHEET_AWAITING_URL # Stay in this state, user can send another URL or click button
        
        
# --- Handler for user choosing Webapp ---
async def choose_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user choosing Webapp linking.
    Can be triggered by both callback query and command.
    """
    user = update.effective_user
    logger.info(f"User {user.id} chose Webapp linking.")

    message = update.effective_message
    
    # If it's a callback query, answer it to remove loading indicator
    if update.callback_query:
        await update.callback_query.answer("✅ Seleccionaste Cuenta Web")

    if user_manager.is_webapp_linked(user.id):
        await message.reply_text(messages.MSG_WEBAPP_ALREADY_LINKED.format(url_link=config.WEBAPP_BASE_URL), parse_mode='HTML')
        context.user_data['onboarding_in_progress'] = False
        context.user_data['onboarding_state'] = states.FINISHED
        return ConversationHandler.END

    # Send confirmation and instructions
    await message.reply_text(messages.MSG_WEBAPP_CHOICE_CONFIRM, parse_mode='HTML')
    webapp_register_url = config.WEBAPP_BASE_URL
    await message.reply_text(
        messages.MSG_WEBAPP_STEPS.format(webapp_base_url=webapp_register_url),
        parse_mode='HTML',
        disable_web_page_preview=True
    )

    context.user_data['onboarding_in_progress'] = True
    context.user_data['onboarding_state'] = states.WEBAPP_SHOWING_INSTRUCTIONS
    return states.WEBAPP_SHOWING_INSTRUCTIONS


# --- Global Handler for /start with payload (Webapp Linking Trigger) ---
async def handle_deeplink_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles /start commands that include a payload, specifically for webapp linking.
    Returns appropriate conversation state to maintain conversation flow.
    """
    user = update.effective_user
    message = update.message
    if not message or not message.text:
        logger.warning(f"handle_deeplink_start received invalid message from user {user.id}. Ignoring.")
        return ConversationHandler.END

    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        logger.warning(f"handle_deeplink_start received plain /start from user {user.id}.")
        return ConversationHandler.END

    payload = command_parts[1]
    logger.info(f"User {user.id} triggered /start with payload: {payload}")

    # Check if this payload is for webapp linking
    WEBAPP_LINK_PREFIX = "link_"
    if payload.startswith(WEBAPP_LINK_PREFIX):
        webapp_user_id = payload[len(WEBAPP_LINK_PREFIX):]
        logger.info(f"Attempting webapp linking for user {user.id} with webapp user ID: {webapp_user_id}") 

        processing_message = await message.reply_text(messages.MSG_WEBAPP_DEEPLINK_TRIGGERED, parse_mode='HTML')


        if webapp_user_id:
            user_manager.set_webapp_linked(user.id, webapp_user_id) # TODO: Check if this have a error
            logger.info(f"Webapp user ID {webapp_user_id} linked successfully for user {user.id}.")
            
            try:
                await processing_message.delete()
            except Exception as e:
                logger.warning(f"Failed to delete webapp processing message: {e}")
            
            await message.reply_text(messages.MSG_WEBAPP_LINK_SUCCESS, parse_mode='HTML')
            context.user_data['onboarding_in_progress'] = False
            context.user_data['onboarding_state'] = states.FINISHED
            return ConversationHandler.END
        else:
            # Webapp linking failed
            logger.warning(f"Webapp linking failed for user {user.id} with webapp user ID: {webapp_user_id}.")
            keyboard = [
                [InlineKeyboardButton(messages.BTN_SWITCH_TO_SHEET, callback_data='switch_to_sheet')],
                [InlineKeyboardButton(messages.BTN_CANCEL_ONBOARDING, callback_data='cancel_onboarding')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await message.reply_text(
                messages.MSG_WEBAPP_LINK_FAILED.format(webapp_base_url=config.WEBAPP_BASE_URL),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            context.user_data['onboarding_in_progress'] = True
            context.user_data['onboarding_state'] = states.WEBAPP_SHOWING_INSTRUCTIONS
            return states.WEBAPP_SHOWING_INSTRUCTIONS

    return ConversationHandler.END


# --- Fallback handler for ConversationHandler ---
async def onboarding_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles messages received during the onboarding conversation that don't match
    the specific handlers for the current state.
    """
    user = update.effective_user
    current_state = context.user_data.get('onboarding_state', 'Unknown') # Get current state name if possible

    logger.warning(f"User {user.id} sent unhandled message '{update.effective_message.text}' in onboarding state {current_state}.")
    
    if current_state == states.GOOGLE_SHEET_AWAITING_URL:
        await update.effective_message.reply_text(messages.MSG_SHEET_LINK_INVALID_URL, parse_mode='HTML')
        keyboard = [
                 [InlineKeyboardButton(messages.BTN_SWITCH_TO_WEBAPP, callback_data='switch_to_webapp')], # Option to switch
                 [InlineKeyboardButton(messages.BTN_CANCEL_ONBOARDING, callback_data='cancel_onboarding')] # Option to cancel
             ]
        await update.effective_message.reply_text(messages.MSG_WEBAPP_LINK_FAILED.format(webapp_base_url=config.WEBAPP_BASE_URL), parse_mode='HTML', disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(keyboard))
        return states.GOOGLE_SHEET_AWAITING_URL
    elif current_state == states.WEBAPP_SHOWING_INSTRUCTIONS:
        keyboard = [
            [InlineKeyboardButton(messages.BTN_SWITCH_TO_SHEET, callback_data='switch_to_sheet')], # Option to switch
            [InlineKeyboardButton(messages.BTN_CANCEL_ONBOARDING, callback_data='cancel_onboarding')] # Option to cancel
        ]
        await update.effective_message.reply_text(messages.MSG_WEBAPP_LINK_FAILED.format(webapp_base_url=config.WEBAPP_BASE_URL), parse_mode='HTML', disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(keyboard))
        return states.WEBAPP_SHOWING_INSTRUCTIONS
    
    elif current_state == states.CHOOSING_LINK_METHOD:
        keyboard = [
            [InlineKeyboardButton(messages.BTN_GOOGLE_SHEET, callback_data='link_sheet')],
            [InlineKeyboardButton(messages.BTN_WEBAPP, callback_data='link_webapp')]
        ]
        await update.effective_message.reply_text(messages.MSG_ONBOARDING_REQUIRED, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return states.CHOOSING_LINK_METHOD
    elif current_state == states.FINISHED:
        return ConversationHandler.END
    else:
        return ConversationHandler.END


async def cancel_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the cancellation of the onboarding process via callback query.
    """
    query = update.callback_query
    await query.answer("❌ Configuración cancelada")  # Show feedback
    
    # Clear any onboarding-related data
    context.user_data['onboarding_in_progress'] = False
    context.user_data['onboarding_state'] = states.FINISHED
    
    # Send message informing about cancellation and how to restart
    await query.message.reply_text(
        messages.MSG_CANCEL_ONBOARDING_CONFIRM,
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


# --- Conversation Handler Definition ---
# This handles the multi-step onboarding flow when initiated by a plain /start.
# Be careful with the order of the handlers and modifications. If you change something, please test all the flows.
onboarding_conv_handler = ConversationHandler(
    entry_points=[
        # Start the conversation via /start command (no payload)
        MessageHandler(filters.TEXT & filters.Regex(r'^/start$'), start_onboarding),
        
        # Start with payload (deep linking)
        MessageHandler(filters.TEXT & filters.Regex(r'^/start link_.*'), handle_deeplink_start),
        
        # Direct linking commands
        CommandHandler('linksheet', choose_sheet),
        CommandHandler('linkweb', choose_webapp),
        
        # Callback queries for direct linking
        CallbackQueryHandler(choose_sheet, pattern='^link_sheet$'),
        CallbackQueryHandler(choose_webapp, pattern='^link_webapp$'),
    ],
    states={
        states.CHOOSING_LINK_METHOD: [
            # Handle button clicks for choosing method
            CallbackQueryHandler(choose_sheet, pattern='^link_sheet$'),
            CallbackQueryHandler(choose_webapp, pattern='^link_webapp$'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, onboarding_fallback)
        ],
        states.GOOGLE_SHEET_AWAITING_URL: [
            # Handle text input (expecting URL)
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_sheet_url),
            CallbackQueryHandler(cancel_onboarding, pattern='^cancel_onboarding$'),
            CallbackQueryHandler(choose_sheet, pattern='^retry_sheet_url$'),
            CallbackQueryHandler(choose_webapp, pattern='^switch_to_webapp$'),
        ],
        states.WEBAPP_SHOWING_INSTRUCTIONS: [
            # Deep linking can interrupt any state
            MessageHandler(filters.TEXT & filters.Regex(r'^/start link_.*'), handle_deeplink_start),
            CallbackQueryHandler(cancel_onboarding, pattern='^cancel_onboarding$'),
            CallbackQueryHandler(choose_sheet, pattern='^switch_to_sheet$'),
            MessageHandler(filters.TEXT, onboarding_fallback)
        ]
    },
    fallbacks=[
        # Allow deep linking to interrupt any state
        MessageHandler(filters.TEXT & filters.Regex(r'^/start link_.*'), handle_deeplink_start),
        CommandHandler('cancel', cancel_onboarding),
        MessageHandler(filters.ALL, onboarding_fallback)
    ]
)