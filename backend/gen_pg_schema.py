import sqlite3
import os
from pathlib import Path

db_path = Path("backend/parsehub.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def sqlite_to_pg_type(sqlite_type):
    sqlite_type = sqlite_type.upper()
    if 'INT' in sqlite_type:
        return 'INTEGER'
    if 'TEXT' in sqlite_type or 'CHAR' in sqlite_type:
        return 'TEXT'
    if 'REAL' in sqlite_type or 'NUMERIC' in sqlite_type:
        return 'REAL'
    if 'TIMESTAMP' in sqlite_type or 'DATETIME' in sqlite_type:
        return 'TIMESTAMP'
    if 'BOOLEAN' in sqlite_type:
        return 'BOOLEAN'
    return 'TEXT'

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [row[0] for row in cursor.fetchall()]

pg_sql = []

for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    col_defs = []
    for cid, name, type_name, notnull, dflt_value, pk in columns:
        pg_type = sqlite_to_pg_type(type_name)
        
        if pk:
            col_def = f"    {name} SERIAL PRIMARY KEY"
        else:
            col_def = f"    {name} {pg_type}"
            if notnull:
                col_def += " NOT NULL"
            if dflt_value is not None:
                # Basic default value translation
                if dflt_value.upper() == 'CURRENT_TIMESTAMP':
                    col_def += " DEFAULT CURRENT_TIMESTAMP"
                else:
                    col_def += f" DEFAULT {dflt_value}"
        
        col_defs.append(col_def)
    
    table_sql = f"CREATE TABLE IF NOT EXISTS {table} (\n" + ",\n".join(col_defs) + "\n);"
    pg_sql.append(table_sql)

# Add some basic indexes
pg_sql.append("CREATE INDEX IF NOT EXISTS idx_metadata_project_token ON metadata(project_token);")
pg_sql.append("CREATE INDEX IF NOT EXISTS idx_runs_project_id ON runs(project_id);")

with open("backend/init_postgres.sql", "w") as f:
    f.write("\n\n".join(pg_sql))

print("✅ Updated backend/init_postgres.sql based on actual SQLite schema.")
conn.close()
