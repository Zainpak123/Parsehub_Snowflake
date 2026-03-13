"""
SQLite to Snowflake Database Migration
Migrates all schema and data from parsehub.db to Snowflake
"""

import sqlite3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import logging

# Fix Unicode output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

try:
    import snowflake.connector
    from snowflake.connector.errors import Error as SnowflakeError
except ImportError:
    print("✗ snowflake-connector-python not installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Snowflake credentials
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'PARSEHUB_DB')

# SQLite database path
SQLITE_DB_PATH = Path(__file__).parent.parent / "parsehub.db"


class DatabaseMigration:
    """Handles SQLite to Snowflake migration"""
    
    def __init__(self):
        self.sqlite_conn = None
        self.snowflake_conn = None
        self.migration_stats = {
            'tables_created': 0,
            'rows_migrated': 0,
            'tables_migrated': 0,
            'errors': []
        }
    
    def connect_sqlite(self):
        """Connect to SQLite database"""
        if not SQLITE_DB_PATH.exists():
            logger.error(f"✗ SQLite database not found: {SQLITE_DB_PATH}")
            return False
        
        try:
            self.sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"✓ Connected to SQLite: {SQLITE_DB_PATH}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to SQLite: {e}")
            return False
    
    def connect_snowflake(self):
        """Connect to Snowflake"""
        try:
            self.snowflake_conn = snowflake.connector.connect(
                account=SNOWFLAKE_ACCOUNT,
                user=SNOWFLAKE_USER,
                password=SNOWFLAKE_PASSWORD,
                warehouse=SNOWFLAKE_WAREHOUSE,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA
            )
            logger.info(f"✓ Connected to Snowflake")
            logger.info(f"  Database: {SNOWFLAKE_DATABASE}")
            logger.info(f"  Schema: {SNOWFLAKE_SCHEMA}")
            return True
        except SnowflakeError as e:
            logger.error(f"✗ Failed to connect to Snowflake: {e}")
            return False
    
    def get_sqlite_tables(self):
        """Get all table names from SQLite"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in cursor.fetchall()]
    
    def get_sqlite_schema(self, table_name):
        """Get schema definition for a SQLite table"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        return columns
    
    def sqlite_type_to_snowflake(self, sqlite_type):
        """Convert SQLite data types to Snowflake data types"""
        sqlite_type = sqlite_type.upper() if sqlite_type else "TEXT"
        
        # Type mapping
        type_map = {
            'INTEGER': 'NUMBER(18,0)',
            'BOOLEAN': 'BOOLEAN',
            'REAL': 'FLOAT',
            'NUMERIC': 'NUMBER(18,2)',
            'TEXT': 'VARCHAR(16777216)',
            'BLOB': 'BINARY',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'TIMESTAMP': 'TIMESTAMP_NTZ'
        }
        
        # Try exact match first
        if sqlite_type in type_map:
            return type_map[sqlite_type]
        
        # Try partial matches
        for key, value in type_map.items():
            if key in sqlite_type:
                return value
        
        # Default to TEXT
        return 'VARCHAR(16777216)'
    
    def create_snowflake_table(self, table_name):
        """Create Snowflake table based on SQLite schema"""
        try:
            schema = self.get_sqlite_schema(table_name)
            
            if not schema:
                logger.warning(f"  ⚠ Table {table_name} has no columns")
                return False
            
            # Build column definitions
            columns = []
            primary_keys = []
            
            for col_id, col_name, col_type, not_null, default_val, pk in schema:
                snowflake_type = self.sqlite_type_to_snowflake(col_type)
                col_def = f"{col_name} {snowflake_type}"
                
                if not_null:
                    col_def += " NOT NULL"
                
                if pk:
                    primary_keys.append(col_name)
                
                columns.append(col_def)
            
            # Add primary key constraint if exists
            if primary_keys:
                columns.append(f"PRIMARY KEY ({', '.join(primary_keys)})")
            
            # Build CREATE TABLE statement
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            create_sql += ",\n".join(f"  {col}" for col in columns)
            create_sql += "\n)"
            
            cursor = self.snowflake_conn.cursor()
            cursor.execute(create_sql)
            
            self.migration_stats['tables_created'] += 1
            logger.info(f"  ✓ Created table: {table_name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to create {table_name}: {e}"
            logger.error(f"  ✗ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
            return False
    
    def migrate_table_data(self, table_name):
        """Migrate data from SQLite table to Snowflake"""
        try:
            # Get row count
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = sqlite_cursor.fetchone()[0]
            
            if row_count == 0:
                logger.info(f"  ✓ Table {table_name}: 0 rows (skipped)")
                return True
            
            # Get schema to get column names
            schema = self.get_sqlite_schema(table_name)
            column_names = [col[1] for col in schema]
            
            # Fetch all data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            # Build INSERT statement for Snowflake
            snowflake_cursor = self.snowflake_conn.cursor()
            batch_size = 100
            
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                
                for row in batch:
                    # Convert row to values tuple, handling NULL values
                    values = []
                    for val in row:
                        if val is None:
                            values.append("NULL")
                        elif isinstance(val, str):
                            # Escape single quotes
                            escaped = val.replace("'", "''")
                            values.append(f"'{escaped}'")
                        elif isinstance(val, bool):
                            values.append("TRUE" if val else "FALSE")
                        else:
                            values.append(str(val))
                    
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(values)})"
                    snowflake_cursor.execute(insert_sql)
            
            self.migration_stats['rows_migrated'] += row_count
            self.migration_stats['tables_migrated'] += 1
            logger.info(f"  ✓ Migrated {row_count} rows to {table_name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to migrate data for {table_name}: {e}"
            logger.error(f"  ✗ {error_msg}")
            self.migration_stats['errors'].append(error_msg)
            return False
    
    def run_migration(self):
        """Run complete migration process"""
        print("\n" + "=" * 80)
        print("🚀 SQLite to Snowflake Database Migration")
        print("=" * 80 + "\n")
        
        # Connect to databases
        logger.info("Connecting to databases...")
        if not self.connect_sqlite():
            return False
        
        if not self.connect_snowflake():
            return False
        
        # Get SQLite tables
        logger.info("\nFetching SQLite schema...")
        tables = self.get_sqlite_tables()
        logger.info(f"Found {len(tables)} tables\n")
        
        if not tables:
            logger.error("No tables found in SQLite database")
            return False
        
        # Step 1: Create all Snowflake tables
        logger.info("=" * 80)
        logger.info("STEP 1: Creating Snowflake Tables")
        logger.info("=" * 80)
        
        for table in tables:
            self.create_snowflake_table(table)
        
        # Step 2: Migrate data
        logger.info("\n" + "=" * 80)
        logger.info("STEP 2: Migrating Data")
        logger.info("=" * 80 + "\n")
        
        for table in tables:
            self.migrate_table_data(table)
        
        # Print summary
        self.print_summary()
        
        return len(self.migration_stats['errors']) == 0
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "=" * 80)
        print("📊 Migration Summary")
        print("=" * 80)
        print(f"✓ Tables created: {self.migration_stats['tables_created']}")
        print(f"✓ Tables migrated: {self.migration_stats['tables_migrated']}")
        print(f"✓ Rows migrated: {self.migration_stats['rows_migrated']:,}")
        
        if self.migration_stats['errors']:
            print(f"\n✗ Errors: {len(self.migration_stats['errors'])}")
            for error in self.migration_stats['errors']:
                print(f"  - {error}")
        
        print("\n" + "=" * 80)
        print("✅ Migration complete!" if not self.migration_stats['errors'] else "⚠️  Migration completed with errors")
        print("=" * 80 + "\n")
    
    def cleanup(self):
        """Close database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        if self.snowflake_conn:
            self.snowflake_conn.close()


def main():
    """Main entry point"""
    migration = DatabaseMigration()
    
    try:
        success = migration.run_migration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        migration.cleanup()


if __name__ == "__main__":
    main()
