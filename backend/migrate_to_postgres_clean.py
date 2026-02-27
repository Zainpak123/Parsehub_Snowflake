mport sqlte3
mport os
from dotenv mport load_dotenv
from pathlb mport Path

# Load envronment varables
dotenv_path = Path(__fle__).parent / ".env"
load_dotenv(dotenv_path)
load_dotenv()

# Strategy: Try psycopg2 frst, fallback to pg8000 (pure python)
try:
    mport psycopg2
    from psycopg2.extras mport execute_values
    HAS_PSYCOPG2 = True
except mportError:
    try:
        mport pg8000
        HAS_PSYCOPG2 = False
    except mportError:
        prnt(" Error: Nether 'psycopg2-bnary' nor 'pg8000' s nstalled.")
        prnt(" Tp: Run 'pp nstall pg8000' (t's much easer to nstall on Wndows)")
        ext(1)


SQLTE_DB = os.getenv('DATABASE_PATH', 'parsehub.db')
POSTGRES_URL = os.getenv('DATABASE_URL')

f not POSTGRES_URL:
    prnt(" Error: DATABASE_URL not found n envronment.")
    ext(1)

# Smart SQLte path resoluton
# f t's a relatve path, frst try relatve to scrpt, then relatve to project root
f not os.path.sabs(SQLTE_DB):
    scrpt_relatve = Path(__fle__).parent / SQLTE_DB
    # f DATABASE_PATH s "backend/parsehub.db" and scrpt s n "backend/", 
    # we should check for "parsehub.db" drectly too.
    just_flename = Path(SQLTE_DB).name
    drect_relatve = Path(__fle__).parent / just_flename
    
    f drect_relatve.exsts():
        SQLTE_DB = str(drect_relatve)
    elf scrpt_relatve.exsts():
        SQLTE_DB = str(scrpt_relatve)
    else:
        # Fallback to whatever was provded
        SQLTE_DB = str(scrpt_relatve)


prnt(f"Startng Mgraton...")
prnt(f"Source (SQLte): {SQLTE_DB}")
prnt(f"Target (Postgres): {POSTGRES_URL.splt('@')[-1]}")

def mgrate():
    try:
        # Connect to databases
        sqlte_conn = sqlte3.connect(SQLTE_DB)
        sqlte_conn.row_factory = sqlte3.Row
        sqlte_cursor = sqlte_conn.cursor()

        f HAS_PSYCOPG2:
            pg_conn = psycopg2.connect(POSTGRES_URL)
            pg_conn.autocommt = True
            pg_cursor = pg_conn.cursor()
        else:
            # pg8000 connecton
            mport pg8000
            # Parse URL to components for pg8000 f needed, but pg8000.connect supports some URL-lke strngs or manual params
            # Most relable: parse the URL manually
            from urllb.parse mport urlparse
            url = urlparse(POSTGRES_URL)
            pg_conn = pg8000.connect(
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port,
                database=url.path[1:] # strp leadng /
            )
            pg_conn.autocommt = True
            pg_cursor = pg_conn.cursor()

        # Step 0: ntalze PostgreSQL Schema (Cleanup and Recreate)
        prnt("Preparng PostgreSQL schema (Drop and Recreate)...")
        sql_path = Path(__fle__).parent / "nt_postgres.sql"
        f sql_path.exsts():
            wth open(sql_path, 'r') as f:
                schema_sql = f.read()
                
                # Extract table names from schema to drop them
                mport re
                table_names = re.fndall(r'CREATE TABLE F NOT EXSTS (\w+)', schema_sql)
                # Drop n reverse order to respect FKs
                for table n reversed(table_names):
                    pg_cursor.execute(f"DROP TABLE F EXSTS {table} CASCADE")
                
                # Execute schema creaton
                for statement n schema_sql.splt(';'):
                    f statement.strp():
                        # Fx BOOLEAN DEFAULT 0/1 for PG
                        statement = statement.replace('BOOLEAN DEFAULT 0', 'BOOLEAN DEFAULT false')
                        statement = statement.replace('BOOLEAN DEFAULT 1', 'BOOLEAN DEFAULT true')
                        pg_cursor.execute(statement)
            prnt("Schema recreated.")
        else:
            prnt("  Warnng: nt_postgres.sql not found. Assumng schema already exsts.")

        # Defne tables n order of mgraton (parent tables frst)
        tables = [

            'projects',
            'mport_batches',
            'metadata',
            'project_metadata',
            'runs',
            'scraped_data',
            'metrcs',
            'recovery_operatons',
            'data_lneage',
            'run_checkponts',
            'montorng_sessons',
            'scraped_records',
            'analytcs_cache',
            'csv_exports',
            'analytcs_records',
            'scrapng_sessons',
            'teraton_runs',
            'combned_scraped_data',
            'url_patterns',
            'product_data'
        ]

        for table n tables:
            prnt(f"--- Mgratng table: {table} ---")
            
            # Check f table exsts n SQLte
            sqlte_cursor.execute(f"SELECT name FROM sqlte_master WHERE type='table' AND name='{table}'")
            f not sqlte_cursor.fetchone():
                prnt(f"Table {table} does not exst n SQLte skppng...")
                contnue

            # Fetch data from SQLte
            sqlte_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlte_cursor.fetchall()
            
            f not rows:
                prnt(f"Table {table} s empty.")
                contnue

            prnt(f"Found {len(rows)} records. Transferrng...")

            # Prepare Postgres column names
            columns = rows[0].keys()
            col_names = ",".jon(columns)
            placeholders = ",".jon(["%s"] * len(columns))
            
            # Prepare data
            data = [tuple(row) for row n rows]

            # Clear exstng data n Postgres
            try:
                pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
            except:
                # Fallback f CASCADE or TRUNCATE fals
                pg_cursor.execute(f"DELETE FROM {table}")

            # nsert nto Postgres
            f HAS_PSYCOPG2:
                query = f"NSERT NTO {table} ({col_names}) VALUES %s"
                execute_values(pg_cursor, query, data)
            else:
                # pg8000 doesn't have execute_values helper for large batches easly
                # We'll do t n chunks
                query = f"NSERT NTO {table} ({col_names}) VALUES ({placeholders})"
                for  n range(0, len(data), 100):
                    batch = data[:+100]
                    # Convert any potental bad float/none values
                    clean_batch = []
                    for row n batch:
                        clean_row = []
                        for val n row:
                            f snstance(val, (float, nt)) and (val != val): # NaN check
                                clean_row.append(None)
                            else:
                                clean_row.append(val)
                        clean_batch.append(tuple(clean_row))
                    pg_cursor.executemany(query, clean_batch)
            
            # Update sequences (Postgres specfc)
            try:
                pg_cursor.execute(f"SELECT setval(pg_get_seral_sequence('{table}', 'd'), COALESCE(MAX(d), 1)) FROM {table}")
            except:
                pass 

            prnt(f"Table {table} mgrated successfully.")


        prnt("\nMgraton Complete!")
        
        sqlte_conn.close()
        pg_conn.close()

    except Excepton as e:
        prnt(f" Mgraton faled: {e}")
        mport traceback
        traceback.prnt_exc()

f __name__ == "__man__":
    mgrate()
