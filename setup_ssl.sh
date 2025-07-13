#!/bin/bash

# AI Investment Advisor - SSL Certificate Setup Script
# This script sets up SSL certificates using Let's Encrypt

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Check if domain is provided
if [ -z "$1" ]; then
    print_error "Usage: $0 <domain.com>"
    print_error "Example: $0 myapp.example.com"
    exit 1
fi

DOMAIN=$1
print_status "Setting up SSL certificate for domain: $DOMAIN"

# Check if domain resolves to this server
print_status "Checking domain DNS resolution..."
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to determine IP")
DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null || echo "Unable to resolve domain")

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    print_warning "Domain $DOMAIN does not resolve to this server IP ($SERVER_IP)"
    print_warning "Current domain IP: $DOMAIN_IP"
    print_warning "Please update your DNS records before proceeding."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install snapd if not present
if ! command -v snap &> /dev/null; then
    print_status "Installing snapd..."
    sudo apt update
    sudo apt install -y snapd
fi

# Install certbot
print_status "Installing certbot..."
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot

# Create symlink if it doesn't exist
if [ ! -L "/usr/bin/certbot" ]; then
    sudo ln -s /snap/bin/certbot /usr/bin/certbot
fi

# Update nginx configuration with domain
print_status "Updating nginx configuration with domain..."
sudo tee /etc/nginx/sites-available/ai-investment-advisor > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Test nginx configuration
if sudo nginx -t; then
    print_status "Nginx configuration is valid"
    sudo systemctl reload nginx
else
    print_error "Nginx configuration is invalid"
    exit 1
fi

# Obtain SSL certificate
print_status "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --redirect

# Test automatic renewal
print_status "Testing automatic certificate renewal..."
sudo certbot renew --dry-run

# Setup automatic renewal via cron
print_status "Setting up automatic certificate renewal..."
(sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -

# Final status check
print_status "Checking SSL setup..."
sleep 2

if sudo nginx -t; then
    print_status "Nginx configuration is valid with SSL"
else
    print_error "Nginx configuration is invalid after SSL setup"
    exit 1
fi

# Test HTTPS
print_status "Testing HTTPS connection..."
if curl -s --max-time 10 https://$DOMAIN > /dev/null; then
    print_status "HTTPS is working correctly!"
else
    print_warning "HTTPS test failed. Please check your configuration."
fi

print_status "SSL setup completed successfully!"
echo ""
echo "Your application is now available at:"
echo "- HTTP: http://$DOMAIN (redirects to HTTPS)"
echo "- HTTPS: https://$DOMAIN"
echo ""
echo "Certificate details:"
sudo certbot certificates
echo ""
print_status "Certificate will auto-renew every 60 days via cron job." 