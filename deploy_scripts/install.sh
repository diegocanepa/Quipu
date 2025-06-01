#!/bin/bash

set -e

APP_NAME="quipu"
SERVICE_NAME="quipu.service"
DEPLOY_DIR="/opt/$APP_NAME"
LOG_DIR="/var/log/$APP_NAME"

echo "=== Quipu Installation Script ==="

# Create user for the service
if ! id -u quipu > /dev/null 2>&1; then
    echo "Creating quipu user..."
    sudo useradd -r -s /bin/false quipu
fi

# Create directories
echo "Creating directories..."
sudo mkdir -p $DEPLOY_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p /opt/backups/$APP_NAME

# Set permissions
sudo chown -R quipu:quipu $DEPLOY_DIR
sudo chown -R quipu:quipu $LOG_DIR
sudo chmod 755 $DEPLOY_DIR

echo "Installation completed!"
