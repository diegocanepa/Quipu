from flask import Flask
from api.actions import bp as actions_bp
from api.bot import bp as bot_bp
from api.bot import initialize_telegram_app, shutdown_telegram_app
from api.status import bp as status_bp
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(actions_bp)
app.register_blueprint(bot_bp)
app.register_blueprint(status_bp)

async def main():
    logger.info("Starting Flask development server...")
    app.run(host="0.0.0.0", port=8080, debug=True)

if __name__ == '__main__':
    asyncio.run(main())