import sqlite3
from datetime import datetime

DB_NAME = "audit_history.db"

def init_history_db():
    """Creates the history table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            scan_date TEXT,
            total_leaks INTEGER,
            risk_score TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_scan_result(filename, total_leaks, risk_score):
    """Saves a new scan to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO scans (filename, scan_date, total_leaks, risk_score) VALUES (?, ?, ?, ?)',
              (filename, date_str, total_leaks, risk_score))
    conn.commit()
    conn.close()

def get_recent_scans():
    """Fetches the last 10 scans."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT filename, scan_date, total_leaks, risk_score FROM scans ORDER BY id DESC LIMIT 10')
    rows = c.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        history.append({
            "filename": r[0],
            "date": r[1],
            "leaks": r[2],
            "risk": r[3]
        })
    return history

# Initialize DB immediately
init_history_db()