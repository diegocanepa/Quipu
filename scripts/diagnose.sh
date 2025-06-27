#!/bin/bash

echo "=== Quipu Deployment Diagnostics ==="
echo ""

# Check service status
echo "🔍 Service Status:"
sudo systemctl is-active quipu.service && echo "✅ Service is running" || echo "❌ Service is not running"
echo ""

# Check service configuration
echo "🔍 Service Configuration:"
if [ -f "/etc/systemd/system/quipu.service" ]; then
    echo "✅ Service file exists"
    echo "📋 Environment variables in service:"
    grep "Environment=" /etc/systemd/system/quipu.service
    echo "📋 ReadWrite paths:"
    grep "ReadWritePaths=" /etc/systemd/system/quipu.service
else
    echo "❌ Service file missing"
fi
echo ""

# Check directories and permissions
echo "🔍 Directory Status:"
for dir in "/opt/quipu" "/var/log/quipu" "/opt/backups/quipu"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
        echo "   Owner: $(stat -c '%U:%G' $dir)"
        echo "   Permissions: $(stat -c '%a' $dir)"
    else
        echo "❌ $dir missing"
    fi
done
echo ""

# Check user
echo "🔍 User Status:"
if id -u quipu > /dev/null 2>&1; then
    echo "✅ quipu user exists"
    echo "   UID: $(id -u quipu)"
    echo "   GID: $(id -g quipu)"
    echo "   Shell: $(getent passwd quipu | cut -d: -f7)"
else
    echo "❌ quipu user missing"
fi
echo ""

# Test write permissions
echo "🔍 Write Permission Test:"
if sudo -u quipu touch /var/log/quipu/test_write.log 2>/dev/null; then
    sudo -u quipu rm -f /var/log/quipu/test_write.log
    echo "✅ Can write to /var/log/quipu"
else
    echo "❌ Cannot write to /var/log/quipu"
fi
echo ""

# Check binary
echo "🔍 Binary Status:"
if [ -f "/opt/quipu/quipu" ]; then
    echo "✅ Binary exists"
    echo "   Owner: $(stat -c '%U:%G' /opt/quipu/quipu)"
    echo "   Permissions: $(stat -c '%a' /opt/quipu/quipu)"
    echo "   Executable: $(test -x /opt/quipu/quipu && echo "Yes" || echo "No")"
else
    echo "❌ Binary missing"
fi
echo ""

# Check recent logs
echo "🔍 Recent Logs (last 10 lines):"
sudo journalctl -u quipu.service --lines=10 --no-pager || echo "No logs available"
echo ""

# Check network
echo "🔍 Network Status:"
if netstat -tuln | grep -q ":8080"; then
    echo "✅ Port 8080 is listening"
else
    echo "❌ Port 8080 not listening"
fi
echo ""

# Memory usage
echo "🔍 Memory Status:"
free -h
echo ""

# Disk usage
echo "🔍 Disk Usage:"
df -h /opt /var/log
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "🔧 If there are issues, try:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl restart quipu.service"
echo "   sudo journalctl -u quipu.service -f"
