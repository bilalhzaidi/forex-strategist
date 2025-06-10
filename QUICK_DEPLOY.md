# 🚀 Quick Deployment Guide for Hetzner

**Domain:** `forextrade.litigataxcounsel.com`  
**Server IP:** `138.199.197.89`  
**Email:** `bilalhzaidi@gmail.com`

## Step 1: Server Setup (5 minutes)

```bash
# 1. SSH into your Hetzner server
ssh root@138.199.197.89

# 2. Create user and setup
adduser bilal
usermod -aG sudo bilal
su - bilal

# 3. Update system
sudo apt update && sudo apt upgrade -y
```

## Step 2: Point Domain (DNS Configuration)

**In your domain registrar (e.g., GoDaddy, Namecheap):**

```
Type: A Record
Name: forextrade (or @)
Value: 138.199.197.89
TTL: 300 seconds
```

**Test DNS propagation:**
```bash
nslookup forextrade.litigataxcounsel.com
# Should return 138.199.197.89
```

## Step 3: Deploy Application (10 minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/forex-strategist.git
cd forex-strategist

# 2. Make scripts executable
chmod +x deploy-hetzner.sh backup.sh

# 3. Deploy (this will install Docker, generate SSL, etc.)
./deploy-hetzner.sh
```

**During deployment:**
- Choose **"y"** for Docker installation
- Choose **"y"** for Let's Encrypt SSL
- Configure your API keys in `.env` when prompted

## Step 4: Configure API Keys

**Edit environment file:**
```bash
nano .env
```

**Required changes:**
```env
# Generate secure passwords
POSTGRES_PASSWORD=your_secure_database_password_123!
REDIS_PASSWORD=your_secure_redis_password_456!
SECRET_KEY=your_super_secure_secret_key_789!

# Get your API keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key

# Pre-configured for you
EMAIL=bilalhzaidi@gmail.com
DOMAIN=forextrade.litigataxcounsel.com
```

## Step 5: Get API Keys

### Alpha Vantage (Required - Free)
1. Visit: https://www.alphavantage.co/support/#api-key
2. Sign up with email: `bilalhzaidi@gmail.com`
3. Get your free API key (25 requests/day)
4. Add to `.env` file

### News API (Optional - Free)
1. Visit: https://newsapi.org/register
2. Sign up with email: `bilalhzaidi@gmail.com`
3. Get your free API key (500 requests/day)
4. Add to `.env` file

## Step 6: Final Deployment

```bash
# After configuring .env, restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Wait 2 minutes for SSL generation
sleep 120

# Test your site
curl -I https://forextrade.litigataxcounsel.com
```

## ✅ Verification Checklist

- [ ] Domain points to server IP
- [ ] HTTPS works: https://forextrade.litigataxcounsel.com
- [ ] API responds: https://forextrade.litigataxcounsel.com/api/v1/health
- [ ] SSL certificate is valid (green lock icon)
- [ ] Application loads and functions

## 🔧 Management Commands

```bash
# View all services
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Restart application
docker-compose -f docker-compose.prod.yml restart

# Manual backup
./backup.sh

# Update application
git pull && docker-compose -f docker-compose.prod.yml up -d --build
```

## 📞 Support

**If something goes wrong:**

1. **Check DNS:**
   ```bash
   nslookup forextrade.litigataxcounsel.com
   ```

2. **Check services:**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

3. **Check logs:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs backend
   ```

4. **Check SSL:**
   ```bash
   curl -I https://forextrade.litigataxcounsel.com
   ```

**Email configured:** `bilalhzaidi@gmail.com`  
**SSL notifications will be sent to this email**

## 🎯 Final Result

Your Forex Trading Advisor will be live at:
- **🌐 Website:** https://forextrade.litigataxcounsel.com
- **🔧 API:** https://forextrade.litigataxcounsel.com/api/v1
- **🏥 Health:** https://forextrade.litigataxcounsel.com/api/v1/health

**Total deployment time:** ~15-20 minutes