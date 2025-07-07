from logging_config import get_logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from api.telegram.middlewere.require_onboarding import require_onboarding
from core import messages
from integrations.spreadsheet.spreadsheet import SpreadsheetManager
from core.user_data_manager import UserDataManager

from config import config

logger = get_logger(__name__)

class CommandHandlers:
    def __init__(self):
        self.user_manager = UserDataManager()
        self.spreadsheet_manager = SpreadsheetManager()

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler for /help command. Displays the help message."""
        await update.effective_message.reply_text(messages.MSG_HELP_TEXT, parse_mode='HTML')

    @require_onboarding
    async def show_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /info command. Shows the user's current linking status."""
        user_id = context.user_data.get('current_user').id
        status = self.user_manager.get_user_linking_status(user_id)

        # Prepare status and links
        has_sheet = status.get('sheet_id')
        has_webapp = status.get('webapp_user_id')
        
        # Prepare links if services are connected
        sheet_link = self.spreadsheet_manager.get_sheet_url(status.get('sheet_id')) if has_sheet else ""
        webapp_link = config.WEBAPP_BASE_URL

        # Prepare status messages
        sheet_status = messages.STATUS_LINKED.format(url_link=sheet_link) if has_sheet else messages.STATUS_NOT_LINKED
        webapp_status = messages.STATUS_LINKED.format(url_link=webapp_link) if has_webapp else messages.STATUS_NOT_LINKED
        
        # Prepare info message
        info_message = messages.MSG_INFO_STATUS.format(sheet_status=sheet_status, webapp_status=webapp_status)

        if not self.user_manager.is_onboarding_complete(user_id):
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

        await update.effective_message.reply_text(info_message, parse_mode='HTML', disable_web_page_preview=True)

    async def handle_unrecognized(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles messages/commands that don't match any specific handler."""
        telegram_user_id = update.effective_user.id
        
        try: 
            user = self.user_manager.get_user_by_telegram_user_id(telegram_user_id=telegram_user_id)
            if not user:
                logger.info(f"User do not exists yet: {telegram_user_id}")
                await update.effective_message.reply_text(messages.MSG_WEBAPP_NOT_REGISTERED_HTML.format(webapp_signup_url=config.WEBAPP_BASE_URL), parse_mode='HTML')
                return
            
            # Check if user is onboarded
            if self.user_manager.is_onboarding_complete(user.id):
                logger.debug(f"User {user.id} is onboarded")
                await update.effective_message.reply_text(messages.UNEXPECTED_ERROR)
            else:
                logger.info(f"User {telegram_user_id} is NOT onboarded.")
                
                keyboard = [
                    [InlineKeyboardButton(messages.BTN_GOOGLE_SHEET, callback_data='link_sheet')],
                    [InlineKeyboardButton(messages.BTN_WEBAPP, callback_data='link_webapp')]
                ]
                await update.effective_message.reply_text(
                    messages.MSG_ONBOARDING_REQUIRED, 
                    parse_mode='HTML', 
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return
        except Exception as e:
            logger.error(f"Error in require_onboarding middleware: {str(e)}")
            await update.effective_message.reply_text(messages.UNEXPECTED_ERROR)
            return

# Instancia para usar en el registro de handlers
command_handlers = CommandHandlers()