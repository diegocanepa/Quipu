"""
WhatsApp messages.
All messages are formatted for better presentation in WhatsApp.
"""

# Linking Messages
MSG_LINKING_INVALID = "❌ *Código de vinculación inválido*\n\nPor favor, verifica el código e intenta nuevamente 🔄"

MSG_LINKING_SUCCESS = (
    "✅ *¡Cuenta vinculada exitosamente!*\n\n"
    "Ahora puedes usar Quipu desde WhatsApp para:\n"
    "• Registrar tus gastos diarios 🛒\n"
    "• Mantener un registro de tus ingresos 💵\n"
    "• Y mucho más...\n\n"
    "¡Comienza a usar Quipu enviando un mensaje! 🚀"
)

MSG_LINKING_CODE_NOT_FOUND = (
    "❌ *No se pudo encontrar el código de vinculación*\n\n"
    "Por favor, asegúrate de incluir el código correctamente en el formato:\n"
    "_Mi código de vinculación es: XXXXX_ 📝"
)

# Welcome Message
MSG_WELCOME = (
    "👋 *¡Bienvenido/a a Quipu!*\n\n"
    "Para comenzar a usar Quipu, necesitas vincular tu cuenta.\n\n"
    "1. Ingresa a la plataforma web: {webapp_url}\n"
    "2. Ve a tu perfil\n"
    "3. Copia tu código de vinculación\n"
    "4. Envíalo aquí en este formato:\n"
    "_Mi código de vinculación es: XXXXX_\n\n"
    "¡Y listo! Comenzarás a disfrutar de todas las funcionalidades de Quipu 🚀"
)

# Error Messages
MSG_UNEXPECTED_ERROR = (
    "❌ *¡Ups! Algo salió mal*\n\n"
    "Por favor, intenta nuevamente en unos minutos.\n"
    "Si el problema persiste, contacta a soporte 📞"
)

# Voice Processing Messages
MSG_VOICE_NO_TEXT = "❌ *No pude entender el mensaje de voz*\n\nPor favor, intentá enviar el mensaje nuevamente o escribí el texto directamente 📝"
MSG_VOICE_PROCESSING_ERROR = "❌ *Hubo un error al procesar el mensaje de voz*\n\nPor favor, intentá nuevamente en unos minutos 🎙️"