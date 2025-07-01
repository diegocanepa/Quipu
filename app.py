import argparse
import asyncio
import logging
from pathlib import Path
import sys
from flask import Flask
from asgiref.wsgi import WsgiToAsgi
import uvicorn
from telegram_bot import app as telegram_app, initialize_telegram, application as telegram_application
from whatsapp_bot import app as whatsapp_app, initialize_whatsapp

# Configure logging
def setup_logging():
    """Configure logging for the application with multiple fallback strategies"""
    import os

    # Try multiple log file locations in order of preference
    log_file_candidates = [
        os.getenv('LOG_FILE', '/var/log/quipu/quipu.log'),  # From environment
        '/var/log/quipu/quipu.log',  # Preferred location
        '/var/log/quipu.log',  # Legacy location (for compatibility)
        '/tmp/quipu.log',  # Temporary fallback
        './quipu.log'  # Local fallback
    ]

    handlers = [logging.StreamHandler(sys.stdout)]
    file_handler_added = False
    
    # Try each log file location until one works
    for log_file_path in log_file_candidates:
        try:
            log_dir = Path(log_file_path).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Test if we can write to the log file
            test_file = log_dir / 'test_write.tmp'
            test_file.touch()
            test_file.unlink()
            
            # Create and test the FileHandler
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            
            # Test writing to the handler
            test_record = logging.LogRecord(
                name='test',
                level=logging.INFO,
                pathname='',
                lineno=0,
                msg='Test log entry during setup',
                args=(),
                exc_info=None
            )
            file_handler.emit(test_record)
            file_handler.flush()
            
            # If we get here, it worked
            handlers.append(file_handler)
            file_handler_added = True
            print(f"✅ Successfully configured file logging to: {log_file_path}")
            break  # Success, stop trying other locations
            
        except (PermissionError, OSError, Exception) as e:
            print(f"⚠️ Failed to setup file logging at {log_file_path}: {e}")
            continue  # Try next location
    
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Force reconfiguration
    )
    
    if not file_handler_added:
        print("⚠️ No file logging configured - using stdout only")
    else:
        print(f"📝 Logging configured with {len(handlers)} handlers (stdout + file)")

setup_logging()
# Get logger for this module
logger = logging.getLogger(__name__)

# Test logging immediately
logger.info("=== LOGGING TEST: This message should appear in both stdout and file ===")
logger.info(f"Logger has {len(logger.handlers)} handlers configured")
for i, handler in enumerate(logger.handlers if hasattr(logger, 'handlers') else []):
    logger.info(f"Handler {i}: {type(handler).__name__}")

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