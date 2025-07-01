# app.py
import argparse
import sys
import logging
import asyncio
from pathlib import Path
from flask import Blueprint, Response, request, make_response
from asgiref.wsgi import WsgiToAsgi
import uvicorn
from http import HTTPStatus
from telegram import Update
from api.telegram.bot import register_handlers, get_application, setup_webhook

def get_version():
    """Get version from version.txt file"""
    try:
        version_file = Path(__file__).parent / "version.txt"
        if version_file.exists():
            return version_file.read_text().strip()
        return "development"
    except Exception:
        return "unknown"

logger = logging.getLogger(__name__)

# Initialize Blueprint and Telegram application
app = Blueprint('telegram', __name__)
application = get_application()
register_handlers(application)

logger.info(f"Starting Quipu Telegram version {get_version()}")

async def process_updates():
    while True:
        logger.info("Running update process")
        try:
            update = await application.update_queue.get()
            logger.info(f"Procesando actualización: {update}")
            await application.process_update(update)
        finally:
            application.update_queue.task_done()
        await asyncio.sleep(0.1)  # Pequeña pausa para no consumir CPU al 100%

@app.post("/webhook")
async def telegram_webhook() -> Response:
    logger.info("Recibiendo petición POST en /telegram/webhook")
    logger.info(f"Headers de la petición: {request.headers}")
    logger.info(f"Cuerpo de la petición: {request.get_data(as_text=True)}")
    logger.info(f"App: {application}")
    try:
        update = Update.de_json(data=request.json, bot=application.bot)
        await application.update_queue.put(update)
        return Response(status=HTTPStatus.OK)
    except Exception as e:
        logger.error(f"Error al procesar la actualización: {e}")
        return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint with version info"""
    version = get_version()
    status = {
        "status": "healthycheck",
        "service": "quipu-telegram",
        "version": version,
        "timestamp": asyncio.get_event_loop().time()
    }
    return make_response(status, HTTPStatus.OK)

@app.get("/version")
async def version_endpoint():
    """Version endpoint"""
    return make_response({"version": get_version()}, HTTPStatus.OK)

async def initialize_telegram(debug: bool = False):
    """Initialize Telegram service"""
    await setup_webhook()
    await application.initialize()
    await application.start()
    asyncio.create_task(process_updates())

def main_cli():
    """CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(description='Quipu Telegram Bot')
    parser.add_argument('--version', action='version',
                       version=f'Quipu {get_version()}')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')

    args = parser.parse_args()
    asyncio.run(initialize_telegram(args.debug))

if __name__ == '__main__':
    main_cli()
