#!/bin/bash

SERVICE_NAME="quipu.service"
DEPLOY_DIR="/opt/quipu"

echo "=== Health Check for Quipu ==="

# Check if service is running
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service is running"
else
    echo "❌ Service is not running"
    echo "Recent logs:"
    journalctl -u $SERVICE_NAME --lines=10 --no-pager
    exit 1
fi

# Check if binary exists and is executable
if [ -x "$DEPLOY_DIR/quipu" ]; then
    echo "✅ Binary is present and executable"
else
    echo "❌ Binary not found or not executable"
    exit 1
fi

# Check if port 8080 is listening
if netstat -tuln | grep -q ":8080"; then
    echo "✅ Port 8080 is listening"
else
    echo "❌ Port 8080 is not listening"
    exit 1
fi

# Check memory usage
MEMORY_USAGE=$(ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem -C quipu | tail -n +2)
if [ -n "$MEMORY_USAGE" ]; then
    echo "📊 Memory usage:"
    echo "$MEMORY_USAGE"
else
    echo "⚠️ Process information not available"
fi

# Check log file size
LOG_FILE="/var/log/quipu/quipu.log"
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
    echo "📝 Log file size: $LOG_SIZE"
else
    echo "⚠️ Log file not found"
fi

echo "✅ Health check completed!"
