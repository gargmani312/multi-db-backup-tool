#!/bin/bash

# Usage:
# ./backup_db.sh postgres mydb myuser secret localhost 5432 myzip123 ./backups
# ./backup_db.sh mysql mydb root secret localhost 3306 myzip123 ./mysql_backups

DB_TYPE=$1
DB_NAME=$2
DB_USER=$3
DB_PASSWORD=$4
DB_HOST=$5
DB_PORT=$6
ZIP_PASSWORD=$7
BACKUP_DIR=$8

# Check if arguments are provided
if [ "$#" -lt 9 ]; then
    echo "Usage: $0 <db_type> <db_name> <db_user> <db_password> <db_host> <db_port> <zip_password> <backup_dir>"
    exit 1
fi

# Run Python backup script
python3 db_backup.py \
    --db-type "$DB_TYPE" \
    --db-name "$DB_NAME" \
    --db-user "$DB_USER" \
    --db-password "$DB_PASSWORD" \
    --db-host "$DB_HOST" \
    --db-port "$DB_PORT" \
    --zip-password "$ZIP_PASSWORD" \
    --backup-dir "$BACKUP_DIR" \
    --max-backups "$MAX_BACKUPS"
