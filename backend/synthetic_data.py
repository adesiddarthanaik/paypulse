import sqlite3, uuid
from datetime import datetime
from database import DB_PATH

FAILURE_CODES = [
    "UPI_TIMEOUT", "BANK_DECLINE", "CARD_EXPIRED",
    "OTP_TIMEOUT", "INSUFFICIENT_FUNDS", "SUBSCRIPTION_LAPSE"
]

CUSTOMERS = [
    "Rahul Sharma", "Priya Patel", "Amit Singh",
    "Neha Gupta", "Vikram Rao", "Anjali Mehta"
]

def seed_payments():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    import random
    for i in range(50):
        c.execute('''INSERT OR IGNORE INTO payments 
            (id, merchant_id, customer_name, amount, failure_code, timestamp)
            VALUES (?,?,?,?,?,?)''', (
            str(uuid.uuid4()),
            "merchant_001",
            random.choice(CUSTOMERS),
            round(random.uniform(299, 9999), 2),
            random.choice(FAILURE_CODES),
            datetime.now().isoformat()
        ))
    conn.commit()
    conn.close()
    print("✓ 50 synthetic payments seeded")

if __name__ == "__main__":
    from database import init_db
    init_db()
    seed_payments()