import argparse
import asyncio
import logging
from flask import Flask
from asgiref.wsgi import WsgiToAsgi
import uvicorn
from telegram_bot import app as telegram_app, initialize_telegram, application as telegram_application
from whatsapp_bot import app as whatsapp_app, initialize_whatsapp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/home/ubuntu/quipu.log")
    ]
)

# Get logger for this module
logger = logging.getLogger(__name__)

# Create main Flask app
app = Flask(__name__)

# Register Telegram routes
app.register_blueprint(telegram_app, url_prefix='/telegram')

# Register WhatsApp routes
app.register_blueprint(whatsapp_app, url_prefix='/whatsapp')

@app.route('/')
def home():
    logger.info("Home endpoint accessed")
    return 'Quipu Multi-Service Financial Bot is running!'

@app.route('/healthcheck')
def healthcheck():
    logger.info("Health check endpoint accessed")
    return {
        'status': 'healthy',
        'services': ['telegram', 'whatsapp']
    }

async def initialize_services(debug: bool = False):
    """Initialize both services"""
    try:
        logger.info("Initializing services...")
        await asyncio.gather(
            initialize_telegram(debug=debug),
            initialize_whatsapp(debug=debug, flask_app=app)
        )
        logger.info("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        raise

async def shutdown_services():
    """Shutdown both services"""
    try:
        logger.info("Shutting down services...")
        await telegram_application.stop()
        # Add WhatsApp shutdown if needed
        logger.info("Services shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down services: {e}")

def main_cli():
    """CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(description='Quipu Multi-Service Financial Bot')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port to run the server on (default: 8080)')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')

    args = parser.parse_args()

    async def run_server():
        try:
            # Initialize services
            await initialize_services(args.debug)
            
            # Start the unified server
            logger.info(f"Starting server on {args.host}:{args.port}")
            server = uvicorn.Server(
                config=uvicorn.Config(
                    app=WsgiToAsgi(app),
                    port=args.port,
                    host=args.host,
                    use_colors=True,
                    log_level="debug" if args.debug else "info",
                    reload=args.debug
                )
            )
            await server.serve()
        finally:
            # Ensure services are properly shut down
            await shutdown_services()

    asyncio.run(run_server())

if __name__ == '__main__':
    main_cli() 