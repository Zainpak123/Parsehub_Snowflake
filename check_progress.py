import os
import pg8000
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv("backend/.env")
url_str = os.getenv("DATABASE_URL")

try:
    url = urlparse(url_str)
    conn = pg8000.connect(
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        database=url.path[1:]
    )
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"{'Table':<30} | {'Count':<10}")
    print("-" * 43)
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<30} | {count:<10}")
        except:
            print(f"{table:<30} | ERROR")
    
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
