#!/bin/bash

# Forex Trading Advisor - Hetzner Production Deployment Script
# Domain: forextrade.litigataxcounsel.com

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Forex Trading Advisor - Hetzner Deployment${NC}"
echo "================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   exit 1
fi

# Function to check command availability
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ $1 is available${NC}"
    return 0
}

# Function to install Docker
install_docker() {
    echo -e "${YELLOW}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed successfully${NC}"
}

# Function to install Docker Compose
install_docker_compose() {
    echo -e "${YELLOW}🐳 Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✅ Docker Compose installed successfully${NC}"
}

# Check system requirements
echo -e "${BLUE}📋 Checking system requirements...${NC}"

# Check if Docker is installed
if ! check_command docker; then
    read -p "Docker is not installed. Install it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_docker
    else
        echo -e "${RED}❌ Docker is required for deployment${NC}"
        exit 1
    fi
fi

# Check if Docker Compose is installed
if ! check_command docker-compose; then
    read -p "Docker Compose is not installed. Install it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_docker_compose
    else
        echo -e "${RED}❌ Docker Compose is required for deployment${NC}"
        exit 1
    fi
fi

# Check if git is installed
check_command git || {
    echo -e "${YELLOW}Installing git...${NC}"
    sudo apt update && sudo apt install -y git
}

# Check if curl is installed
check_command curl || {
    echo -e "${YELLOW}Installing curl...${NC}"
    sudo apt update && sudo apt install -y curl
}

echo -e "${GREEN}✅ All system requirements are met${NC}"

# Set up project directory
PROJECT_DIR="/opt/forex-strategist"
echo -e "${BLUE}📁 Setting up project directory: $PROJECT_DIR${NC}"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Project directory already exists${NC}"
    read -p "Do you want to update the existing deployment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd $PROJECT_DIR
        echo -e "${YELLOW}🔄 Pulling latest changes...${NC}"
        sudo git pull
    else
        echo -e "${RED}❌ Deployment cancelled${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    sudo git clone https://github.com/bilalhzaidi/forex-strategist.git $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Set proper ownership
sudo chown -R $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# Setup environment configuration
echo -e "${BLUE}⚙️  Setting up environment configuration...${NC}"

# Copy Hetzner environment template
if [ ! -f .env ]; then
    cp .env.hetzner .env
    echo -e "${YELLOW}⚠️  Environment file created from template${NC}"
    echo -e "${YELLOW}📝 Please edit .env file with your actual configuration:${NC}"
    echo "   - Database passwords"
    echo "   - API keys (Alpha Vantage, News API)"
    echo "   - Secret keys"
    echo "   - Monitoring configuration"
    echo ""
    read -p "Press Enter after you've configured the .env file..." -r
    echo ""
fi

# Validate required environment variables
source .env

if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "your_secure_postgres_password_here" ]; then
    echo -e "${RED}❌ Please set a secure POSTGRES_PASSWORD in .env${NC}"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your_super_secure_secret_key_for_production" ]; then
    echo -e "${RED}❌ Please set a secure SECRET_KEY in .env${NC}"
    exit 1
fi

if [ -z "$ALPHA_VANTAGE_API_KEY" ] || [ "$ALPHA_VANTAGE_API_KEY" = "your_alpha_vantage_api_key" ]; then
    echo -e "${YELLOW}⚠️  Alpha Vantage API key not configured. The application will have limited functionality.${NC}"
fi

echo -e "${GREEN}✅ Environment configuration validated${NC}"

# Create necessary directories
echo -e "${BLUE}📁 Creating necessary directories...${NC}"
sudo mkdir -p /var/log/forex-strategist
sudo mkdir -p /opt/forex-strategist/data
sudo mkdir -p /opt/forex-strategist/backups
sudo mkdir -p /opt/forex-strategist/ssl

# Set proper permissions
sudo chown -R $USER:$USER /var/log/forex-strategist
sudo chown -R $USER:$USER /opt/forex-strategist

# Setup SSL certificate
echo -e "${BLUE}🔒 Setting up SSL certificate...${NC}"
if [ ! -f "./ssl/forextrade.litigataxcounsel.com.crt" ]; then
    echo -e "${YELLOW}⚠️  SSL certificate not found${NC}"
    echo "You have two options:"
    echo "1. Use Let's Encrypt (automatic, recommended)"
    echo "2. Provide your own SSL certificate"
    echo ""
    read -p "Use Let's Encrypt? (y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🔒 Let's Encrypt will be configured after deployment${NC}"
        USE_LETSENCRYPT=true
    else
        echo -e "${YELLOW}📝 Please place your SSL certificate files in ./ssl/ directory:${NC}"
        echo "   - forextrade.litigataxcounsel.com.crt"
        echo "   - forextrade.litigataxcounsel.com.key"
        read -p "Press Enter after placing the certificate files..." -r
        USE_LETSENCRYPT=false
    fi
else
    echo -e "${GREEN}✅ SSL certificate found${NC}"
    USE_LETSENCRYPT=false
fi

# Deploy with Docker Compose
echo -e "${BLUE}🚀 Deploying application...${NC}"

# Stop existing containers
if [ "$(docker ps -aq)" ]; then
    echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
    docker-compose -f docker-compose.prod.yml down
fi

# Build and start containers
echo -e "${YELLOW}🔨 Building and starting containers...${NC}"
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 30

# Setup SSL with Let's Encrypt if chosen
if [ "$USE_LETSENCRYPT" = true ]; then
    echo -e "${BLUE}🔒 Setting up Let's Encrypt SSL...${NC}"
    
    # Stop nginx temporarily
    docker-compose -f docker-compose.prod.yml stop nginx
    
    # Run certbot
    docker-compose -f docker-compose.prod.yml run --rm certbot
    
    # Start nginx with SSL
    docker-compose -f docker-compose.prod.yml start nginx
fi

# Health checks
echo -e "${BLUE}🏥 Performing health checks...${NC}"

# Check if backend is responding
echo -e "${YELLOW}Checking backend health...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:8000/health &>/dev/null; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Backend health check failed${NC}"
        docker-compose -f docker-compose.prod.yml logs backend
        exit 1
    fi
    echo -e "${YELLOW}⏳ Waiting for backend... (attempt $i/10)${NC}"
    sleep 5
done

# Check if frontend is responding
echo -e "${YELLOW}Checking frontend health...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:80/health &>/dev/null; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Frontend health check failed${NC}"
        docker-compose -f docker-compose.prod.yml logs frontend
        exit 1
    fi
    echo -e "${YELLOW}⏳ Waiting for frontend... (attempt $i/10)${NC}"
    sleep 5
done

# Setup backup cron job
echo -e "${BLUE}💾 Setting up automatic backups...${NC}"
CRON_JOB="0 2 * * * cd $PROJECT_DIR && ./backup.sh > /var/log/forex-strategist/backup.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
echo -e "${GREEN}✅ Daily backup scheduled at 2 AM${NC}"

# Setup log rotation
echo -e "${BLUE}📋 Setting up log rotation...${NC}"
sudo tee /etc/logrotate.d/forex-strategist > /dev/null <<EOF
/var/log/forex-strategist/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 644 $USER $USER
    postrotate
        docker-compose -f $PROJECT_DIR/docker-compose.prod.yml restart backend frontend
    endscript
}
EOF
echo -e "${GREEN}✅ Log rotation configured${NC}"

# Final status
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "================================================="
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo "   🌐 Domain: forextrade.litigataxcounsel.com"
echo "   🔗 HTTP:  http://$(curl -s ifconfig.me)"
echo "   🔒 HTTPS: https://forextrade.litigataxcounsel.com"
echo "   📱 API:   https://forextrade.litigataxcounsel.com/api/v1"
echo "   🏥 Health: https://forextrade.litigataxcounsel.com/api/v1/health"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Point your domain forextrade.litigataxcounsel.com to this server's IP"
echo "2. Test the application at https://forextrade.litigataxcounsel.com"
echo "3. Monitor logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "4. Check metrics: docker-compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/metrics"
echo ""
echo -e "${GREEN}🔧 Management Commands:${NC}"
echo "   Start:   docker-compose -f docker-compose.prod.yml up -d"
echo "   Stop:    docker-compose -f docker-compose.prod.yml down"
echo "   Logs:    docker-compose -f docker-compose.prod.yml logs -f [service]"
echo "   Update:  ./deploy-hetzner.sh"
echo "   Backup:  ./backup.sh"
echo ""
echo -e "${BLUE}📞 Support: Check logs and health endpoints if issues occur${NC}"