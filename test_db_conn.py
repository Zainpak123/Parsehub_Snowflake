import os
import pg8000
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv("backend/.env")
url_str = os.getenv("DATABASE_URL")
print(f"Testing connection to: {url_str.split('@')[-1]}")

try:
    url = urlparse(url_str)
    conn = pg8000.connect(
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        timeout=10
    )
    print("✅ Connection successful!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(f"PG Version: {cursor.fetchone()[0]}")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
