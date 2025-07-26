import subprocess
import os
import datetime
import glob
import argparse
from pathlib import Path


class GenericDBBackup:
    def __init__(self, args):
        self.DB_TYPE = args.db_type.lower()
        self.DB_NAME = args.db_name
        self.DB_USER = args.db_user
        self.DB_HOST = args.db_host
        self.DB_PORT = args.db_port or (
            "5432" if self.DB_TYPE == "postgres" else "3306"
        )
        self.DB_PASSWORD = args.db_password
        self.ZIP_PASSWORD = args.zip_password
        self.BACKUP_DIR = Path(args.backup_dir or "./db_backups")
        self.MAX_BACKUPS = args.max_backups

    def _cleanup_old_backups(self):
        backup_files = sorted(
            glob.glob(f"{self.BACKUP_DIR}/backup_{self.DB_TYPE}_{self.DB_NAME}_*.zip"),
            key=os.path.getmtime,
        )
        while len(backup_files) >= self.MAX_BACKUPS:
            oldest_file = backup_files.pop(0)
            os.remove(oldest_file)
            print(f"🗑 Deleted old backup: {oldest_file}")

    def _get_backup_command(self, backup_file):
        if self.DB_TYPE == "postgres":
            return (
                f"PGPASSWORD='{self.DB_PASSWORD}' pg_dump "
                f"-U {self.DB_USER} -h {self.DB_HOST} -p {self.DB_PORT} "
                f"-d {self.DB_NAME} > {backup_file}"
            )
        elif self.DB_TYPE == "mysql":
            return (
                f"mysqldump -u {self.DB_USER} -p'{self.DB_PASSWORD}' "
                f"-h {self.DB_HOST} -P {self.DB_PORT} {self.DB_NAME} > {backup_file}"
            )
        else:
            raise ValueError(f"Unsupported DB_TYPE: {self.DB_TYPE}")

    def backup_database(self):
        os.makedirs(self.BACKUP_DIR, exist_ok=True)
        self._cleanup_old_backups()

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = (
            f"{self.BACKUP_DIR}/backup_{self.DB_TYPE}_{self.DB_NAME}_{timestamp}.sql"
        )
        zip_file = (
            f"{self.BACKUP_DIR}/backup_{self.DB_TYPE}_{self.DB_NAME}_{timestamp}.zip"
        )

        # Run backup command
        command = self._get_backup_command(backup_file)
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"✅ {self.DB_TYPE.capitalize()} backup completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error occurred during backup: {e}")
            return

        # Zip the backup
        try:
            zip_command = f"zip -j -P {self.ZIP_PASSWORD} {zip_file} {backup_file}"
            subprocess.run(zip_command, shell=True, check=True)
            os.remove(backup_file)
            print(f"✅ Backup compressed and saved as {zip_file}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error occurred during zipping: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generic DB Backup Script (MySQL & PostgreSQL)"
    )
    parser.add_argument(
        "--db-type", required=True, choices=["postgres", "mysql"], help="Database type"
    )
    parser.add_argument("--db-name", required=True, help="Database name")
    parser.add_argument("--db-user", required=True, help="Database user")
    parser.add_argument("--db-password", required=True, help="Database password")
    parser.add_argument(
        "--db-host", default="localhost", help="Database host (default: localhost)"
    )
    parser.add_argument(
        "--db-port", help="Database port (default: 5432 for Postgres, 3306 for MySQL)"
    )
    parser.add_argument(
        "--zip-password", default="backup123", help="Password for zip file"
    )
    parser.add_argument(
        "--backup-dir", default="./db_backups", help="Directory to store backups"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    db_backup = GenericDBBackup(args)
    db_backup.backup_database()
