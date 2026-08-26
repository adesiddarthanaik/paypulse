from tools.groq_client import get_llm
from datetime import datetime
import sqlite3, time
from database import DB_PATH

SYNTHETIC_SETTLEMENTS = [
    {"id": "S001", "amount": 15000, "merchant": "merchant_001", "status": "SETTLED", "date": "2026-08-20"},
    {"id": "S002", "amount": 8500,  "merchant": "merchant_001", "status": "PENDING", "date": "2026-08-21"},
    {"id": "S003", "amount": 22000, "merchant": "merchant_001", "status": "SETTLED", "date": "2026-08-22"},
    {"id": "S004", "amount": 3200,  "merchant": "merchant_001", "status": "FAILED",  "date": "2026-08-23"},
    {"id": "S005", "amount": 18900, "merchant": "merchant_001", "status": "SETTLED", "date": "2026-08-24"},
]

def run_finance_agent() -> dict:
    llm = get_llm()

    settled = [s for s in SYNTHETIC_SETTLEMENTS if s['status'] == 'SETTLED']
    pending = [s for s in SYNTHETIC_SETTLEMENTS if s['status'] == 'PENDING']
    failed  = [s for s in SYNTHETIC_SETTLEMENTS if s['status'] == 'FAILED']

    total = sum(s['amount'] for s in SYNTHETIC_SETTLEMENTS)
    settled_amount = sum(s['amount'] for s in settled)

    result = llm.invoke(f"""
You are a finance reconciliation agent.
Settlements: {SYNTHETIC_SETTLEMENTS}
Settled: {len(settled)}, Pending: {len(pending)}, Failed: {len(failed)}
Total: Rs{total}, Settled: Rs{settled_amount}
Identify exceptions and provide reconciliation summary.
JSON only: {{"match_rate": "...", "exceptions": [...], "recommendation": "..."}}
""").content

    time.sleep(2)

    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO audit_log
        (payment_id, agent, decision, reasoning, timestamp)
        VALUES (?,?,?,?,?)''',
        ("finance_batch", "FinanceAgent", "RECONCILED", result, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return {
        "total_records": len(SYNTHETIC_SETTLEMENTS),
        "settled": len(settled),
        "pending": len(pending),
        "failed": len(failed),
        "total_amount": total,
        "settled_amount": settled_amount,
        "ai_analysis": result
    }