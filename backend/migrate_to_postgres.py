import sqlite3
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path)
load_dotenv()

# Strategy: Try psycopg2 first, fallback to pg8000 (pure python)
try:
    import psycopg2
    from psycopg2.extras import execute_values
    HAS_PSYCOPG2 = True
except ImportError:
    try:
        import pg8000
        HAS_PSYCOPG2 = False
    except ImportError:
        print("❌ Error: Neither 'psycopg2-binary' nor 'pg8000' is installed.")
        print("💡 Tip: Run 'pip install pg8000' (it's much easier to install on Windows)")
        exit(1)


SQLITE_DB = os.getenv('DATABASE_PATH', 'parsehub.db')
POSTGRES_URL = os.getenv('DATABASE_URL')

if not POSTGRES_URL:
    print("❌ Error: DATABASE_URL not found in environment.")
    exit(1)

# Smart SQLite path resolution
# If it's a relative path, first try relative to script, then relative to project root
if not os.path.isabs(SQLITE_DB):
    script_relative = Path(__file__).parent / SQLITE_DB
    # If DATABASE_PATH is "backend/parsehub.db" and script is in "backend/", 
    # we should check for "parsehub.db" directly too.
    just_filename = Path(SQLITE_DB).name
    direct_relative = Path(__file__).parent / just_filename
    
    if direct_relative.exists():
        SQLITE_DB = str(direct_relative)
    elif script_relative.exists():
        SQLITE_DB = str(script_relative)
    else:
        # Fallback to whatever was provided
        SQLITE_DB = str(script_relative)


print(f"Starting Migration...")
print(f"Source (SQLite): {SQLITE_DB}")
print(f"Target (Postgres): {POSTGRES_URL.split('@')[-1]}")

def migrate():
    try:
        # Connect to databases
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()

        if HAS_PSYCOPG2:
            pg_conn = psycopg2.connect(POSTGRES_URL)
            pg_conn.autocommit = True
            pg_cursor = pg_conn.cursor()
        else:
            # pg8000 connection
            import pg8000
            # Parse URL to components for pg8000 if needed, but pg8000.connect supports some URL-like strings or manual params
            # Most reliable: parse the URL manually
            from urllib.parse import urlparse
            url = urlparse(POSTGRES_URL)
            pg_conn = pg8000.connect(
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port,
                database=url.path[1:] # strip leading /
            )
            pg_conn.autocommit = True
            pg_cursor = pg_conn.cursor()

        # Step 0: Initialize PostgreSQL Schema (Cleanup and Recreate)
        print("Preparing PostgreSQL schema (Drop and Recreate)...")
        sql_path = Path(__file__).parent / "init_postgres.sql"
        if sql_path.exists():
            with open(sql_path, 'r') as f:
                schema_sql = f.read()
                
                # Extract table names from schema to drop them
                import re
                table_names = re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)', schema_sql)
                # Drop in reverse order to respect FKs
                for table in reversed(table_names):
                    pg_cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                
                # Execute schema creation
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        # Fix BOOLEAN DEFAULT 0/1 for PG
                        statement = statement.replace('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT false')
                        statement = statement.replace('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT true')
                        pg_cursor.execute(statement)
            print("Schema recreated.")
        else:
            print("⚠️  Warning: init_postgres.sql not found. Assuming schema already exists.")

        # Define tables in order of migration (parent tables first)
        tables = [

            'projects',
            'import_batches',
            'metadata',
            'project_metadata',
            'runs',
            'scraped_data',
            'metrics',
            'recovery_operations',
            'data_lineage',
            'run_checkpoints',
            'monitoring_sessions',
            'scraped_records',
            'analytics_cache',
            'csv_exports',
            'analytics_records',
            'scraping_sessions',
            'iteration_runs',
            'combined_scraped_data',
            'url_patterns',
            'product_data'
        ]

        for table in tables:
            print(f"--- Migrating table: {table} ---")
            
            # Check if table exists in SQLite
            sqlite_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not sqlite_cursor.fetchone():
                print(f"Table {table} does not exist in SQLite skipping...")
                continue

            # Fetch data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"Table {table} is empty.")
                continue

            print(f"Found {len(rows)} records. Transferring...")

            # Prepare Postgres column names
            columns = rows[0].keys()
            col_names = ",".join(columns)
            placeholders = ",".join(["%s"] * len(columns))
            
            # Prepare data
            data = [tuple(row) for row in rows]

            # Clear existing data in Postgres
            try:
                pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
            except:
                # Fallback if CASCADE or TRUNCATE fails
                pg_cursor.execute(f"DELETE FROM {table}")

            # Insert into Postgres
            if HAS_PSYCOPG2:
                query = f"INSERT INTO {table} ({col_names}) VALUES %s"
                execute_values(pg_cursor, query, data)
            else:
                # pg8000 doesn't have execute_values helper for large batches easily
                # We'll do it in chunks
                query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                for i in range(0, len(data), 100):
                    batch = data[i:i+100]
                    # Convert any potential bad float/none values
                    clean_batch = []
                    for row in batch:
                        clean_row = []
                        for val in row:
                            if isinstance(val, (float, int)) and (val != val): # NaN check
                                clean_row.append(None)
                            else:
                                clean_row.append(val)
                        clean_batch.append(tuple(clean_row))
                    pg_cursor.executemany(query, clean_batch)
            
            # Update sequences (Postgres specific)
            try:
                pg_cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table}")
            except:
                pass 

            print(f"Table {table} migrated successfully.")


        print("\nMigration Complete!")
        
        sqlite_conn.close()
        pg_conn.close()

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
