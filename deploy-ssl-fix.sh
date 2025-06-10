#!/bin/bash

# Forex Trading Advisor - SSL Fix Deployment Script
# This script fixes the SSL issue by deploying the updated configuration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 Forex Trading Advisor - SSL Fix Deployment${NC}"
echo "=============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   exit 1
fi

# Project directory
PROJECT_DIR="/opt/forex-strategist"
echo -e "${BLUE}📁 Working in project directory: $PROJECT_DIR${NC}"

# Navigate to project directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory $PROJECT_DIR not found${NC}"
    echo "Please run the main deployment script first"
    exit 1
fi

cd $PROJECT_DIR

# Pull latest changes
echo -e "${YELLOW}🔄 Pulling latest changes...${NC}"
sudo git pull

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Create necessary directories for certbot
echo -e "${BLUE}📁 Creating SSL directories...${NC}"
sudo mkdir -p /etc/letsencrypt
sudo mkdir -p /var/www/certbot
sudo chown -R $USER:$USER /var/www/certbot

# First, start without SSL to get the certificate
echo -e "${YELLOW}🚀 Starting services in HTTP-only mode for certificate request...${NC}"

# Temporarily modify nginx config for initial certificate request
cp nginx-ssl.conf nginx-ssl.conf.backup
sed 's/listen 443 ssl http2;/# listen 443 ssl http2;/' nginx-ssl.conf > nginx-http-temp.conf
sed 's/ssl_certificate/#ssl_certificate/g' nginx-http-temp.conf > nginx-ssl.conf

# Start containers
docker-compose -f docker-compose.prod.yml up -d postgres redis backend frontend nginx

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 30

# Check if services are running
echo -e "${BLUE}🏥 Checking service health...${NC}"
if curl -f http://localhost/health &>/dev/null; then
    echo -e "${GREEN}✅ Services are running${NC}"
else
    echo -e "${RED}❌ Services are not responding${NC}"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

# Request SSL certificate
echo -e "${BLUE}🔒 Requesting SSL certificate...${NC}"
docker-compose -f docker-compose.prod.yml --profile certbot run --rm certbot

# Check if certificate was created
if [ -f "/etc/letsencrypt/live/forextrade.litigataxcounsel.com/fullchain.pem" ]; then
    echo -e "${GREEN}✅ SSL certificate obtained successfully${NC}"
    
    # Restore original nginx config with SSL
    cp nginx-ssl.conf.backup nginx-ssl.conf
    rm nginx-http-temp.conf nginx-ssl.conf.backup
    
    # Restart nginx with SSL configuration
    echo -e "${YELLOW}🔄 Restarting nginx with SSL configuration...${NC}"
    docker-compose -f docker-compose.prod.yml restart nginx
    
else
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo "Continuing with HTTP-only configuration"
fi

# Final health checks
echo -e "${BLUE}🏥 Performing final health checks...${NC}"

# Check HTTP
echo -e "${YELLOW}Checking HTTP...${NC}"
if curl -f http://localhost/health &>/dev/null; then
    echo -e "${GREEN}✅ HTTP is working${NC}"
else
    echo -e "${RED}❌ HTTP health check failed${NC}"
fi

# Check HTTPS (if certificate exists)
if [ -f "/etc/letsencrypt/live/forextrade.litigataxcounsel.com/fullchain.pem" ]; then
    echo -e "${YELLOW}Checking HTTPS...${NC}"
    if curl -f -k https://localhost/health &>/dev/null; then
        echo -e "${GREEN}✅ HTTPS is working${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTPS might need a few moments to start${NC}"
    fi
fi

# Setup auto-renewal for SSL certificate
if [ -f "/etc/letsencrypt/live/forextrade.litigataxcounsel.com/fullchain.pem" ]; then
    echo -e "${BLUE}🔄 Setting up SSL certificate auto-renewal...${NC}"
    
    # Create renewal script
    cat > /tmp/renew-ssl.sh << 'EOF'
#!/bin/bash
cd /opt/forex-strategist
docker-compose -f docker-compose.prod.yml --profile certbot run --rm certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
EOF
    
    sudo mv /tmp/renew-ssl.sh /usr/local/bin/renew-ssl.sh
    sudo chmod +x /usr/local/bin/renew-ssl.sh
    
    # Add to crontab (check twice daily as recommended by Let's Encrypt)
    RENEWAL_CRON="0 0,12 * * * /usr/local/bin/renew-ssl.sh > /var/log/forex-strategist/ssl-renewal.log 2>&1"
    (crontab -l 2>/dev/null | grep -v renew-ssl.sh; echo "$RENEWAL_CRON") | crontab -
    
    echo -e "${GREEN}✅ SSL auto-renewal configured${NC}"
fi

# Final status
echo ""
echo -e "${GREEN}🎉 SSL Fix Deployment completed!${NC}"
echo "============================================="
echo -e "${BLUE}📊 Deployment Status:${NC}"
echo "   🌐 Domain: forextrade.litigataxcounsel.com"
echo "   🔗 HTTP:  http://forextrade.litigataxcounsel.com"

if [ -f "/etc/letsencrypt/live/forextrade.litigataxcounsel.com/fullchain.pem" ]; then
    echo "   🔒 HTTPS: https://forextrade.litigataxcounsel.com ✅"
    echo "   📱 API:   https://forextrade.litigataxcounsel.com/api/v1"
    echo "   🏥 Health: https://forextrade.litigataxcounsel.com/api/v1/health"
else
    echo "   🔒 HTTPS: Not configured (certificate request failed)"
    echo "   📱 API:   http://forextrade.litigataxcounsel.com/api/v1"
    echo "   🏥 Health: http://forextrade.litigataxcounsel.com/api/v1/health"
fi

echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Test the website: https://forextrade.litigataxcounsel.com"
echo "2. Monitor logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "3. Check SSL status: curl -I https://forextrade.litigataxcounsel.com"
echo ""
echo -e "${GREEN}🔧 Management Commands:${NC}"
echo "   Start:   docker-compose -f docker-compose.prod.yml up -d"
echo "   Stop:    docker-compose -f docker-compose.prod.yml down"
echo "   Logs:    docker-compose -f docker-compose.prod.yml logs -f [service]"
echo "   SSL Renew: /usr/local/bin/renew-ssl.sh"