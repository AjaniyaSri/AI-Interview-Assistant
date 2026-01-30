import os
import sqlite3

def get_conn():
    path = os.getenv("SQLITE_PATH", "backend/app/data/interviews.db")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        role TEXT,
        company TEXT,
        question TEXT,
        answer TEXT,
        total_score INTEGER,
        breakdown_json TEXT
    )
    """)
    return conn