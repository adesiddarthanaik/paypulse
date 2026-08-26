import sqlite3

DB_PATH = "paypulse.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id TEXT PRIMARY KEY,
        merchant_id TEXT,
        customer_name TEXT,
        amount REAL,
        failure_code TEXT,
        status TEXT DEFAULT 'PENDING',
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id TEXT,
        agent TEXT,
        decision TEXT,
        reasoning TEXT,
        timestamp TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS recovery_results (
        payment_id TEXT PRIMARY KEY,
        intervention TEXT,
        message TEXT,
        payment_link TEXT,
        outcome TEXT,
        amount_recovered REAL DEFAULT 0
    )''')

    conn.commit()
    conn.close()