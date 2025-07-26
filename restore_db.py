import subprocess
import argparse
import os


class GenericDBRestore:
    def __init__(self, args):
        self.DB_TYPE = args.db_type.lower()
        self.DB_NAME = args.db_name
        self.DB_USER = args.db_user
        self.DB_PASSWORD = args.db_password
        self.DB_HOST = args.db_host
        self.DB_PORT = args.db_port or (
            "5432" if self.DB_TYPE == "postgres" else "3306"
        )
        self.SQL_FILE = args.sql_file

        if not os.path.exists(self.SQL_FILE):
            raise FileNotFoundError(f"SQL file not found: {self.SQL_FILE}")

    def _create_database_command(self):
        if self.DB_TYPE == "postgres":
            return (
                f"PGPASSWORD='{self.DB_PASSWORD}' psql "
                f"-U {self.DB_USER} -h {self.DB_HOST} -p {self.DB_PORT} "
                f'-c "CREATE DATABASE {self.DB_NAME};"'
            )
        elif self.DB_TYPE == "mysql":
            return (
                f"mysql -u {self.DB_USER} -p'{self.DB_PASSWORD}' "
                f"-h {self.DB_HOST} -P {self.DB_PORT} "
                f'-e "CREATE DATABASE IF NOT EXISTS {self.DB_NAME};"'
            )

    def _restore_command(self):
        if self.DB_TYPE == "postgres":
            return (
                f"PGPASSWORD='{self.DB_PASSWORD}' psql "
                f"-U {self.DB_USER} -h {self.DB_HOST} -p {self.DB_PORT} "
                f"-d {self.DB_NAME} -f {self.SQL_FILE}"
            )
        elif self.DB_TYPE == "mysql":
            return (
                f"mysql -u {self.DB_USER} -p'{self.DB_PASSWORD}' "
                f"-h {self.DB_HOST} -P {self.DB_PORT} {self.DB_NAME} < {self.SQL_FILE}"
            )

    def restore_database(self):
        print(f"🔍 Checking/Creating database {self.DB_NAME}...")
        try:
            subprocess.run(self._create_database_command(), shell=True, check=True)
            print(f"✅ Database {self.DB_NAME} is ready.")
        except subprocess.CalledProcessError:
            print(f"⚠️ Could not create database (may already exist). Continuing...")

        print(f"🔄 Starting restore for {self.DB_TYPE} database: {self.DB_NAME}")
        try:
            subprocess.run(self._restore_command(), shell=True, check=True)
            print(f"✅ Restore completed successfully from {self.SQL_FILE}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error during restore: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generic DB Restore Script (MySQL & PostgreSQL)"
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
        "--sql-file", required=True, help="Path to the .sql file to restore"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    db_restore = GenericDBRestore(args)
    db_restore.restore_database()
