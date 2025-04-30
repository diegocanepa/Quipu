import logging
from typing import List
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from core.llm_processor import LLMProcessor, ProcessingResult
from core.data_server import DataSaver
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

llm_processor = LLMProcessor()
data_saver = DataSaver()

# Variable set to know the stage of the conversation
CONFIRM_SAVE = 1

async def proccess_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """    
    Handles incoming messages from Telegram users, processes them using the LLMProcessor,
    and sends a separate response back to the user for each processed result.
    """
    
    user_message = update.message.text
    logger.info(f"Received message from user {update.effective_user.id}: {user_message}")

    results: List[ProcessingResult] = await llm_processor.process_content(user_message)

    if not results:
        await update.message.reply_text("❌ Hubo un error inesperado durante el procesamiento.", parse_mode='MarkdownV2')
        return
    
    for result in results:
        if result.error:
            response_text = f"❌ {result.error}"
            await update.message.reply_text(response_text, parse_mode='MarkdownV2')
        else:
            response_text = result.data_object.to_formatted_string()
                    
            # Create confirmation buttons
            keyboard = [
                [InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_{update.message.message_id}")],
                [InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{update.message.message_id}")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
                
            await update.message.reply_text(response_text, parse_mode='MarkdownV2', reply_markup=reply_markup)
            context.user_data['pending_save'] = result.data_object
            context.user_data['original_message_id'] = update.message.message_id
            return CONFIRM_SAVE

async def confirm_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback query handler para el botón de confirmar. Guarda los datos."""
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback Query Data (Confirm): {query.data}")

    if query.data.startswith("confirm_"):
        original_message_id = int(query.data.split("_")[1])
        if context.user_data.get('original_message_id') == original_message_id and 'pending_save' in context.user_data:
            data_to_save = context.user_data['pending_save']
            
            logger.info(f"Mensaje a guardar: {data_to_save}")
            logger.info(f"Mensaje original: {original_message_id}")

            success = await data_saver.save_content(data_to_save)
            original_text = query.message.text

            if success:
                await query.edit_message_text(text=f"{original_text}\n\n✅ Guardado correctamente")
            else:
                await query.edit_message_text(text=f"{original_text}\n\n❌ Error al guardar")
        else:
            await query.edit_message_text(text="❌ La confirmación ha expirado.")

        context.user_data.clear() 
        return ConversationHandler.END
    return ConversationHandler.END

async def cancel_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
    """Callback query handler para el botón de cancelar."""
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback Query Data (Cancel): {query.data}")
    await query.edit_message_text(text="❌ Acción cancelada.")
    context.user_data.clear()
    return ConversationHandler.END