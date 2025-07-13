#!/bin/bash

# AI Investment Advisor - Cloud Deployment Script
# This script automates the deployment process for Ubuntu/Debian servers

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

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    print_error "This script is designed for Ubuntu/Debian systems with apt package manager."
    exit 1
fi

print_status "Starting AI Investment Advisor deployment..."

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx supervisor redis-server curl

# Create application user if it doesn't exist
if ! id "appuser" &>/dev/null; then
    print_status "Creating application user..."
    sudo useradd -m -s /bin/bash appuser
    sudo usermod -aG sudo appuser
fi

# Setup application directory
APP_DIR="/home/appuser/ai-investment-advisor"
print_status "Setting up application directory..."

# Clone or update repository
if [ -d "$APP_DIR" ]; then
    print_warning "Application directory already exists. Updating..."
    sudo -u appuser git -C "$APP_DIR" pull
else
    print_status "Cloning repository..."
    sudo -u appuser git clone https://github.com/yourusername/ai-investment-advisor.git "$APP_DIR"
fi

# Setup virtual environment
print_status "Setting up Python virtual environment..."
sudo -u appuser python3.11 -m venv "$APP_DIR/venv"
sudo -u appuser "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u appuser "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
sudo -u appuser "$APP_DIR/venv/bin/pip" install gunicorn

# Create environment file if it doesn't exist
ENV_FILE="$APP_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    print_status "Creating environment file..."
    sudo -u appuser cat > "$ENV_FILE" << 'EOF'
# Production Environment Configuration
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
FLASK_APP_PORT=5000
FLASK_SECRET_KEY=your_very_secure_secret_key_here
FLASK_DEBUG=False
FLASK_ENV=production
EOF
    print_warning "Please edit $ENV_FILE with your actual API keys and secret key!"
fi

# Create startup script
print_status "Creating startup script..."
sudo -u appuser cat > "$APP_DIR/start_app.sh" << 'EOF'
#!/bin/bash
cd /home/appuser/ai-investment-advisor
source venv/bin/activate
exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
EOF
sudo -u appuser chmod +x "$APP_DIR/start_app.sh"

# Create supervisor configuration
print_status "Configuring supervisor..."
sudo tee /etc/supervisor/conf.d/ai-investment-advisor.conf > /dev/null << 'EOF'
[program:ai-investment-advisor]
command=/home/appuser/ai-investment-advisor/start_app.sh
directory=/home/appuser/ai-investment-advisor
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ai-investment-advisor.log
environment=PATH="/home/appuser/ai-investment-advisor/venv/bin"
EOF

# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Configure nginx
print_status "Configuring nginx..."
sudo tee /etc/nginx/sites-available/ai-investment-advisor > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/ai-investment-advisor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
if sudo nginx -t; then
    print_status "Nginx configuration is valid"
else
    print_error "Nginx configuration is invalid"
    exit 1
fi

# Start services
print_status "Starting services..."
sudo systemctl restart nginx
sudo systemctl enable nginx
sudo supervisorctl start ai-investment-advisor

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Create backup script
print_status "Creating backup script..."
sudo -u appuser cat > "/home/appuser/backup.sh" << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/appuser/backups"
mkdir -p $BACKUP_DIR

# Backup data directory
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz /home/appuser/ai-investment-advisor/data/ 2>/dev/null || true

# Keep only last 7 days of backups
find $BACKUP_DIR -name "data_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true
EOF
sudo -u appuser chmod +x "/home/appuser/backup.sh"

# Add backup to cron
print_status "Setting up automated backups..."
(sudo -u appuser crontab -l 2>/dev/null; echo "0 2 * * * /home/appuser/backup.sh") | sudo -u appuser crontab -

# Final status check
print_status "Checking deployment status..."
sleep 5

if sudo supervisorctl status ai-investment-advisor | grep -q "RUNNING"; then
    print_status "Application is running successfully!"
else
    print_error "Application failed to start. Check logs with: sudo supervisorctl tail ai-investment-advisor"
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    print_status "Nginx is running successfully!"
else
    print_error "Nginx failed to start. Check logs with: sudo journalctl -u nginx"
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to determine IP")

print_status "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit $ENV_FILE with your actual API keys"
echo "2. Restart the application: sudo supervisorctl restart ai-investment-advisor"
echo "3. Access your application at: http://$SERVER_IP"
echo "4. For HTTPS, configure SSL certificate using certbot"
echo ""
echo "Useful commands:"
echo "- Check app status: sudo supervisorctl status ai-investment-advisor"
echo "- View app logs: sudo supervisorctl tail ai-investment-advisor"
echo "- Restart app: sudo supervisorctl restart ai-investment-advisor"
echo "- Check nginx status: sudo systemctl status nginx"
echo ""
print_warning "Remember to configure your domain DNS and SSL certificate for production use!" 