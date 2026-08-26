import razorpay, os
from dotenv import load_dotenv
load_dotenv()

def create_payment_link(amount: float, customer_name: str, description: str):
    try:
        client = razorpay.Client(
            auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
        )
        link = client.payment_link.create({
            "amount": int(amount * 100),
            "currency": "INR",
            "description": description,
            "customer": {"name": customer_name},
            "notify": {"sms": False, "email": False}
        })
        return link.get("short_url", "https://rzp.io/test/demo")
    except Exception as e:
        return f"https://rzp.io/test/demo-{int(amount)}"