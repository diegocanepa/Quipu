#!/bin/bash

set -e

echo "=== Optimizing EC2 t2.micro for Quipu ==="

# Update system
sudo apt update && sudo apt upgrade -y

# Install only essential packages
sudo apt install -y \
    curl \
    wget \
    systemd \
    logrotate \
    fail2ban \
    ufw \
    net-tools \
    htop

echo "Configuring memory optimization..."

# Configure swap (importante para t2.micro)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Optimize swappiness for better performance
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# Configure firewall (minimal rules)
echo "Configuring minimal firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8080/tcp
sudo ufw --force enable

# Configure fail2ban with lighter config
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Optimize systemd journal size
sudo mkdir -p /etc/systemd/journald.conf.d
sudo tee /etc/systemd/journald.conf.d/quipu.conf << EOF
[Journal]
SystemMaxUse=100M
RuntimeMaxUse=50M
EOF

# Configure logrotate for quipu
sudo tee /etc/logrotate.d/quipu << EOF
/var/log/quipu/*.log {
    daily
    missingok
    rotate 3
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 quipu quipu
    maxsize 10M
}
EOF

# Disable unnecessary services to save memory
sudo systemctl disable snapd
sudo systemctl stop snapd
sudo systemctl mask snapd

echo "Creating optimized service user..."
sudo useradd -r -s /bin/false quipu

echo "Setting up directories..."
sudo mkdir -p /opt/quipu
sudo mkdir -p /var/log/quipu
sudo mkdir -p /opt/backups/quipu

sudo chown -R quipu:quipu /opt/quipu
sudo chown -R quipu:quipu /var/log/quipu
sudo chmod 755 /opt/quipu

echo "Free tier optimization completed!"
echo ""
echo "Memory status:"
free -h
echo ""
echo "Disk usage:"
df -h
echo ""
echo "Next steps:"
echo "1. Create /opt/quipu/.env with your configuration"
echo "2. Configure GitHub secrets"
echo "3. Test deployment"
echo ""
echo "Memory monitoring commands:"
echo "- htop"
echo "- free -h"
echo "- sudo journalctl -u quipu -f"
