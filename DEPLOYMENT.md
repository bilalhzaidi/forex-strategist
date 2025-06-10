# 🚀 Forex Trading Advisor - Production Deployment Guide

## Overview

This guide covers deploying the Forex Trading Advisor to a Hetzner server with the domain `forextrade.litigataxcounsel.com`.

## Prerequisites

- Hetzner server (Ubuntu 20.04 LTS or newer recommended)
- Domain pointed to server IP
- SSH access to the server
- Alpha Vantage API key (required)
- News API key (optional but recommended)

## Quick Deployment

### 1. Server Setup

```bash
# Connect to your Hetzner server
ssh root@your-server-ip

# Create deployment user
adduser forex
usermod -aG sudo forex
su - forex

# Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl
```

### 2. Deploy Application

```bash
# Clone repository
git clone https://github.com/yourusername/forex-strategist.git
cd forex-strategist

# Run deployment script
chmod +x deploy-hetzner.sh
./deploy-hetzner.sh
```

The script will:
- Install Docker and Docker Compose
- Set up SSL certificates with Let's Encrypt
- Configure environment variables
- Deploy all services
- Set up automated backups
- Configure monitoring

### 3. Configure Environment

Edit the `.env` file with your actual values:

```bash
nano .env
```

Required variables:
- `POSTGRES_PASSWORD`: Secure database password
- `REDIS_PASSWORD`: Secure Redis password
- `SECRET_KEY`: Secure application secret
- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key
- `NEWS_API_KEY`: Your News API key (optional)

### 4. Point Domain

Point your domain `forextrade.litigataxcounsel.com` to your server's IP address:

**A Record:**
- Name: `@` or `forextrade`
- Value: `your-server-ip`
- TTL: `300`

**CNAME Record (optional):**
- Name: `www`
- Value: `forextrade.litigataxcounsel.com`
- TTL: `300`

## Services

The deployment includes:

### 🌐 Frontend (React)
- **URL**: https://forextrade.litigataxcounsel.com
- **Technology**: React 18 + Tailwind CSS
- **Features**: Responsive UI, PWA support, SEO optimized

### 🔧 Backend (FastAPI)
- **URL**: https://forextrade.litigataxcounsel.com/api/v1
- **Technology**: Python FastAPI + SQLAlchemy
- **Features**: Rate limiting, caching, monitoring, security headers

### 🗄️ Database (PostgreSQL)
- **Technology**: PostgreSQL 15
- **Features**: Automated backups, performance monitoring

### ⚡ Cache (Redis)
- **Technology**: Redis 7
- **Features**: API response caching, session storage

### 🔒 SSL/TLS
- **Technology**: Let's Encrypt + Nginx
- **Features**: Automatic renewal, security headers, HTTP/2

## API Endpoints

### Public Endpoints
- `GET /api/v1/health` - Health check
- `POST /api/v1/analyze` - Analyze currency pair
- `GET /api/v1/rates/{pair}` - Get current rates
- `GET /api/v1/supported-pairs` - List supported pairs

### Admin Endpoints
- `GET /api/v1/system/health` - Detailed health check
- `GET /metrics` - Application metrics (dev only)

## Monitoring & Maintenance

### Health Checks

```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# Check application health
curl https://forextrade.litigataxcounsel.com/api/v1/health

# Check detailed health
curl https://forextrade.litigataxcounsel.com/api/v1/system/health
```

### Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Backups

Automated daily backups are configured at 2 AM UTC:

```bash
# Manual backup
./backup.sh

# View backups
ls -la /opt/forex-strategist/backups/

# Restore from backup (if needed)
# ./restore.sh backup_filename
```

### Updates

```bash
# Pull latest changes
cd /opt/forex-strategist
git pull

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## Performance Optimization

### Resource Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- 1TB bandwidth

**Recommended:**
- 4 CPU cores
- 8GB RAM
- 50GB SSD storage
- Unlimited bandwidth

### Scaling

For high traffic, consider:
- Load balancer with multiple backend instances
- Database read replicas
- CDN for static assets
- Redis cluster for caching

## Security

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### SSL Certificate

SSL certificates are automatically managed by Let's Encrypt:
- Auto-renewal every 60 days
- HTTP to HTTPS redirect
- Security headers configured
- Perfect Forward Secrecy

### Security Headers

All responses include:
- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `X-XSS-Protection`
- `Content-Security-Policy`

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs service_name

# Check disk space
df -h

# Check memory usage
free -h
```

**SSL certificate issues:**
```bash
# Check certificate status
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates

# Force renewal
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --force-renewal
```

**Database connection issues:**
```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Connect to database
docker-compose -f docker-compose.prod.yml exec postgres psql -U forex_user -d forex_strategist
```

### Performance Issues

**High CPU usage:**
- Check for infinite loops in application code
- Monitor external API call rates
- Consider scaling horizontally

**High memory usage:**
- Check for memory leaks
- Adjust container memory limits
- Monitor cache size

**Slow response times:**
- Check database query performance
- Monitor external API response times
- Review caching configuration

## Support

### Logs Location
- Application logs: `/var/log/forex-strategist/`
- Docker logs: `docker-compose logs`
- System logs: `/var/log/syslog`

### Metrics
- System metrics: Available through health endpoints
- Application metrics: `/metrics` endpoint (development)
- Container metrics: `docker stats`

### Contact
For deployment issues or questions:
1. Check logs first
2. Review this documentation
3. Check GitHub issues
4. Contact support

## Environment Variables Reference

### Required
- `POSTGRES_PASSWORD` - Database password
- `SECRET_KEY` - Application secret key
- `ALPHA_VANTAGE_API_KEY` - Alpha Vantage API key

### Optional
- `NEWS_API_KEY` - News API key
- `SENTRY_DSN` - Error tracking
- `REDIS_PASSWORD` - Redis password

### Configuration
- `ENVIRONMENT=production`
- `DEBUG=False`
- `DOMAIN=forextrade.litigataxcounsel.com`