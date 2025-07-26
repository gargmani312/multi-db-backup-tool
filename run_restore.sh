#!/bin/bash

# Usage:
# ./restore_db.sh postgres mydb myuser secret localhost 5432 ./db_backups/mydb_backup.sql
# ./restore_db.sh mysql mydb root secret localhost 3306 ./db_backups/mydb_backup.sql
# Optional: add --force to drop and recreate database before restore

DB_TYPE=$1
DB_NAME=$2
DB_USER=$3
DB_PASSWORD=$4
DB_HOST=$5
DB_PORT=$6
SQL_FILE=$7
FORCE_FLAG=$8  # Optional: "--force" to drop and recreate DB

if [ "$#" -lt 7 ]; then
    echo "Usage: $0 <db_type> <db_name> <db_user> <db_password> <db_host> <db_port> <sql_file> [--force]"
    exit 1
fi

# Base Python restore command
COMMAND="python3 restore_db.py \
    --db-type \"$DB_TYPE\" \
    --db-name \"$DB_NAME\" \
    --db-user \"$DB_USER\" \
    --db-password \"$DB_PASSWORD\" \
    --db-host \"$DB_HOST\" \
    --db-port \"$DB_PORT\" \
    --sql-file \"$SQL_FILE\""

# Add force flag if provided
if [ "$FORCE_FLAG" == "--force" ]; then
    COMMAND="$COMMAND --force-recreate"
fi

# Run restore
eval $COMMAND
