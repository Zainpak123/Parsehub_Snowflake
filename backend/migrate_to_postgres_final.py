import sqlite3
import os
from dotenv import load_dotenv
from pathlib import Path
import re
from urllib.parse import urlparse

# Load environment variables
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path)
load_dotenv()

# Strategy: Try psycopg2 first, fallback to pg8000
try:
    import psycopg2
    from psycopg2.extras import execute_values
    HAS_PSYCOPG2 = True
except ImportError:
    try:
        import pg8000
        HAS_PSYCOPG2 = False
    except ImportError:
        print("Error: Neither 'psycopg2-binary' nor 'pg8000' is installed.")
        exit(1)

SQLITE_DB = os.getenv('DATABASE_PATH', 'parsehub.db')
POSTGRES_URL = os.getenv('DATABASE_URL')

if not POSTGRES_URL:
    print("Error: DATABASE_URL not found in environment.")
    exit(1)

# Smart SQLite path resolution
if not os.path.isabs(SQLITE_DB):
    script_relative = Path(__file__).parent / SQLITE_DB
    just_filename = Path(SQLITE_DB).name
    direct_relative = Path(__file__).parent / just_filename
    
    if direct_relative.exists():
        SQLITE_DB = str(direct_relative)
    elif script_relative.exists():
        SQLITE_DB = str(script_relative)
    else:
        SQLITE_DB = str(script_relative)

print(f"Starting Migration...")
print(f"Source: {SQLITE_DB}")

def migrate():
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()

        if HAS_PSYCOPG2:
            pg_conn = psycopg2.connect(POSTGRES_URL)
            pg_conn.autocommit = True
            pg_cursor = pg_conn.cursor()
        else:
            import pg8000
            url = urlparse(POSTGRES_URL)
            pg_conn = pg8000.connect(
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port,
                database=url.path[1:]
            )
            pg_conn.autocommit = True
            pg_cursor = pg_conn.cursor()

        print("Preparing PostgreSQL schema...")
        sql_path = Path(__file__).parent / "init_postgres.sql"
        if sql_path.exists():
            with open(sql_path, 'r') as f:
                schema_sql = f.read()
                table_names = re.findall(r'CREATE TABLE IF NOT EXISTS (\w+)', schema_sql)
                for table in reversed(table_names):
                    pg_cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                
                for statement in schema_sql.split(';'):
                    if statement.strip():
                        statement = statement.replace('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT false')
                        statement = statement.replace('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT true')
                        pg_cursor.execute(statement)
            print("Schema recreated.")

        # Tables in order of migration (parents first)
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

        # Verify tables exist in SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
        tables = [t for t in tables if t in existing_sqlite_tables]


        for table in tables:
            print(f"Migrating table: {table}")
            
            # Identify numeric columns for this table
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            table_info = sqlite_cursor.fetchall()
            int_cols = set()
            float_cols = set()
            for cid, col_name, col_type, notnull, dflt, pk in table_info:
                t = col_type.upper()
                if 'INT' in t:
                    int_cols.add(col_name)
                elif 'REAL' in t or 'NUMERIC' in t or 'FLOAT' in t:
                    float_cols.add(col_name)


            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            if not rows:
                print(f"Table {table} is empty.")
                continue

            print(f"Transferring {len(rows)} records...")
            columns = rows[0].keys()
            col_names = ",".join(columns)
            placeholders = ",".join(["%s"] * len(columns))
            
            data = []
            for row in rows:
                clean_row = []
                for col in columns:
                    val = row[col]
                    val_str = str(val).strip().lower() if val is not None else ""
                    
                    if col in int_cols:
                        if val is None or val == '' or val_str == 'n/a' or val_str == 'nan':
                            clean_row.append(None)
                        elif val_str == 'true':
                            clean_row.append(1)
                        elif val_str == 'false':
                            clean_row.append(0)
                        else:
                            try:
                                # Force to int
                                clean_val = str(val).replace(',', '').strip()
                                clean_row.append(int(float(clean_val)))
                            except:
                                clean_row.append(None)
                    elif col in float_cols:
                        if val is None or val == '' or val_str == 'n/a' or val_str == 'nan':
                            clean_row.append(None)
                        else:
                            try:
                                clean_val = str(val).replace(',', '').strip()
                                clean_row.append(float(clean_val))
                            except:
                                clean_row.append(None)
                    else:
                        clean_row.append(val)

                data.append(tuple(clean_row))


            try:
                if HAS_PSYCOPG2:
                    query = f"INSERT INTO {table} ({col_names}) VALUES %s"
                    execute_values(pg_cursor, query, data)
                else:
                    for i in range(0, len(data), 1000):
                        batch = data[i:i+1000]
                        v_placeholders = ",".join([f"({placeholders})" for _ in range(len(batch))])
                        batch_query = f"INSERT INTO {table} ({col_names}) VALUES {v_placeholders}"
                        flat_data = []
                        for row_tuple in batch:
                            flat_data.extend(row_tuple)
                        pg_cursor.execute(batch_query, flat_data)


            except Exception as e:
                print(f"FAILED on table {table}")
                print(f"Error: {e}")
                # Print first row of batch for debugging
                if len(data) > 0:
                    print(f"Sample data row 0: {data[0]}")
                raise e


            
            try:
                pg_cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table}")
            except:
                pass 
            print(f"Table {table} migrated.")

        print("\nMigration Complete!")
        sqlite_conn.close()
        pg_conn.close()

    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
