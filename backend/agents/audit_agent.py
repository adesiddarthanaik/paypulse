import sqlite3
from datetime import datetime
from database import DB_PATH

def run_audit_agent(payment_id: str, decision: str, reasoning: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO audit_log
        (payment_id, agent, decision, reasoning, timestamp)
        VALUES (?,?,?,?,?)''',
        (payment_id, "AuditAgent", decision, reasoning, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return {"status": "logged", "payment_id": payment_id}