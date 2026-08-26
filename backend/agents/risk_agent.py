from tools.groq_client import get_llm
from datetime import datetime
import sqlite3, time
from database import DB_PATH

def run_risk_agent(payment: dict) -> dict:
    decision = "GO"
    reason = "Auto-approved for recovery"
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO audit_log
        (payment_id, agent, decision, reasoning, timestamp)
        VALUES (?,?,?,?,?)''',
        (payment['id'], "RiskAgent", decision, reason, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    time.sleep(1)
    return {"payment_id": payment['id'], "decision": decision, "reason": reason}