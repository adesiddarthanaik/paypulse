from tools.groq_client import get_llm
from tools.razorpay_tool import create_payment_link
from datetime import datetime
import sqlite3, time
from database import DB_PATH

MERCHANT_CATALOG = [
    {"id": "P001", "name": "Running Shoes", "price": 2999, "category": "Footwear"},
    {"id": "P002", "name": "Sports T-Shirt", "price": 799, "category": "Clothing"},
    {"id": "P003", "name": "Protein Powder", "price": 1499, "category": "Nutrition"},
    {"id": "P004", "name": "Water Bottle", "price": 399, "category": "Accessories"},
    {"id": "P005", "name": "Yoga Mat", "price": 899, "category": "Fitness"},
]

def run_growth_agent(customer_name: str, last_purchase: str, amount: float) -> dict:
    llm = get_llm()
    
    catalog_str = "\n".join([f"{p['name']} - Rs{p['price']}" for p in MERCHANT_CATALOG])
    
    result = llm.invoke(f"""
You are a sales agent for an Indian sports store.
Customer: {customer_name}, last bought: {last_purchase}, spent: Rs{amount}
Catalog: {catalog_str}
Suggest ONE upsell product and write a Hinglish WhatsApp message.
JSON only: {{"product": "...", "price": 0, "message": "...", "reasoning": "..."}}
""").content

    time.sleep(2)

    link = create_payment_link(amount, customer_name, f"Special offer for {customer_name}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute('''INSERT INTO audit_log
        (payment_id, agent, decision, reasoning, timestamp)
        VALUES (?,?,?,?,?)''',
        (f"growth_{customer_name}", "GrowthAgent", "UPSELL_SENT", result, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return {
        "customer": customer_name,
        "upsell_result": result,
        "payment_link": link
    }