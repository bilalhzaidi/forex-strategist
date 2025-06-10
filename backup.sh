#!/bin/bash

# Forex Trading Advisor - Backup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_DIR="/opt/forex-strategist/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo -e "${BLUE}🗄️  Forex Trading Advisor - Backup Started${NC}"
echo "============================================="
echo "Date: $(date)"
echo "Backup Directory: $BACKUP_DIR"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Function to backup database
backup_database() {
    echo -e "${YELLOW}📦 Backing up PostgreSQL database...${NC}"
    
    # Get database credentials from environment
    source .env
    
    # Create database backup
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump \
        -U forex_user \
        -d forex_strategist \
        --no-password \
        --verbose \
        --format=custom \
        --compress=9 \
        > "$BACKUP_DIR/database_$DATE.dump"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database backup completed: database_$DATE.dump${NC}"
        
        # Compress the backup
        gzip "$BACKUP_DIR/database_$DATE.dump"
        echo -e "${GREEN}✅ Database backup compressed${NC}"
    else
        echo -e "${RED}❌ Database backup failed${NC}"
        return 1
    fi
}

# Function to backup application data
backup_app_data() {
    echo -e "${YELLOW}📁 Backing up application data...${NC}"
    
    # Create application data backup
    tar -czf "$BACKUP_DIR/app_data_$DATE.tar.gz" \
        -C /opt/forex-strategist \
        data/ \
        .env \
        2>/dev/null || true
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Application data backup completed: app_data_$DATE.tar.gz${NC}"
    else
        echo -e "${RED}❌ Application data backup failed${NC}"
        return 1
    fi
}

# Function to backup logs
backup_logs() {
    echo -e "${YELLOW}📋 Backing up logs...${NC}"
    
    # Create logs backup
    tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" \
        -C /var/log \
        forex-strategist/ \
        2>/dev/null || true
    
    echo -e "${GREEN}✅ Logs backup completed: logs_$DATE.tar.gz${NC}"
}

# Function to backup Docker volumes
backup_docker_volumes() {
    echo -e "${YELLOW}🐳 Backing up Docker volumes...${NC}"
    
    # Backup postgres data volume
    docker run --rm \
        -v forex-strategist_postgres_data:/data \
        -v "$BACKUP_DIR:/backup" \
        alpine tar czf "/backup/postgres_volume_$DATE.tar.gz" -C /data .
    
    # Backup redis data volume
    docker run --rm \
        -v forex-strategist_redis_data:/data \
        -v "$BACKUP_DIR:/backup" \
        alpine tar czf "/backup/redis_volume_$DATE.tar.gz" -C /data .
    
    echo -e "${GREEN}✅ Docker volumes backup completed${NC}"
}

# Function to create system info snapshot
backup_system_info() {
    echo -e "${YELLOW}📊 Creating system info snapshot...${NC}"
    
    cat > "$BACKUP_DIR/system_info_$DATE.txt" << EOF
Forex Trading Advisor - System Info Snapshot
Generated: $(date)

=== System Information ===
Hostname: $(hostname)
OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
Kernel: $(uname -r)
Uptime: $(uptime)

=== Docker Information ===
Docker Version: $(docker --version)
Docker Compose Version: $(docker-compose --version)

=== Container Status ===
$(docker-compose -f docker-compose.prod.yml ps)

=== Disk Usage ===
$(df -h)

=== Memory Usage ===
$(free -h)

=== Network Configuration ===
$(ip addr show)

=== Environment Variables (sanitized) ===
ENVIRONMENT=$ENVIRONMENT
DEBUG=$DEBUG
DOMAIN=$DOMAIN
$(env | grep -E '^(ALPHA_VANTAGE|NEWS_API)' | sed 's/=.*/=***/')
EOF
    
    echo -e "${GREEN}✅ System info snapshot created: system_info_$DATE.txt${NC}"
}

# Function to cleanup old backups
cleanup_old_backups() {
    echo -e "${YELLOW}🧹 Cleaning up old backups (older than $RETENTION_DAYS days)...${NC}"
    
    # Find and delete old backup files
    OLD_BACKUPS=$(find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS)
    
    if [ -n "$OLD_BACKUPS" ]; then
        echo "$OLD_BACKUPS" | while read file; do
            echo "Deleting: $file"
            rm "$file"
        done
        echo -e "${GREEN}✅ Old backups cleaned up${NC}"
    else
        echo -e "${BLUE}ℹ️  No old backups to clean up${NC}"
    fi
}

# Function to verify backups
verify_backups() {
    echo -e "${YELLOW}🔍 Verifying backup integrity...${NC}"
    
    # Check if backup files exist and are not empty
    BACKUP_FILES=(
        "database_$DATE.dump.gz"
        "app_data_$DATE.tar.gz"
        "logs_$DATE.tar.gz"
        "postgres_volume_$DATE.tar.gz"
        "redis_volume_$DATE.tar.gz"
        "system_info_$DATE.txt"
    )
    
    ALL_GOOD=true
    for file in "${BACKUP_FILES[@]}"; do
        if [ -f "$BACKUP_DIR/$file" ] && [ -s "$BACKUP_DIR/$file" ]; then
            echo -e "${GREEN}✅ $file - OK${NC}"
        else
            echo -e "${RED}❌ $file - MISSING OR EMPTY${NC}"
            ALL_GOOD=false
        fi
    done
    
    if [ "$ALL_GOOD" = true ]; then
        echo -e "${GREEN}✅ All backups verified successfully${NC}"
    else
        echo -e "${RED}❌ Some backups are missing or corrupted${NC}"
        return 1
    fi
}

# Function to send backup notification (optional)
send_notification() {
    echo -e "${YELLOW}📧 Sending backup notification...${NC}"
    
    # Calculate backup sizes
    TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
    BACKUP_COUNT=$(ls -1 $BACKUP_DIR/*_$DATE.* | wc -l)
    
    # If you have a notification service configured, send notification here
    # For example, using curl to send to a webhook:
    # curl -X POST "your-webhook-url" \
    #      -H "Content-Type: application/json" \
    #      -d "{\"message\": \"Forex Trading Advisor backup completed. Files: $BACKUP_COUNT, Total size: $TOTAL_SIZE\"}"
    
    echo -e "${BLUE}ℹ️  Backup notification would be sent here if configured${NC}"
}

# Main backup execution
main() {
    echo -e "${BLUE}🚀 Starting backup process...${NC}"
    
    # Change to project directory
    cd /opt/forex-strategist
    
    # Perform backups
    backup_database || echo -e "${RED}⚠️  Database backup failed${NC}"
    backup_app_data || echo -e "${RED}⚠️  App data backup failed${NC}"
    backup_logs || echo -e "${RED}⚠️  Logs backup failed${NC}"
    backup_docker_volumes || echo -e "${RED}⚠️  Docker volumes backup failed${NC}"
    backup_system_info || echo -e "${RED}⚠️  System info backup failed${NC}"
    
    # Verify backups
    if verify_backups; then
        echo -e "${GREEN}✅ Backup verification passed${NC}"
    else
        echo -e "${RED}❌ Backup verification failed${NC}"
        exit 1
    fi
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Send notification
    send_notification
    
    # Final summary
    echo ""
    echo -e "${GREEN}🎉 Backup completed successfully!${NC}"
    echo "======================================="
    echo "Date: $(date)"
    echo "Backup Location: $BACKUP_DIR"
    echo "Files Created:"
    ls -la $BACKUP_DIR/*_$DATE.* | while read line; do
        echo "  $line"
    done
    echo ""
    echo "Total Backup Size: $(du -sh $BACKUP_DIR | cut -f1)"
    echo "Available Disk Space: $(df -h $BACKUP_DIR | tail -1 | awk '{print $4}')"
    echo ""
    echo -e "${BLUE}📋 To restore from backup, use the restore.sh script${NC}"
}

# Execute main function
main "$@"