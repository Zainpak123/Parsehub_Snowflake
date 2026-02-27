import sqlite3
import os
from pathlib import Path

db_path = Path("backend/parsehub.db")
if not db_path.exists():
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table_name, sql in tables:
    print(f"--- Table: {table_name} ---")
    print(sql)
    print("\n")

conn.close()
