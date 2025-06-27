#!/bin/bash

set -e

echo "=== Fixing Quipu permissions and directories ==="

APP_NAME="quipu"
SERVICE_NAME="quipu.service"
DEPLOY_DIR="/opt/$APP_NAME"
LOG_DIR="/var/log/$APP_NAME"

# Ensure user exists
if ! id -u quipu > /dev/null 2>&1; then
    echo "Creating quipu user..."
    sudo useradd -r -s /bin/false quipu
fi

# Create directories with correct permissions
echo "Creating and setting up directories..."
sudo mkdir -p $DEPLOY_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p /opt/backups/$APP_NAME

# Set ownership and permissions
echo "Setting permissions..."
sudo chown -R quipu:quipu $DEPLOY_DIR
sudo chown -R quipu:quipu $LOG_DIR
sudo chown -R quipu:quipu /opt/backups/$APP_NAME

# Make directories writable
sudo chmod 755 $DEPLOY_DIR
sudo chmod 755 $LOG_DIR
sudo chmod 755 /opt/backups/$APP_NAME

# Test write permissions
echo "Testing write permissions..."
sudo -u quipu touch $LOG_DIR/test.log
sudo -u quipu rm -f $LOG_DIR/test.log

echo "✅ Permissions fixed successfully!"

# Reload systemd and restart service if needed
if systemctl list-unit-files | grep -q "^$SERVICE_NAME"; then
    echo "Reloading systemd configuration..."
    sudo systemctl daemon-reload
    
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        echo "Restarting service..."
        sudo systemctl restart $SERVICE_NAME
        sleep 5
        
        if sudo systemctl is-active --quiet $SERVICE_NAME; then
            echo "✅ Service restarted successfully"
        else
            echo "❌ Service failed to restart"
            sudo journalctl -u $SERVICE_NAME --lines=20 --no-pager
        fi
    fi
fi

echo "=== Permission fix completed ==="
