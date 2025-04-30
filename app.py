# app.py
import logging
import asyncio
from flask import Flask, Response, request, make_response
from asgiref.wsgi import WsgiToAsgi
import uvicorn
from http import HTTPStatus
from telegram import Update
from api.bot import register_handlers, get_application, setup_webhook

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
application = get_application()  # Obtener la instancia de la aplicación
register_handlers(application)  # Pasar la instancia a register_handlers()

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
    """Simple health check"""
    return make_response("Bot is running", HTTPStatus.OK)

async def main():
    await setup_webhook()
    server = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(app),
            port=8080,
            host="0.0.0.0",
            use_colors=True,
        )
    )

    async with application:
        await application.start()
        await server.serve()
        await application.stop()

if __name__ == '__main__':
    asyncio.run(main())