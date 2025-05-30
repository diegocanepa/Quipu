#!/bin/bash

echo "=== Quipu Resource Monitor (Free Tier) ==="
echo ""

# Memory usage
echo "🧠 MEMORY USAGE:"
free -h
echo ""

# Disk usage
echo "💾 DISK USAGE:"
df -h /
echo ""

# Quipu service status
echo "🤖 QUIPU SERVICE:"
if systemctl is-active --quiet quipu; then
    echo "✅ Service is running"
    
    # Get process info
    PID=$(pgrep quipu)
    if [ -n "$PID" ]; then
        echo "📊 Process info:"
        ps -p $PID -o pid,ppid,pcpu,pmem,rss,vsz,cmd
        echo ""
        
        # Memory details
        echo "🔍 Memory details:"
        cat /proc/$PID/status | grep -E "VmRSS|VmSize|VmPeak"
    fi
else
    echo "❌ Service is not running"
fi

echo ""

# Swap usage
echo "🔄 SWAP USAGE:"
swapon --show
echo ""

# Network connections
echo "🌐 NETWORK:"
netstat -tuln | grep :8080 && echo "✅ Port 8080 listening" || echo "❌ Port 8080 not listening"

echo ""

# Recent logs
echo "📝 RECENT LOGS (last 5 lines):"
sudo journalctl -u quipu --lines=5 --no-pager

echo ""
echo "🔧 Quick commands:"
echo "- View logs: sudo journalctl -u quipu -f"
echo "- Restart service: sudo systemctl restart quipu"
echo "- Check memory: watch free -h"
echo "- Process monitor: htop"
