from tools.groq_client import get_llm
from tools.razorpay_tool import create_payment_link
from datetime import datetime
import sqlite3, time
from database import DB_PATH

HINGLISH_TEMPLATES = {
    "UPI_TIMEOUT": "Aapka UPI payment timeout ho gaya. Iss link se abhi complete karein 👇",
    "BANK_DECLINE": "Aapka payment decline hua. EMI ya doosre method se try karein 👇",
    "CARD_EXPIRED": "Aapka card expire ho gaya hai. UPI se pay karein 👇",
    "OTP_TIMEOUT": "OTP time out hua. Abhi retry karein 👇",
    "INSUFFICIENT_FUNDS": "Insufficient funds. EMI option available hai 👇",
    "SUBSCRIPTION_LAPSE": "Aapka subscription renew karna baaki hai 👇"
}

ESCALATION_MESSAGES = {
    1: "Friendly reminder — payment pending hai",
    2: "Aapka order wait kar raha hai — abhi complete karein",
    3: "Last reminder — alternate payment method try karein",
    4: "ESCALATED_TO_HUMAN"
}

def get_customer_memory(customer_name: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    memory = conn.execute(
        "SELECT * FROM customer_memory WHERE customer_name=?",
        (customer_name,)
    ).fetchone()
    conn.close()
    return dict(memory) if memory else None

def update_customer_memory(customer_name: str, intervention: str, level: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO customer_memory 
        (customer_name, total_failures, total_attempts, last_intervention, last_contact, escalation_level)
        VALUES (?,1,1,?,?,?)
        ON CONFLICT(customer_name) DO UPDATE SET
        total_failures = total_failures + 1,
        total_attempts = total_attempts + 1,
        last_intervention = ?,
        last_contact = ?,
        escalation_level = ?''',
        (customer_name, intervention, datetime.now().isoformat(), level,
         intervention, datetime.now().isoformat(), level)
    )
    conn.commit()
    conn.close()

def run_recovery_agent(payment: dict) -> dict:
    llm = get_llm()
    customer = payment['customer_name']

    # Check memory
    memory = get_customer_memory(customer)
    
    if memory:
        level = min(memory['escalation_level'] + 1, 4)
        if memory['total_attempts'] >= 3:
            return {
                "payment_id": payment['id'],
                "message": f"Max attempts reached for {customer}. Escalated to human.",
                "link": None,
                "diagnosis": "Memory: 3 previous attempts — stopping rule triggered",
                "intervention": "HUMAN_ESCALATION",
                "escalation_level": 4,
                "memory_used": True
            }
    else:
        level = 1

    # Groq Call 1 — Diagnose
    diagnosis = llm.invoke(f"""
Payment failed: {payment['failure_code']}
Amount: Rs{payment['amount']}
Customer history: {memory if memory else 'First time failure'}
Return JSON: {{"failure_type":"...","severity":"LOW/MEDIUM/HIGH","recoverable":true,"reasoning":"..."}}
""").content

    time.sleep(1)

    # Groq Call 2 — Intervention
    intervention = llm.invoke(f"""
Diagnosis: {diagnosis}
Escalation level: {level}/4
Previous intervention: {memory['last_intervention'] if memory else 'None'}
Interventions: WHATSAPP_LINK, RETRY, EMI_OFFER, HUMAN_ESCALATION
Return JSON: {{"intervention":"...","reasoning":"..."}}
""").content

    time.sleep(1)

    link = create_payment_link(
        payment['amount'],
        customer,
        f"Complete your payment of Rs{payment['amount']}"
    )

    base_message = HINGLISH_TEMPLATES.get(
        payment['failure_code'],
        "Aapka payment pending hai 👇"
    )
    escalation_note = ESCALATION_MESSAGES.get(level, "")
    message = f"{base_message} {link}"

    # Update memory
    update_customer_memory(customer, "WHATSAPP_LINK", level)

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
        (payment['id'], "RecoveryAgent",
         f"Level {level} intervention",
         f"Memory: {memory}\nDiagnosis: {diagnosis}\nIntervention: {intervention}",
         datetime.now().isoformat())
    )
    conn.execute(
        "UPDATE payments SET status='RECOVERY_ATTEMPTED' WHERE id=?",
        (payment['id'],)
    )
    conn.commit()
    conn.close()

    return {
        "payment_id": payment['id'],
        "message": message,
        "link": link,
        "diagnosis": diagnosis,
        "intervention": intervention,
        "escalation_level": level,
        "memory_used": memory is not None
    }