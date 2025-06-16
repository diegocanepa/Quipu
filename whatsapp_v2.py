import os
import json
import logging
from flask import Flask, jsonify, request
from pywa_async import WhatsApp, handlers, types
from api.whatsapp_v2.handlers_registry import WhatsAppV2Handlers
from config import config
import uvicorn
from asgiref.wsgi import WsgiToAsgi

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
# Obtener logger para este módulo
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize WhatsApp client
wa = WhatsApp(
    phone_id=config.WHATSAPP_PHONE_ID,
    token=config.WHATSAPP_TOKEN,
    server=app,  
    verify_token=config.WHATSAPP_VERIFY_TOKEN, 
    app_id=config.WHATSAPP_APP_ID,
    app_secret=config.WHATSAPP_APP_SECRET,
    webhook_endpoint="/webhook",
)

# Initialize handlers
my_handlers = WhatsAppV2Handlers(wa)
my_handlers.register_handlers()

@app.route('/')
def home():
    logger.info("Home endpoint accessed")
    return 'WhatsApp Bot is running!'

# Convertir la app Flask a ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    uvicorn.run(
        "main:asgi_app",  # Usar string de importación
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG
    )