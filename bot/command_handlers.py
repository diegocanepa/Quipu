import logging
from telegram import ForceReply, Update
from telegram.ext import ContextTypes


logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hola {user.mention_html()}! Soy FinMate y te ayudare a administrar tus finanzas de manera rapida y sencilla.",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Aun no tengo desarollado el comando /help")
    
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs the error and sends a user-friendly message."""
    logger.error(f"Exception while handling an update {update}:", exc_info=context.error)

    try:
        if update.effective_chat:
            await update.effective_chat.send_message(
                "¡Ups! 🤖 Parece que ocurrió un error al procesar tu mensaje. Por favor, inténtalo de nuevo más tarde. Si el problema persiste, contacta al administrador.",
                quote=True
            )
        else:
            logger.warning("Could not send error message to user as effective_chat is None.")
    except Exception as e:
        logger.error(f"Could not send error message to user: {e}")