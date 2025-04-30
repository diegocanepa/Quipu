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

flask_app = Flask(__name__)
application = get_application()
register_handlers()

@flask_app.post("/telegram")
async def telegram_webhook() -> Response:
    """Receive updates from Telegram and queue them"""
    update = Update.de_json(data=request.json, bot=application.bot)
    await application.update_queue.put(update)
    return Response(status=HTTPStatus.OK)

@flask_app.get("/healthcheck")
async def healthcheck():
    """Simple health check"""
    return make_response("Bot is running", HTTPStatus.OK)

async def main():
    await setup_webhook()
    server = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(flask_app),
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
