#!/bin/bash

set -e

echo "=== Setting up EC2 server for Quipu ==="

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    curl \
    wget \
    unzip \
    systemd \
    logrotate \
    fail2ban \
    ufw \
    net-tools

# Configure firewall
echo "Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8080/tcp
sudo ufw --force enable

# Configure fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure logrotate
sudo tee /etc/logrotate.d/quipu << EOF
/var/log/quipu/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 quipu quipu
}
EOF

# Configure SSH security (opcional pero recomendado)
echo "Configuring SSH security..."
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

echo "Server setup completed!"
echo "Don't forget to:"
echo "1. Configure your .env file in /opt/quipu/"
echo "2. Set up GitHub secrets"
echo "3. Test the deployment"
