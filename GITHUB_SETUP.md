# 🐙 GitHub Repository Setup Guide

## Step 1: Create GitHub Repository

1. **Go to GitHub:** https://github.com/bilalhzaidi
2. **Click "New repository"** (green button)
3. **Repository settings:**
   ```
   Repository name: forex-strategist
   Description: AI-powered Forex Trading Advisor - Production-ready application with FastAPI backend and React frontend
   Visibility: Public (or Private if you prefer)
   Initialize: Do NOT check any boxes (no README, no .gitignore, no license)
   ```
4. **Click "Create repository"**

## Step 2: Push Your Code

After creating the repository on GitHub, run these commands:

```bash
# Navigate to your project
cd /home/bilal/projects/forex-strategist

# Verify git status
git status

# Push to GitHub
git push -u origin main
```

If you get authentication errors, you'll need to:

### Option A: Use Personal Access Token (Recommended)
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` permissions
3. Use token as password when prompted

### Option B: Use SSH (Alternative)
```bash
# Change remote to SSH
git remote set-url origin git@github.com:bilalhzaidi/forex-strategist.git

# Push with SSH
git push -u origin main
```

## Step 3: Verify Repository

After successful push, verify:
1. **Repository URL:** https://github.com/bilalhzaidi/forex-strategist
2. **Check files are uploaded** (should see all 58 files)
3. **README.md should display** the project information

## Step 4: Deploy to Hetzner

Once your repository is live on GitHub, you can deploy to your Hetzner server:

```bash
# SSH to your Hetzner server
ssh root@138.199.197.89

# Create user (if not done already)
adduser bilal
usermod -aG sudo bilal
su - bilal

# Update system
sudo apt update && sudo apt upgrade -y

# Clone your repository
git clone https://github.com/bilalhzaidi/forex-strategist.git
cd forex-strategist

# Run deployment
chmod +x deploy-hetzner.sh backup.sh
./deploy-hetzner.sh
```

## Repository Structure

Your repository will contain:

```
forex-strategist/
├── backend/                 # FastAPI application
├── frontend/               # React application  
├── docker-compose.prod.yml # Production Docker setup
├── deploy-hetzner.sh      # Deployment script
├── backup.sh              # Backup script
├── nginx-ssl.conf         # Nginx SSL configuration
├── .env.hetzner          # Environment template
├── README.md             # Project documentation
├── DEPLOYMENT.md         # Deployment guide
├── QUICK_DEPLOY.md       # Quick start guide
└── GITHUB_SETUP.md       # This file
```

## Repository URL
**Your repository will be:** https://github.com/bilalhzaidi/forex-strategist

## Deployment Command for Hetzner
Once repository is created, deployment becomes simple:

```bash
# On your Hetzner server (138.199.197.89)
git clone https://github.com/bilalhzaidi/forex-strategist.git
cd forex-strategist
./deploy-hetzner.sh
```

## Benefits of GitHub Deployment

✅ **Version Control:** Track all changes  
✅ **Easy Updates:** `git pull` to update  
✅ **Backup:** Code is safely stored on GitHub  
✅ **Collaboration:** Share with team members  
✅ **Documentation:** README and guides included  
✅ **CI/CD Ready:** Can add automated deployments later  

## Next Steps After Repository Creation

1. **Create repository** on GitHub
2. **Push code** from local machine
3. **Clone on Hetzner** server
4. **Point domain** to 138.199.197.89
5. **Deploy** with `./deploy-hetzner.sh`
6. **Configure API keys**
7. **Go live!** 🚀