# ✅ Deployment Checklist for Hetzner

**Server:** `138.199.197.89`  
**Domain:** `forextrade.litigataxcounsel.com`  
**Email:** `bilalhzaidi@gmail.com`

## Pre-Deployment Setup

### 1. DNS Configuration ⏳
**Point your domain to the server:**

**DNS Records to Add:**
```
Type: A
Name: forextrade
Value: 138.199.197.89
TTL: 300

Type: A  
Name: www
Value: 138.199.197.89
TTL: 300
```

**Verify DNS (wait 5-30 minutes after DNS changes):**
```bash
nslookup forextrade.litigataxcounsel.com
# Expected: 138.199.197.89

dig forextrade.litigataxcounsel.com
# Expected: 138.199.197.89
```

### 2. Server Access ✅
```bash
ssh root@138.199.197.89
```

### 3. API Keys Ready 📋
- [ ] Alpha Vantage API key (get from: https://www.alphavantage.co/support/#api-key)
- [ ] News API key (optional, get from: https://newsapi.org/register)

## Deployment Steps

### Step 1: Initial Server Setup
```bash
# SSH into server
ssh root@138.199.197.89

# Create deployment user
adduser bilal
usermod -aG sudo bilal
su - bilal

# Update system
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl
```

### Step 2: Deploy Application
```bash
# Clone repository (you'll need to upload your files or create a repo)
# For now, create project directory
sudo mkdir -p /opt/forex-strategist
sudo chown bilal:bilal /opt/forex-strategist
cd /opt/forex-strategist

# Upload your forex-strategist files here
# Then run:
chmod +x deploy-hetzner.sh
./deploy-hetzner.sh
```

### Step 3: Configure Environment
```bash
# Edit environment file
nano .env

# Required configuration:
POSTGRES_PASSWORD=Generate_Secure_Password_123!
REDIS_PASSWORD=Generate_Secure_Redis_Password_456!
SECRET_KEY=Generate_Super_Secure_Secret_Key_789!
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
NEWS_API_KEY=your_news_api_key_here

# Pre-configured:
EMAIL=bilalhzaidi@gmail.com
DOMAIN=forextrade.litigataxcounsel.com
ENVIRONMENT=production
DEBUG=False
```

### Step 4: Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Step 5: Start Services
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Wait for SSL certificate generation (2-3 minutes)
sleep 180

# Check services
docker-compose -f docker-compose.prod.yml ps
```

## Verification Checklist

### ✅ DNS & Network
- [ ] Domain resolves to `138.199.197.89`
- [ ] Port 80 accessible: `curl http://138.199.197.89`
- [ ] Port 443 accessible: `curl https://138.199.197.89`

### ✅ Services
- [ ] All containers running: `docker-compose -f docker-compose.prod.yml ps`
- [ ] Backend health: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend accessible: `curl http://localhost:80/health`
- [ ] Database connected: `docker-compose exec postgres psql -U forex_user -d forex_strategist -c "SELECT 1;"`

### ✅ SSL Certificate
- [ ] Certificate generated: `docker-compose logs certbot`
- [ ] HTTPS works: `curl -I https://forextrade.litigataxcounsel.com`
- [ ] SSL grade A: Test at https://www.ssllabs.com/ssltest/
- [ ] Auto-renewal configured: `crontab -l`

### ✅ Application
- [ ] Frontend loads: https://forextrade.litigataxcounsel.com
- [ ] API responds: https://forextrade.litigataxcounsel.com/api/v1/health
- [ ] Currency pair analysis works
- [ ] Error handling works (try invalid requests)

### ✅ Performance
- [ ] Response time < 2 seconds
- [ ] Gzip compression enabled
- [ ] Static files cached properly
- [ ] Database queries optimized

### ✅ Monitoring
- [ ] Logs accessible: `docker-compose logs -f`
- [ ] Metrics endpoint: `curl localhost:8000/metrics` (dev only)
- [ ] Health checks passing
- [ ] Backup script works: `./backup.sh`

## Post-Deployment

### Email Notifications Setup
You should receive emails at `bilalhzaidi@gmail.com` for:
- SSL certificate generation confirmation
- SSL renewal notifications
- Any critical system alerts

### Monitoring Commands
```bash
# Check all services
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f [service_name]

# Check SSL certificate
openssl s_client -connect forextrade.litigataxcounsel.com:443 -servername forextrade.litigataxcounsel.com

# Monitor resources
docker stats

# Check disk space
df -h

# View system logs
sudo journalctl -f
```

### Backup Verification
```bash
# Run manual backup
./backup.sh

# Check backup files
ls -la /opt/forex-strategist/backups/

# Test backup restoration (dry run)
# ./restore.sh --dry-run latest_backup.tar.gz
```

## Troubleshooting

### Common Issues

**DNS not resolving:**
```bash
# Check DNS propagation
nslookup forextrade.litigataxcounsel.com 8.8.8.8
dig @8.8.8.8 forextrade.litigataxcounsel.com
```

**SSL certificate issues:**
```bash
# Check certificate generation logs
docker-compose logs certbot

# Manual certificate generation
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot --email bilalhzaidi@gmail.com -d forextrade.litigataxcounsel.com --agree-tos
```

**Application not responding:**
```bash
# Check container status
docker-compose ps

# Check backend logs
docker-compose logs backend

# Check database connection
docker-compose exec postgres psql -U forex_user -d forex_strategist
```

**Performance issues:**
```bash
# Check resource usage
htop
docker stats

# Check database performance
docker-compose exec postgres psql -U forex_user -d forex_strategist -c "SELECT * FROM pg_stat_activity;"
```

## Success Criteria

### ✅ Deployment Successful When:
1. **HTTPS works:** https://forextrade.litigataxcounsel.com shows green lock
2. **API responds:** https://forextrade.litigataxcounsel.com/api/v1/health returns 200
3. **Analysis works:** Can successfully analyze currency pairs
4. **SSL grade A:** Passes SSL security tests
5. **Performance good:** Page load < 3 seconds
6. **Monitoring active:** Logs and metrics accessible

**Final Test URL:** https://forextrade.litigataxcounsel.com

**API Test:** https://forextrade.litigataxcounsel.com/api/v1/supported-pairs