# app.py
import argparse
import sys
import logging
import asyncio
from pathlib import Path
from flask import Flask, Response, request, make_response
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

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

setup_logging()
logger = logging.getLogger(__name__)

# Initialize Flask app and Telegram application
app = Flask(__name__)
application = get_application()
register_handlers(application)

logger.info(f"Starting Quipu version {get_version()}")

async def process_updates():
    async with application:
        await application.start()
        while True:
            logger.info("Running update process")
            try:
                update = await application.update_queue.get()
                logger.info(f"Procesando actualización: {update}")
                await application.process_update(update)
            finally:
                application.update_queue.task_done()
            await asyncio.sleep(0.1)  # Pequeña pausa para no consumir CPU al 100%

@app.post("/telegram")
async def telegram_webhook() -> Response:
    logger.info("Recibiendo petición POST en /telegram")
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
        "status": "healthy",
        "service": "quipu",
        "version": version,
        "timestamp": asyncio.get_event_loop().time()
    }
    return make_response(status, HTTPStatus.OK)

@app.get("/version")
async def version_endpoint():
    """Version endpoint"""
    return make_response({"version": get_version()}, HTTPStatus.OK)

async def main():
    await setup_webhook()
    server = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(app),
            port=8080,
            host="0.0.0.0",
            use_colors=True,
            log_level="debug",
            reload=True
        )
    )

    async with application:
        asyncio.create_task(process_updates())  # Iniciar el consumidor de la cola en segundo plano
        await application.start()
        await server.serve()
        await application.stop()

def main_cli():
    """CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(description='Quipu Multi-Service Financial Bot')
    parser.add_argument('--version', action='version',
                       version=f'Quipu {get_version()}')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port to run the server on (default: 8080)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind to (default: 0.0.0.0)')

    args = parser.parse_args()

    # Update uvicorn config with CLI args
    global main
    original_main = main

    async def main_with_args():
        await setup_webhook()
        server = uvicorn.Server(
            config=uvicorn.Config(
                app=WsgiToAsgi(app),
                port=args.port,
                host=args.host,
                use_colors=True,
                log_level="info",
                reload=False
            )
        )

        async with application:
            asyncio.create_task(process_updates())
            await application.start()
            await server.serve()
            await application.stop()

    asyncio.run(main_with_args())

if __name__ == '__main__':
    main_cli()
