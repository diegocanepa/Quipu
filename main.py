import asyncio
from asgiref.wsgi import WsgiToAsgi
import uvicorn
from bot.bot_instance import application
from config import WEBHOOK_URL
from app import app  # Reutiliza el Flask app

async def setup_webhook():
    await application.bot.set_webhook(url=WEBHOOK_URL)

async def main():
    await setup_webhook()
    await application.initialize()
    await application.start()
    asgi_app = WsgiToAsgi(app)
    config = uvicorn.Config(app=asgi_app, port=8000, host="0.0.0.0")
    server = uvicorn.Server(config)
    await server.serve()
    await application.stop()

if __name__ == "__main__":
    asyncio.run(main())
