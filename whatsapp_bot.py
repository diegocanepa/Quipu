import os
import json
import logging
import asyncio
from flask import Blueprint, jsonify, request, make_response
from pywa_async import WhatsApp, handlers, types
from api.whatsapp.handlers_registry import WhatsAppV2Handlers
from config import config
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from http import HTTPStatus
import argparse

# Get logger for this module with CloudWatch support
from logging_config import get_logger
logger = get_logger(__name__)

app = Blueprint('whatsapp', __name__)

# Initialize WhatsApp client
wa = None  # Will be initialized in initialize_whatsapp

# Initialize handlers
my_handlers = None  # Will be initialized in initialize_whatsapp

@app.route('/')
def home():
    logger.info("WhatsApp home endpoint accessed")
    return 'WhatsApp Bot is running!'

@app.get("/healthcheck")
async def healthcheck():
    """Health check endpoint with version info"""
    logger.info("WhatsApp health check endpoint accessed")
    status = {
        "status": "healthy",
        "service": "quipu-whatsapp",
        "timestamp": asyncio.get_event_loop().time()
    }
    return make_response(status, HTTPStatus.OK)

async def initialize_whatsapp(debug: bool = False, flask_app=None):
    """Initialize WhatsApp service"""
    global wa, my_handlers
    logger.info("Initializing WhatsApp service...")
    
    if flask_app is None:
        raise ValueError("Flask app is required for WhatsApp initialization")
    
    # Initialize WhatsApp client with the Flask app
    wa = WhatsApp(
        phone_id=config.WHATSAPP_PHONE_ID,
        token=config.WHATSAPP_TOKEN,
        server=flask_app,  # Use the Flask app instead of the Blueprint
        verify_token=config.WHATSAPP_VERIFY_TOKEN, 
        app_id=config.WHATSAPP_APP_ID,
        app_secret=config.WHATSAPP_APP_SECRET,
        webhook_endpoint="/whatsapp/webhook",  # Full path including the prefix
    )
    
    # Initialize handlers
    my_handlers = WhatsAppV2Handlers(wa)
    my_handlers.register_handlers()
    
    logger.info(f"Webhook URL: /whatsapp/webhook")
    logger.info("WhatsApp service initialized successfully")

def main_cli():
    """CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(description='Quipu WhatsApp Bot')
    parser.add_argument('--debug', action='store_true',
                       help='Run in debug mode')

    args = parser.parse_args()
    asyncio.run(initialize_whatsapp(args.debug))

if __name__ == '__main__':
    main_cli()