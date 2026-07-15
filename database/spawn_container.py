#!/usr/bin/env python3

from pathlib import Path
import psycopg2

SCRIPT_DIR = Path(__file__).parent

CREATE_SQL_FILES = [
    "create_users.sql",
    "create_products.sql",
    "create_orders.sql",
    "create_order_products.sql",
    "create_files.sql",
]

DATA_SQL_FILES = [
    "add_users.sql",
    "add_products.sql",
    "add_orders.sql",
    "add_order_products.sql",
]


def reset_database(cursor):
    """Drop and recreate the public schema."""

    print("Resetting database...")

    cursor.execute("""
        DROP SCHEMA IF EXISTS public CASCADE;
        CREATE SCHEMA public;

        GRANT ALL ON SCHEMA public TO test;
        GRANT ALL ON SCHEMA public TO public;
    """)

    print("Database reset completed.")


def execute_sql_scripts(cursor, script_names, description):
    """Execute SQL scripts stored next to this script."""

    for file_name in script_names:
        script_path = SCRIPT_DIR / file_name

        if not script_path.exists():
            raise FileNotFoundError(f"SQL file not found: {script_path}")

        print(f"{description}: {file_name}")

        with open(script_path, "r", encoding="utf-8") as f:
            sql_script = f.read()

        cursor.execute(sql_script)


def refresh_database():
    """Reset database and recreate schema/data."""

    conn = None

    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="test",
            password="test",
            database="performance_test",
        )

        conn.autocommit = False

        cursor = conn.cursor()

        reset_database(cursor)

        print("Creating schema...")
        execute_sql_scripts(
            cursor,
            CREATE_SQL_FILES,
            "Executing create script",
        )

        print("Loading data...")
        execute_sql_scripts(
            cursor,
            DATA_SQL_FILES,
            "Executing data script",
        )

        conn.commit()

        cursor.close()

        print("Database refreshed successfully.")

    except Exception:
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()


def wait_for_postgres_to_be_ready():
    """Wait until PostgreSQL accepts connections."""

    max_attempts = 30

    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="test",
                password="test",
                database="performance_test",
            )
            conn.close()

            print("PostgreSQL is ready.")
            return

        except psycopg2.OperationalError as e:
            print(f"Waiting for PostgreSQL ({attempt}/{max_attempts})...")
            print(e)
            time.sleep(2)

    raise RuntimeError("PostgreSQL did not become ready in time.")

def main():
    try:
        wait_for_postgres_to_be_ready()
        
        refresh_database()

    except Exception as e:
        print(f"\nDatabase refresh failed: {e}")
        raise


if __name__ == "__main__":
    main()