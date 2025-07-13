# AI Investment Advisor - Multi-Agent System

A sophisticated multi-agent system for investment advice, stock analysis, and financial insights. Built with Flask, OpenAI, and Alpha Vantage APIs.

## Features

### 🤖 Multi-Agent Architecture
- **Coordinator Agent**: Main orchestrator that routes requests to specialized agents
- **Stock Quote Agent**: Fetches real-time and historical stock prices with caching
- **Stock News Agent**: Retrieves and analyzes stock news with sentiment analysis
- **Trading Advice Agent**: Provides investment advice based on legendary investor personalities

### 👥 Expert Personalities
Switch between different investment philosophies:
- **Warren Buffett** - Value investing and long-term focus
- **Peter Lynch** - Growth at reasonable price (GARP)
- **Benjamin Graham** - Deep value with margin of safety
- **George Soros** - Macro investing and reflexivity
- **Cathie Wood** - Innovation and disruptive technology
- **Charlie Munger** - Quality businesses and mental models
- **Michael Burry** - Contrarian value investing
- **Phil Fisher** - Growth investing with "scuttlebutt" research
- **Rakesh Jhunjhunwala** - Long-term wealth creation
- **Stanley Druckenmiller** - Macro trends and risk management
- **Bill Ackman** - Activist investing
- **Aswath Damodaran** - Valuation-focused approach

### 🌐 Web Interface
- Real-time chat interface with WebSocket support
- Clickable personality selection
- Modern, responsive design
- Stock data visualization

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd bd2
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Flask Application Configuration
FLASK_APP_PORT=5000
FLASK_SECRET_KEY=your_secret_key_here
FLASK_DEBUG=True
```

### 5. Get API Keys
- **OpenAI API Key**: Sign up at [OpenAI](https://platform.openai.com/)
- **Alpha Vantage API Key**: Get free key at [Alpha Vantage](https://www.alphavantage.co/support/#api-key)

### 6. Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Usage Examples

### Stock Quotes
- "What's the current price of AAPL?"
- "Show me Tesla stock price on 2023-12-01"
- "MSFT stock quote"

### Stock News
- "Show me recent news for Apple"
- "Tesla news from last week"
- "Microsoft headlines from January 1 to January 31"

### Investment Advice
- "Should I buy Amazon stock?"
- "What do you think about investing in Tesla?"
- "Analyze my portfolio: 50% AAPL, 30% MSFT, 20% GOOGL"

### Personality Changes
- "Change personality to Peter Lynch"
- "Switch to Cathie Wood"
- "Become Benjamin Graham"

## Project Structure

```
bd2/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── coordinator_agent.py   # Main orchestrator
│   ├── stock_quote_agent.py   # Stock price data
│   ├── stock_news_agent.py    # News and sentiment
│   └── trading_advice_agent.py # Investment advice
├── data/                      # CSV cache files
├── static/
│   ├── css/style.css         # Web interface styling
│   └── js/main.js            # Client-side JavaScript
├── templates/
│   └── index.html            # Web interface template
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Features in Detail

### Caching System
- Stock quotes cached in CSV format (`{ticker}_data.csv`)
- News articles cached with sentiment analysis
- Automatic cache management and updates

### Real-time Communication
- WebSocket-based real-time messaging
- Instant personality switching
- Live data updates

### Intelligent Routing
- Natural language processing for intent classification
- Automatic delegation to appropriate agents
- Context-aware responses

## API Limitations

### Alpha Vantage
- Free tier: 5 API calls per minute, 500 calls per day
- Stock data: 2+ years of historical data
- News: Real-time and historical articles

### OpenAI
- Rate limits depend on your plan
- GPT-3.5-turbo used for personality responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Cloud Deployment

### Quick Deployment (Recommended)

For a quick and automated deployment, use the included deployment scripts:

```bash
# 1. Clone the repository on your server
git clone <your-repository-url> ai-investment-advisor
cd ai-investment-advisor

# 2. Run the automated deployment script
./deploy.sh

# 3. Configure your API keys in the .env file
nano /home/appuser/ai-investment-advisor/.env

# 4. Restart the application
sudo supervisorctl restart ai-investment-advisor

# 5. (Optional) Setup SSL certificate for your domain
./setup_ssl.sh your-domain.com
```

### Prerequisites for Cloud Deployment
- Cloud server (AWS EC2, Google Cloud, DigitalOcean, etc.)
- Domain name (optional but recommended)
- SSL certificate (for HTTPS)
- Basic knowledge of Linux server administration

### 1. Server Setup

#### Option A: AWS EC2 Deployment

1. **Launch EC2 Instance**
   ```bash
   # Choose Ubuntu 22.04 LTS or Amazon Linux 2
   # Minimum: t3.micro (1 vCPU, 1GB RAM)
   # Recommended: t3.small (2 vCPU, 2GB RAM)
   ```

2. **Configure Security Groups**
   ```bash
   # Allow inbound traffic:
   # SSH (22) - Your IP only
   # HTTP (80) - 0.0.0.0/0
   # HTTPS (443) - 0.0.0.0/0
   # Custom TCP (5000) - 0.0.0.0/0 (for development)
   ```

3. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

#### Option B: DigitalOcean Droplet

1. **Create Droplet**
   ```bash
   # Choose Ubuntu 22.04 LTS
   # Minimum: Basic plan $6/month (1GB RAM, 1 vCPU)
   # Recommended: $12/month (2GB RAM, 1 vCPU)
   ```

2. **Connect via SSH**
   ```bash
   ssh root@your-droplet-ip
   ```

### 2. Server Configuration

#### Update System and Install Dependencies
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install system dependencies
sudo apt install git nginx supervisor redis-server -y

# Install Node.js (for potential future enhancements)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Create Application User
```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash appuser
sudo usermod -aG sudo appuser
sudo su - appuser
```

### 3. Application Deployment

#### Clone and Setup Application
```bash
# Clone the repository
git clone <your-repository-url> ai-investment-advisor
cd ai-investment-advisor

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production server
pip install gunicorn
```

#### Configure Environment Variables
```bash
# Create production environment file
nano .env
```

```env
# Production Environment Configuration
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
FLASK_APP_PORT=5000
FLASK_SECRET_KEY=your_very_secure_secret_key_here
FLASK_DEBUG=False
FLASK_ENV=production
```

#### Create Production Startup Script
```bash
# Create startup script
nano start_app.sh
```

```bash
#!/bin/bash
cd /home/appuser/ai-investment-advisor
source venv/bin/activate
exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

```bash
# Make script executable
chmod +x start_app.sh
```

### 4. Process Management with Supervisor

#### Create Supervisor Configuration
```bash
sudo nano /etc/supervisor/conf.d/ai-investment-advisor.conf
```

```ini
[program:ai-investment-advisor]
command=/home/appuser/ai-investment-advisor/start_app.sh
directory=/home/appuser/ai-investment-advisor
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ai-investment-advisor.log
environment=PATH="/home/appuser/ai-investment-advisor/venv/bin"
```

#### Start and Enable Supervisor
```bash
# Update supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start the application
sudo supervisorctl start ai-investment-advisor

# Check status
sudo supervisorctl status
```

### 5. Nginx Reverse Proxy Setup

#### Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/ai-investment-advisor
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

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
```

#### Enable Site and Restart Nginx
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/ai-investment-advisor /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 6. SSL Certificate Setup (HTTPS)

#### Install Certbot
```bash
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

#### Obtain SSL Certificate
```bash
# Get certificate for your domain
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 7. Firewall Configuration

#### Configure UFW (Ubuntu Firewall)
```bash
# Enable firewall
sudo ufw enable

# Allow necessary ports
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Check status
sudo ufw status
```

### 8. Monitoring and Maintenance

#### Log Management
```bash
# View application logs
sudo tail -f /var/log/ai-investment-advisor.log

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View supervisor logs
sudo supervisorctl tail ai-investment-advisor
```

#### System Monitoring
```bash
# Check application status
sudo supervisorctl status ai-investment-advisor

# Restart application
sudo supervisorctl restart ai-investment-advisor

# Check system resources
htop
df -h
free -h
```

### 9. Backup and Recovery

#### Database Backup (if using database)
```bash
# Create backup script
nano backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/appuser/backups"
mkdir -p $BACKUP_DIR

# Backup data directory
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz /home/appuser/ai-investment-advisor/data/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "data_backup_*.tar.gz" -mtime +7 -delete
```

#### Automated Backups with Cron
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/appuser/backup.sh
```

### 10. Performance Optimization

#### Redis for Session Management (Optional)
```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: maxmemory 128mb
# Set: maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

#### Application Optimization
```bash
# Update requirements.txt for production
echo "redis==4.5.1" >> requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt
pip install -r requirements.txt
```

### 11. Security Best Practices

#### System Security
```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart ssh
```

#### Application Security
- Use strong secret keys
- Keep API keys secure
- Regular security updates
- Monitor access logs
- Use HTTPS only in production

### 12. Scaling Considerations

#### Horizontal Scaling
- Use load balancer (AWS ALB, Nginx)
- Multiple application instances
- Shared session storage (Redis)
- Database clustering

#### Vertical Scaling
- Increase server resources
- Optimize application code
- Use caching strategies
- Database indexing

### 13. Troubleshooting Deployment

#### Common Issues
1. **Port conflicts**: Change port in `.env` file
2. **Permission errors**: Check file ownership and permissions
3. **SSL certificate issues**: Verify domain DNS settings
4. **Application crashes**: Check logs with `sudo supervisorctl tail ai-investment-advisor`

#### Health Check Endpoint
Add to `app.py`:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### 14. Domain and DNS Setup

#### Configure DNS Records
```
A Record: your-domain.com → your-server-ip
CNAME Record: www.your-domain.com → your-domain.com
```

#### Test Deployment
```bash
# Test HTTP
curl http://your-domain.com

# Test HTTPS
curl https://your-domain.com

# Test WebSocket
# Open browser and test real-time functionality
```

## Deployment Scripts

The project includes two automated deployment scripts to simplify cloud deployment:

### 1. `deploy.sh` - Main Deployment Script

This script automates the entire deployment process:

- Updates system packages
- Installs Python 3.11, nginx, supervisor, and other dependencies
- Creates application user and directory structure
- Sets up Python virtual environment
- Installs application dependencies
- Configures supervisor for process management
- Sets up nginx reverse proxy
- Configures firewall (UFW)
- Creates automated backup system
- Performs health checks

**Usage:**
```bash
./deploy.sh
```

**Features:**
- Colored output for better visibility
- Error handling and validation
- Automatic service startup
- Backup system with cron jobs
- Health checks and status reporting

### 2. `setup_ssl.sh` - SSL Certificate Setup

This script sets up HTTPS using Let's Encrypt SSL certificates:

- Installs certbot via snap
- Updates nginx configuration with domain
- Obtains SSL certificate from Let's Encrypt
- Sets up automatic certificate renewal
- Tests HTTPS functionality

**Usage:**
```bash
./setup_ssl.sh your-domain.com
```

**Features:**
- DNS resolution validation
- Automatic HTTP to HTTPS redirect
- Certificate auto-renewal via cron
- HTTPS connectivity testing

### Script Requirements

Both scripts require:
- Ubuntu/Debian server with `apt` package manager
- Non-root user with sudo privileges
- Internet connectivity for package installation

### Post-Deployment Configuration

After running the deployment scripts:

1. **Configure API Keys:**
   ```bash
   nano /home/appuser/ai-investment-advisor/.env
   ```

2. **Restart Application:**
   ```bash
   sudo supervisorctl restart ai-investment-advisor
   ```

3. **Check Status:**
   ```bash
   sudo supervisorctl status ai-investment-advisor
   sudo systemctl status nginx
   ```

4. **View Logs:**
   ```bash
   sudo supervisorctl tail ai-investment-advisor
   sudo tail -f /var/log/nginx/access.log
   ```

## License

This project is licensed under the MIT License.

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `.env` file is properly configured
   - Check API key validity and quotas

2. **Import Errors**
   - Activate virtual environment
   - Install all requirements: `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change `FLASK_APP_PORT` in `.env` file
   - Or kill process using the port

4. **Cache Issues**
   - Clear `data/` folder to reset cache
   - Restart application

### Support

For issues and questions, please create an issue in the repository. 