import sqlite3
conn = sqlite3.connect('backend/parsehub.db')
print([r[0] for r in conn.execute('SELECT name FROM sqlite_master WHERE type="table" AND name NOT LIKE "sqlite_%"')])
conn.close()
