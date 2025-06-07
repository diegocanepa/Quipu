import logging
from telegram import Update
from telegram.ext import ContextTypes

from core import messages
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from core.user_data_manager import UserDataManager
from integrations.platforms.telegram_adapter import TelegramAdapter

from config import config

logger = logging.getLogger(__name__)

# Initialize managers
user_manager = UserDataManager()
spreadsheet_manager = SpreadsheetManager()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /help command. Displays the help message."""
    platform = TelegramAdapter(update)
    await platform.reply_text(messages.MSG_HELP_TEXT)
     
async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /info command. Shows the user's current linking status."""
    platform = TelegramAdapter(update)
    user_id = platform.get_user_id()
    status = user_manager.get_user_linking_status(user_id)

    # Prepare status and links
    has_sheet = status.get('sheet_id')
    has_webapp = status.get('webapp_user_id')
    
    # Prepare links if services are connected
    sheet_link = spreadsheet_manager.get_sheet_url(status.get('sheet_id')) if has_sheet else ""
    webapp_link = config.WEBAPP_BASE_URL

    # Prepare status messages
    sheet_status = messages.STATUS_LINKED.format(url_link=sheet_link) if has_sheet else messages.STATUS_NOT_LINKED
    webapp_status = messages.STATUS_LINKED.format(url_link=webapp_link) if has_webapp else messages.STATUS_NOT_LINKED
    
    # Prepare info message
    info_message = messages.MSG_INFO_STATUS.format(sheet_status=sheet_status, webapp_status=webapp_status)

    if not user_manager.is_onboarding_complete(user_id):
        info_message += messages.MSG_INFO_NOT_LINKED_ACTIONS
    else:
        info_message += messages.MSG_INFO_LINKED_ACTIONS

        # Add commands to link the other method if not already linked
        if not has_sheet or not has_webapp:
            info_message += messages.MSG_INFO_LINK_OTHER_METHOD
            if not has_sheet:
                info_message += "\n" + messages.MSG_INFO_LINK_SHEET_CMD
            if not has_webapp:
                info_message += "\n" + messages.MSG_INFO_LINK_WEBAPP_CMD

    await platform.reply_text(info_message, disable_web_page_preview=True)

async def handle_unrecognized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles messages/commands that don't match any specific handler."""
    platform = TelegramAdapter(update)
    user_id = platform.get_user_id()
    text = platform.get_message_text()

    # IMPORTANT: Check if the user is currently in the onboarding conversation
    # The ConversationHandler's fallback might already handle this.
    # If you want this handler to run *only* outside conversations and for onboarded users:
    if context.user_data.get('onboarding_in_progress'):
        # If onboarding conversation is active, let its fallback handle it
        logger.debug(f"User {user_id} sent unrecognized message '{text}', but in onboarding conversation. Letting conv handler fallback.")
        # Returning here allows the ConversationHandler's MessageHandler(filters.ALL, onboarding_fallback) to catch it.
        return
    else:
        # User is not in onboarding conversation. Check if they are onboarded.
        if not user_manager.is_onboarding_complete(user_id):
            logger.info(f"User {user_id} sent unrecognized message '{text}' and is not onboarded. Prompting setup.")
            await platform.reply_text(
                messages.MSG_ONBOARDING_REQUIRED + "\n\n Use /start para comenzar! ✨"
            )
        else:
            logger.info(f"User {user_id} sent unrecognized message '{text}' and IS onboarded. Providing general help.")
            # User is onboarded but sent something the bot doesn't recognize as a command or data entry format
            if text.startswith('/'):
                await platform.reply_text(messages.MSG_UNKNOWN_COMMAND)
            else:
                # Assume it's potentially a data entry attempt that failed parsing
                await platform.reply_text(messages.MSG_UNKNOWN_MESSAGE)