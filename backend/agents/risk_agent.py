import sqlite3, time
from datetime import datetime
from database import DB_PATH
from tools.groq_client import get_llm

def calculate_risk_score(payment: dict) -> dict:
    score = 0
    factors = []

    # Amount scoring
    if payment['amount'] > 10000:
        score += 25
        factors.append({"factor": "High amount", "points": 25})
    elif payment['amount'] > 5000:
        score += 15
        factors.append({"factor": "Medium amount", "points": 15})

    # Failure code scoring
    high_risk_codes = ["FRAUD_SUSPECTED", "CARD_STOLEN"]
    medium_risk_codes = ["BANK_DECLINE", "INSUFFICIENT_FUNDS"]

    if payment['failure_code'] in high_risk_codes:
        score += 40
        factors.append({"factor": "High risk failure code", "points": 40})
    elif payment['failure_code'] in medium_risk_codes:
        score += 20
        factors.append({"factor": "Suspicious failure code", "points": 20})

    # Repeat failure scoring
    conn = sqlite3.connect(DB_PATH)
    attempts = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE payment_id=?",
        (payment['id'],)
    ).fetchone()[0]
    conn.close()

    if attempts > 2:
        score += 20
        factors.append({"factor": "Multiple previous attempts", "points": 20})

    # Time scoring
    hour = datetime.now().hour
    if hour in [0, 1, 2, 3, 4, 5]:
        score += 15
        factors.append({"factor": "Unusual transaction time", "points": 15})

    return {"score": min(score, 100), "factors": factors}

def run_risk_agent(payment: dict) -> dict:
    risk_data = calculate_risk_score(payment)
    score = risk_data['score']
    factors = risk_data['factors']

    if score >= 70:
        decision = "NO-GO"
        review_status = "AUTO_BLOCKED"
    elif score >= 40:
        decision = "HUMAN_REVIEW"
        review_status = "PENDING_REVIEW"
    else:
        decision = "GO"
        review_status = "AUTO_APPROVED"

    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO audit_log
        (payment_id, agent, decision, reasoning, timestamp)
        VALUES (?,?,?,?,?)''',
        (payment['id'], "RiskAgent",
         f"{decision} (Score: {score}/100)",
         str(factors),
         datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    time.sleep(0.5)

    return {
        "payment_id": payment['id'],
        "decision": decision,
        "review_status": review_status,
        "risk_score": score,
        "factors": factors
    }