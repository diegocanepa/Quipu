from flask import Flask
from api.actions import bp as actions_bp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(actions_bp)

if __name__ == '__main__':
    # Run the Flask application using Uvicorn for better performance in production.
    # Host '0.0.0.0' makes the application accessible from outside the container.
    # Port '8080' is the default port for this application.
    logger.info("Starting Flask development server...")
    app.run(host="0.0.0.0", port=8080)