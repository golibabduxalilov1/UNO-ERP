#!/bin/bash
# PostgreSQL kunlik backup skripti
# Cron uchun: 0 2 * * * /path/to/backup.sh

DB_NAME="mebel_db"
DB_USER="postgres"
BACKUP_DIR="/var/backups/mebel"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mebel_backup_$DATE.sql.gz"

mkdir -p "$BACKUP_DIR"
pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

# 30 kundan eski backuplarni o'chirish
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete

echo "Backup yaratildi: $BACKUP_FILE"
