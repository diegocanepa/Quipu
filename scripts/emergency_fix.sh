#!/bin/bash

set -e

echo "=== Quipu Emergency Logging Fix ==="

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

# Create the problematic log file path as a symlink to the correct location
echo "Creating symlink for legacy log path..."
sudo mkdir -p /var/log
if [ -f "/var/log/quipu.log" ]; then
    sudo rm -f /var/log/quipu.log
fi
sudo ln -sf $LOG_DIR/quipu.log /var/log/quipu.log

# Set ownership and permissions
echo "Setting permissions..."
sudo chown -R quipu:quipu $DEPLOY_DIR
sudo chown -R quipu:quipu $LOG_DIR
sudo chown -R quipu:quipu /opt/backups/$APP_NAME
sudo chown quipu:quipu /var/log/quipu.log

# Make directories writable
sudo chmod 755 $DEPLOY_DIR
sudo chmod 755 $LOG_DIR
sudo chmod 755 /opt/backups/$APP_NAME

# Test write permissions
echo "Testing write permissions..."
sudo -u quipu touch $LOG_DIR/test.log
sudo -u quipu rm -f $LOG_DIR/test.log

# Test the symlink
sudo -u quipu touch /var/log/quipu.log
sudo -u quipu rm -f /var/log/quipu.log

echo "✅ Emergency fix applied successfully!"

# Update service file to have the correct environment variables
if [ -f "/etc/systemd/system/$SERVICE_NAME" ]; then
    echo "Updating service file with correct environment variables..."
    
    # Backup original service file
    sudo cp /etc/systemd/system/$SERVICE_NAME /etc/systemd/system/$SERVICE_NAME.backup
    
    # Add LOG_FILE environment variable if it doesn't exist
    if ! grep -q "Environment=LOG_FILE" /etc/systemd/system/$SERVICE_NAME; then
        sudo sed -i '/Environment=PYTHONDONTWRITEBYTECODE=1/a Environment=LOG_FILE=/var/log/quipu/quipu.log' /etc/systemd/system/$SERVICE_NAME
    fi
    
    # Reload systemd
    sudo systemctl daemon-reload
fi

# Restart service if needed
if systemctl list-unit-files | grep -q "^$SERVICE_NAME"; then
    echo "Reloading systemd configuration..."
    sudo systemctl daemon-reload
    
    if sudo systemctl is-active --quiet $SERVICE_NAME; then
        echo "Restarting service..."
        sudo systemctl restart $SERVICE_NAME
        sleep 5
        
        if sudo systemctl is-active --quiet $SERVICE_NAME; then
            echo "✅ Service restarted successfully"
            sudo systemctl status $SERVICE_NAME --no-pager
        else
            echo "❌ Service failed to restart"
            sudo journalctl -u $SERVICE_NAME --lines=20 --no-pager
        fi
    else
        echo "Starting service..."
        sudo systemctl start $SERVICE_NAME
        sleep 5
        
        if sudo systemctl is-active --quiet $SERVICE_NAME; then
            echo "✅ Service started successfully"
        else
            echo "❌ Service failed to start"
            sudo journalctl -u $SERVICE_NAME --lines=20 --no-pager
        fi
    fi
fi

echo "=== Emergency fix completed ==="
echo ""
echo "📋 What this script did:"
echo "   - Created /var/log/quipu/ directory"
echo "   - Created symlink /var/log/quipu.log -> /var/log/quipu/quipu.log"
echo "   - Set correct permissions for quipu user"
echo "   - Updated service file with LOG_FILE environment variable"
echo "   - Restarted the service"
echo ""
echo "🔍 To verify everything is working:"
echo "   sudo systemctl status quipu.service"
echo "   sudo tail -f /var/log/quipu/quipu.log"
