from tools.groq_client import get_llm
from tools.razorpay_tool import create_payment_link
from datetime import datetime
import sqlite3
from database import DB_PATH

HINGLISH_TEMPLATES = {
    "UPI_TIMEOUT": "Aapka UPI payment timeout ho gaya. Iss link se abhi complete karein 👇",
    "BANK_DECLINE": "Aapka payment decline hua. EMI ya doosre method se try karein 👇",
    "CARD_EXPIRED": "Aapka card expire ho gaya hai. UPI se pay karein 👇",
    "OTP_TIMEOUT": "OTP time out hua. Abhi retry karein 👇",
    "INSUFFICIENT_FUNDS": "Insufficient funds. EMI option available hai 👇",
    "SUBSCRIPTION_LAPSE": "Aapka subscription renew karna baaki hai 👇"
}

def run_recovery_agent(payment: dict) -> dict:
    llm = get_llm()

    # Groq Call 1 — Diagnose
    diagnosis = llm.invoke(f"""
You are a payment recovery expert.
Payment failed with code: {payment['failure_code']}
Amount: ₹{payment['amount']}
Customer: {payment['customer_name']}

Return JSON only:
{{"failure_type": "...", "severity": "LOW/MEDIUM/HIGH", "recoverable": true/false, "reasoning": "..."}}
""").content

    # Groq Call 2 — Intervention
    intervention = llm.invoke(f"""
Payment diagnosis: {diagnosis}
Available interventions: WHATSAPP_LINK, RETRY, EMI_OFFER, ESCALATE

Return JSON only:
{{"intervention": "...", "reasoning": "..."}}
""").content

    # Generate payment link
    link = create_payment_link(
        payment['amount'],
        payment['customer_name'],
        f"Complete your payment of ₹{payment['amount']}"
    )

    message = HINGLISH_TEMPLATES.get(payment['failure_code'], "Aapka payment pending hai 👇")
    message += f" {link}"

    # Save to DB
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT OR REPLACE INTO recovery_results
        (payment_id, intervention, message, payment_link, outcome, amount_recovered)
        VALUES (?,?,?,?,?,?)''',
        (payment['id'], "WHATSAPP_LINK", message, link, "ATTEMPTED", payment['amount'])
    )
    conn.execute('''INSERT INTO audit_log
        (payment_id, agent, decision, reasoning, timestamp)
        VALUES (?,?,?,?,?)''',
        (payment['id'], "RecoveryAgent", intervention, diagnosis, datetime.now().isoformat())
    )
    conn.execute("UPDATE payments SET status='RECOVERY_ATTEMPTED' WHERE id=?", (payment['id'],))
    conn.commit()
    conn.close()

    return {
        "payment_id": payment['id'],
        "message": message,
        "link": link,
        "diagnosis": diagnosis,
        "intervention": intervention
    }