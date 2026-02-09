import sqlite3
import os

DB_PATH = "database/fraudhound.db"

def get_connection():
    os.makedirs("database", exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scam_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        risk_score REAL,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def insert_event(text, risk_score, source):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO scam_events (text, risk_score, source) VALUES (?, ?, ?)",
        (text, risk_score, source)
    )

    conn.commit()
    conn.close()

def fetch_all_events():
    conn = get_connection()
    df = conn.execute(
        "SELECT * FROM scam_events ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return df
