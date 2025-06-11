import logging
from dataclasses import dataclass
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from api.telegram.middlewere.requiere_user import require_user
from core.models.user import User
from integrations.platforms.telegram_adapter import TelegramAdapter
from core.onboarding_manager import OnboardingManager

logger = logging.getLogger(__name__)

# Constants
CALLBACK_PATTERNS = {
    'LINK_SHEET': '^link_sheet$',
    'LINK_WEBAPP': '^link_webapp$',
    'CANCEL': '^cancel_onboarding$',
    'RETRY_SHEET': '^retry_sheet_url$',
    'SWITCH_TO_WEBAPP': '^switch_to_webapp$',
    'SWITCH_TO_SHEET': '^switch_to_sheet$'
}

COMMAND_PATTERNS = {
    'START': r'^/start$',
    'START_WITH_LINK': r'^/start link_.*'
}

@dataclass
class OnboardingState:
    """
    Data class to hold onboarding state information.
    
    This class represents the current state of a user's onboarding process,
    including whether they are actively in the process and what step they are on.
    
    Attributes:
        state (int): The current state of the onboarding process
        in_progress (bool): Whether the user is currently in the onboarding process
    """
    state: int
    in_progress: bool = True

class OnboardingStateManager:
    """
    Manages the onboarding state in the context.
    
    This class provides methods to get and set the onboarding state in the Telegram context.
    It ensures consistent state management across different handlers and provides
    a single source of truth for the onboarding state.
    
    Methods:
        set_state: Updates the onboarding state in the context
        get_state: Retrieves the current onboarding state from the context
    """
    
    def __init__(self, onboarding_manager: OnboardingManager):
        self.onboarding_manager = onboarding_manager
    
    def set_state(self, context: ContextTypes.DEFAULT_TYPE, state: int, in_progress: bool = True) -> None:
        """Sets the onboarding state in the context."""
        context.user_data['onboarding_state'] = state
        context.user_data['onboarding_in_progress'] = in_progress

    def get_state(self, context: ContextTypes.DEFAULT_TYPE) -> OnboardingState:
        """Gets the current onboarding state from the context."""
        return OnboardingState(
            state=context.user_data.get('onboarding_state', self.onboarding_manager.CHOOSING_LINK_METHOD),
            in_progress=context.user_data.get('onboarding_in_progress', True)
        )

class BaseOnboardingHandler:
    """
    Base class for onboarding handlers with common functionality.
    
    This class provides shared functionality for all onboarding handlers,
    including callback query handling and state management. It serves as a
    foundation for more specific handler classes.
    
    Attributes:
        onboarding_manager: Manages the core onboarding logic
        state_manager: Manages the onboarding state in the context
    """
    
    def __init__(self):
        self.onboarding_manager = OnboardingManager()
        self.state_manager = OnboardingStateManager(self.onboarding_manager)

    async def answer_callback_query(self, update: Update) -> None:
        """Answers a callback query if it exists."""
        if update.callback_query:
            await update.callback_query.answer()

    def _end_conversation(self, state: int) -> int:
        """Determines if the conversation should end based on the state."""
        return ConversationHandler.END if state == self.onboarding_manager.END else state

class StartHandler(BaseOnboardingHandler):
    """
    Handles the start of the onboarding process.
    
    This class manages the initial steps of the onboarding process, including:
    - Regular start command handling
    - Deep link handling for webapp integration
    
    It's responsible for initiating the onboarding flow and setting up the
    initial state for new users.
    """
    @require_user
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles the /start command without a payload."""
        user = context.user_data['current_user']
        platform = TelegramAdapter(update, user)
        state = await self.onboarding_manager.start_onboarding(platform)
        self.state_manager.set_state(context, state)
        return self._end_conversation(state)

    async def handle_deeplink_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles webapp deep linking."""
        platform = TelegramAdapter(update)
        state = await self.onboarding_manager.handle_webapp_deeplink(platform)
        self.state_manager.set_state(context, state, state != self.onboarding_manager.END)
        return self._end_conversation(state)

class SheetHandler(BaseOnboardingHandler):
    """
    Handles Google Sheet related onboarding steps.
    
    This class manages all interactions related to Google Sheet integration during onboarding,
    including:
    - Initial sheet choice
    - Sheet URL validation and processing
    - Sheet access verification
    
    It guides users through the process of linking their Google Sheet to the bot.
    """

    @require_user
    async def handle_sheet_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles the user choosing Google Sheet linking."""
        user = context.user_data['current_user']
        platform = TelegramAdapter(update, user)
        await self.answer_callback_query(update)
        state = await self.onboarding_manager.handle_sheet_choice(platform)
        self.state_manager.set_state(context, state)
        return self._end_conversation(state)

    @require_user
    async def handle_sheet_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles the user sending a sheet URL."""
        user = context.user_data['current_user']
        platform = TelegramAdapter(update, user)
        state = await self.onboarding_manager.handle_sheet_url(platform)
        self.state_manager.set_state(context, state)
        return self._end_conversation(state)

class WebappHandler(BaseOnboardingHandler):
    """
    Handles Webapp related onboarding steps.
    
    This class manages the webapp integration process during onboarding,
    including:
    - Initial webapp choice
    - Webapp linking instructions
    - Deep link processing
    
    It guides users through the process of linking their webapp account to the bot.
    """
    @require_user
    async def handle_webapp_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles the user choosing Webapp linking."""
        user = context.user_data['current_user']
        platform = TelegramAdapter(update, user)
        await self.answer_callback_query(update)
        state = await self.onboarding_manager.handle_webapp_choice(platform)
        self.state_manager.set_state(context, state)
        return self._end_conversation(state)

class GeneralHandler(BaseOnboardingHandler):
    """
    Handles general onboarding operations.
    
    This class manages common operations that can occur during any stage of onboarding,
    including:
    - Cancellation of the onboarding process
    - Handling of unrecognized messages
    - Fallback behavior
    
    It provides a safety net for handling unexpected user inputs and graceful
    process termination.
    """
    @require_user
    async def handle_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles onboarding cancellation."""
        user = context.user_data['current_user']
        platform = TelegramAdapter(update, user)
        await self.answer_callback_query(update)
        state = await self.onboarding_manager.handle_cancel(platform)
        self.state_manager.set_state(context, state, False)
        return self._end_conversation(state)

    @require_user
    async def handle_fallback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles unrecognized messages during onboarding."""
        user = context.user_data['current_user']
        platform = TelegramAdapter(update, user)
        current_state = self.state_manager.get_state(context).state
        state = await self.onboarding_manager.handle_fallback(platform, current_state)
        self.state_manager.set_state(context, state, state != self.onboarding_manager.END)
        return self._end_conversation(state)

# Initialize handlers
start_handler = StartHandler()
sheet_handler = SheetHandler()
webapp_handler = WebappHandler()
general_handler = GeneralHandler()

# --- Conversation Handler Definition ---
onboarding_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.TEXT & filters.Regex(COMMAND_PATTERNS['START']), start_handler.handle_start),
        MessageHandler(filters.TEXT & filters.Regex(COMMAND_PATTERNS['START_WITH_LINK']), start_handler.handle_deeplink_start),
        CommandHandler('linksheet', sheet_handler.handle_sheet_choice),
        CommandHandler('linkweb', webapp_handler.handle_webapp_choice),
        CallbackQueryHandler(sheet_handler.handle_sheet_choice, pattern=CALLBACK_PATTERNS['LINK_SHEET']),
        CallbackQueryHandler(webapp_handler.handle_webapp_choice, pattern=CALLBACK_PATTERNS['LINK_WEBAPP']),
    ],
    states={
        start_handler.onboarding_manager.CHOOSING_LINK_METHOD: [
            CallbackQueryHandler(sheet_handler.handle_sheet_choice, pattern=CALLBACK_PATTERNS['LINK_SHEET']),
            CallbackQueryHandler(webapp_handler.handle_webapp_choice, pattern=CALLBACK_PATTERNS['LINK_WEBAPP']),
            CallbackQueryHandler(general_handler.handle_cancel, pattern=CALLBACK_PATTERNS['CANCEL']),
            MessageHandler(filters.TEXT & ~filters.COMMAND, general_handler.handle_fallback)
        ],
        start_handler.onboarding_manager.GOOGLE_SHEET_AWAITING_URL: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, sheet_handler.handle_sheet_url),
            CallbackQueryHandler(general_handler.handle_cancel, pattern=CALLBACK_PATTERNS['CANCEL']),
            CallbackQueryHandler(sheet_handler.handle_sheet_choice, pattern=CALLBACK_PATTERNS['RETRY_SHEET']),
            CallbackQueryHandler(webapp_handler.handle_webapp_choice, pattern=CALLBACK_PATTERNS['SWITCH_TO_WEBAPP']),
        ],
        start_handler.onboarding_manager.WEBAPP_SHOWING_INSTRUCTIONS: [
            MessageHandler(filters.TEXT & filters.Regex(COMMAND_PATTERNS['START_WITH_LINK']), start_handler.handle_deeplink_start),
            CallbackQueryHandler(general_handler.handle_cancel, pattern=CALLBACK_PATTERNS['CANCEL']),
            CallbackQueryHandler(sheet_handler.handle_sheet_choice, pattern=CALLBACK_PATTERNS['SWITCH_TO_SHEET']),
            MessageHandler(filters.TEXT, general_handler.handle_fallback)
        ]
    },
    fallbacks=[
        MessageHandler(filters.TEXT & filters.Regex(COMMAND_PATTERNS['START_WITH_LINK']), start_handler.handle_deeplink_start),
        CommandHandler('cancel', general_handler.handle_cancel),
        MessageHandler(filters.ALL, general_handler.handle_fallback)
    ]
)