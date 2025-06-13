"""
Onboarding messages.
All messages are formatted in HTML for better presentation.
"""

MSG_WELCOME = (
    "¡Hola! 👋 Bienvenido/a a Quipu, tu copiloto financiero personal. Me alegra tenerte aquí "
    "y estoy listo para ayudarte a tomar el control de tus finanzas. 💰\n\n"
    "¿Qué podemos hacer juntos?\n"
    "• Registrar tus <b>gastos diarios</b> de forma sencilla 🛒\n"
    "• Mantener un registro de tus <b>ingresos</b> 💵\n"
    "Pronto tendremos más herramientas emocionantes:\n\n"
    "• Dar seguimiento a tus <b>cambios de divisas</b> favoritos 💱\n"
    "• Seguimiento de <b>inversiones</b> 📈\n"
    "• Planificación de <b>ahorros</b> 🏦\n"
    "• Y muchas sorpresas más...\n\n"
    "Mi objetivo es hacer que manejar tus finanzas sea fácil y hasta divertido. "
    "¡Estoy aquí para ayudarte a alcanzar tus metas financieras! 🎯\n\n"
    "¿Comenzamos esta aventura juntos? 😊"
)

MSG_WELCOME_BACK = (
    "¡Hola de nuevo! 👋\n"
    "Usa /info para ver tu estado o /help para ver los comandos disponibles."
)

MSG_PRESENT_OPTIONS = (
    "Para empezar, necesito que elijas cómo guardar tus datos para tenerlos siempre a mano:\n\n"
    "1️⃣ <b>Google Sheet</b>\n"
    "• Guarda todo en tu Drive\n"
    "• Formato visual y familiar\n\n"
    "2️⃣ <b>Cuenta Web</b>\n"
    "• Interfaz web moderna\n"
    "• Más funciones disponibles\n\n"
    "¿Cuál preferís? 👇"
)

# Google Sheet linking messages
MSG_SHEET_CHOICE_CONFIRM = (
    "¡Excelente elección! ✅\n"
    "Vamos a configurar tu Google Sheet."
)

MSG_SHEET_STEP_1_COPY = (
    "<b>Paso 1: Copia la plantilla</b>\n\n"
    "1. Abre este enlace ➡️ <a href=\"{template_url}\">Plantilla Google Sheet</a>\n"
    "2. Ve a \"<i>Archivo → Hacer una copia</i>\"\n"
    "3. Nombra tu hoja (ej: \"Mis Finanzas\")\n"
    "4. Guárdala en tu Drive"
)

MSG_SHEET_STEP_2_SHARE = (
    "<b>Paso 2: Comparte la hoja</b>\n\n"
    "1. Abre <i>tu copia</i> de la hoja\n"
    "2. Clic en \"<b>Compartir</b>\" (arriba a la derecha)\n"
    "3. Agrega este email como <b>Editor</b>:\n"
    "<code>{sa_email}</code>\n\n"
    "Luego, envíame el <b>enlace</b> de tu hoja 👇"
)

MSG_SHEET_LINK_CHECKING = (
    "Verificando el acceso a tu Google Sheet... Por favor espera. 🔄"
)

MSG_SHEET_AWAITING_URL = (
    "Envíame el enlace de tu Google Sheet para continuar 👇"
)
MSG_SHEET_CHECKING_ACCESS = (
    "Verificando el acceso a tu Google Sheet... Por favor espera. 🤔"
)
MSG_SHEET_LINK_SUCCESS = (
    "¡Perfecto! 🎉\n"
    "Tu Google Sheet está vinculada y lista para usar.\n\n"
    "<i>Ejemplos de uso:</i>\n"
    "• <code>gasto 500 cafe</code>\n"
    "• <code>ingreso 1000 sueldo</code>\n\n"
    "Usa /help para ver más comandos."
)

MSG_SHEET_LINK_FAILED_ACCESS = (
    "❌ No pude acceder a tu hoja.\n\n"
    "Verifica que:\n"
    "• Compartiste con: <code>{sa_email}</code>\n"
    "• El permiso es \"<b>Editor</b>\"\n"
    "• El enlace es correcto\n\n"
    "¿Intentamos de nuevo? Compartime el enlace de tu hoja!"
)

MSG_SHEET_LINK_INVALID_URL = (
    "❌ El enlace no parece ser válido.\n"
    "Debe comenzar con: <code>https://docs.google.com/spreadsheets/...</code>"
)

MSG_SHEET_ALREADY_LINKED = (
    "¡Tu Google Sheet ya está vinculada! ✅\n"
    "Usa /info para ver tu estado."
)

MSG_WEBAPP_ALREADY_LINKED = (
    "¡Tu cuenta web ya está vinculada a través de la web! ✅\n"
    "Mirá tus datos haciendo click <a href=\"{url_link}\">acá</a> 📊\n\n"
    "<i>Para más información sobre tu cuenta usá /info</i> 💫"
)

# Webapp linking messages
MSG_WEBAPP_CHOICE_CONFIRM = (
    "¡Excelente elección! ✅\n"
    "Vamos a vincular tu cuenta web."
)

MSG_WEBAPP_STEPS = (
    "<b>Sigue estos pasos:</b>\n\n"
    "1. Ingresa aquí:\n"
    "<a href=\"{webapp_base_url}\">🌐 Plataforma Web</a>\n\n"
    "2. En tu perfil, busca \"<b>Vincular con Telegram</b>\"\n\n"
    "3. Haz clic y confirma la vinculación ✨"
)

MSG_WEBAPP_LINK_REMINDER = (
    "Haz clic en '<b>Vincular con Telegram</b>' en la web para completar el proceso 🔗"
)

MSG_WEBAPP_LINK_SUCCESS = (
    "¡Vinculación exitosa! 🎉\n\n"
    "<i>Ejemplos de uso:</i>\n"
    "• <code>gasto 500 cafe</code>\n"
    "• <code>ingreso 1000 sueldo</code>\n\n"
    "Usa /help para ver más comandos."
)

MSG_WEBAPP_LINK_FAILED = (
    "❌ La vinculación con la aplicación web no se pudo completar.\n\n"
    "Puedes:\n"
    "• Seguí los pasos de nuevo e intenta nuevamente desde la <a href=\"{webapp_base_url}\">web</a>\n"
    "• Cambiar a Google Sheets\n"
    "• Cancelar la configuración"
)

MSG_WEBAPP_DEEPLINK_TRIGGERED = (
    "Procesando tu solicitud de vinculación... 🔄"
)

MSG_ONBOARDING_REQUIRED = (
    "¡Hola! 👋\n\n"
    "Para poder utilizar todas las funcionalidades del bot, necesitas vincular "
    "una opción de almacenamiento de datos.\n\n"
    "<b>¿Por qué es necesario?</b>\n"
    "• Para guardar tus registros de forma segura 🔒\n"
    "• Para que puedas acceder a tus datos en cualquier momento 📱\n"
    "• Para brindarte un mejor servicio personalizado ✨\n\n"
    "<b>Opciones disponibles:</b>\n"
    "1️⃣ <b>Google Sheet</b> - Para amantes de las hojas de cálculo\n"
    "2️⃣ <b>Cuenta Web</b> - Para una experiencia más moderna\n\n"
    "¿Cuál preferís? 👇"
)

MSG_INFO_STATUS = (
    "<b>Estado de tu cuenta:</b>\n\n"
    "📊 Google Sheet: {sheet_status}\n"
    "🌐 Cuenta Web: {webapp_status}\n"
)

STATUS_LINKED = (
    "✅ Vinculado <a href=\"{url_link}\">(ver datos)</a>"
)
STATUS_NOT_LINKED = (
    "❌ No vinculado"
)

MSG_INFO_NOT_LINKED_ACTIONS = (
    "\n¡Hey! 👋 Parece que aún no has completado el proceso de bienvenida.\n\n"
    "Para comenzar a usar todas las funciones:\n"
    "👉 Escribe /start y configura tu cuenta en unos simples pasos"
)

MSG_INFO_LINKED_ACTIONS = (
    "\n<b>¡Todo listo! Tu cuenta está configurada</b> ✨\n"
    "Podés empezar a registrar tus movimientos así:\n\n"
    "<b>📝 Ejemplos rápidos:</b>\n"
    "• <code>gasto 500 cafe</code> ☕️\n"
    "• <code>ingreso 1000 sueldo</code> 💰\n\n"
    "¡Es así de simple! ¿Qué te gustaría registrar primero? 🚀"
)

MSG_INFO_LINK_OTHER_METHOD = (
    "\n\n<b>¿Querés vincular otro método?</b>"
)

MSG_INFO_LINK_SHEET_CMD = "• /linksheet para Google Sheet"
MSG_INFO_LINK_WEBAPP_CMD = "• /linkweb para Cuenta Web"

MSG_HELP_TEXT = (
    "<b>Soy tu bot financiero personal. Acá te dejo los comandos disponibles:</b>\n\n"
    "• /start – Iniciar configuración\n"
    "• /info – Ver estado de cuenta\n"
    "• /linksheet – Vincular Google Sheet\n"
    "• /linkweb – Vincular Cuenta Web\n"
    "• /help – Ver esta ayuda\n\n"
    "<i>Para registrar movimientos, escribe:</i>\n"
    "<code>gasto 100 cafe</code> o <code>ingreso 500 sueldo</code>"
)

MSG_CANCEL_ONBOARDING = (
    "Configuración cancelada.\n"
    "Usa /start cuando quieras continuar 👋"
)

MSG_UNKNOWN_COMMAND = (
    "No reconozco ese comando.\n"
    "Usa /help para ver las opciones disponibles."
)

MSG_UNKNOWN_MESSAGE = (
    "Hmm, no entendí lo que querés hacer. Asegurate de usar el comando correcto y seguí las instrucciones. Si no sabés cómo hacerlo, podés usar /help para ver las opciones disponibles."
)

MSG_CANCEL_ONBOARDING_CONFIRM = (
    "✖️ Proceso de configuración cancelado.\n\n"
    "Si querés volver a comenzar la configuración en cualquier momento, "
    "simplemente envía el comando /start."
)

MSG_ONBOARDING_ERROR = (
    "❌ Ups! Ocurrió un error durante el proceso de configuración.\n\n"
    "<b>¿Qué podés hacer?</b>\n"
    "• Intentar nuevamente desde el principio\n"
    "• Elegir otro método de vinculación\n"
    "👉 Usa /start para reiniciar el proceso"
)

# Pop up answers / messages
GOOGLE_SHEET_SELECTED = "✅ Google Sheet seleccionado"
WEBAPP_SELECTED = "✅ Cuenta Web seleccionada"
CANCEL_ONBOARDING_ANSWER = "❌ Configuración cancelada"

# Button Texts
BTN_GOOGLE_SHEET = "📊 Vincular Google Sheet"
BTN_WEBAPP = "🌐 Vincular Cuenta Web"
BTN_SWITCH_TO_WEBAPP = "🌐 Usar Cuenta Web"
BTN_RETRY = "🔄 Reintentar vinculación"
BTN_SWITCH_TO_SHEET = "📊 Usar Google Sheet"
BTN_CANCEL_ONBOARDING = "❌ Cancelar"


"""
General messages used across the application.
All messages are formatted in HTML for better presentation.
"""

# Error messages
UNEXPECTED_ERROR = "❌ Hubo un error inesperado durante el procesamiento."
MESSAGE_NOT_FOUND = "❌ No se encontró el mensaje original."
USER_NOT_FOUND = "❌ Ocurrió un error inesperado al buscar el usuario."
SAVE_ERROR = "❌ Error al guardar"
CANCEL_MESSAGE = "❌ Acción cancelada."

# Success messages
SAVE_SUCCESS = "✅ Guardado correctamente"

# Button texts
CONFIRM_BUTTON = "✅ Confirmar"
CANCEL_BUTTON = "❌ Cancelar"

MSG_WEBAPP_NOT_REGISTERED_HTML = (
    "🚫 <b>¡Aún no creaste una cuenta en nuestra página web!</b>\n\n"
    "Para comenzar a utilizar la plataforma web, primero necesitás crear tu cuenta.\n\n"
    "<b>🧾 Pasos:</b>\n"
    "1. Ingresá aquí ➡️ <a href=\"{webapp_signup_url}\">Crear cuenta en Quipu</a>\n"
    "2. Completá el registro en pocos segundos\n"
    "3. Desde tu perfil, hacé clic en \"<b>Vincular con Telegram</b>\" para conectar tu cuenta\n\n"
    "Una vez vinculada, vas a poder gestionar tus finanzas fácilmente desde Telegram 📱✨"
)

# Voice Processing Messages
MSG_VOICE_NO_TEXT = "❌ <b>No pude entender el mensaje de voz</b>\n\nPor favor, intentá enviar el mensaje nuevamente o escribí el texto directamente 📝"
MSG_VOICE_PROCESSING_ERROR = "❌ <b>Hubo un error al procesar el mensaje de voz</b>\n\nPor favor, intentá nuevamente en unos minutos 🎙️"
