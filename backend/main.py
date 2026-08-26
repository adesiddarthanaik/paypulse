from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agents.growth_agent import run_growth_agent
from agents.finance_agent import run_finance_agent
from agents.orchestrator import PayPulseOrchestrator
from database import init_db
from synthetic_data import seed_payments

from agents.recovery_agent import run_recovery_agent
from agents.risk_agent import run_risk_agent


app = FastAPI(title="paypulse")


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


# ---------------------------------------------------------
# STARTUP
# ---------------------------------------------------------

@app.on_event("startup")
def startup():
    init_db()
    seed_payments()


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {"status": "paypulse running"}


# ---------------------------------------------------------
# GET ALL PAYMENTS
# ---------------------------------------------------------

@app.get("/api/payments")
def get_payments():
    import sqlite3
    from database import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    payments = conn.execute(
        "SELECT * FROM payments"
    ).fetchall()

    conn.close()

    return [dict(p) for p in payments]


# ---------------------------------------------------------
# RUN RECOVERY FOR ONE PAYMENT
# ---------------------------------------------------------

@app.post("/api/run-recovery/{payment_id}")
def run_recovery(payment_id: str):
    import sqlite3
    from database import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    payment_row = conn.execute(
        "SELECT * FROM payments WHERE id=?",
        (payment_id,)
    ).fetchone()

    conn.close()

    # Payment not found
    if payment_row is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    payment = dict(payment_row)

    # -----------------------------------------------------
    # STEP 1: Risk Agent
    # -----------------------------------------------------

    risk = run_risk_agent(payment)

    # If risk agent says NO-GO, stop recovery
    if risk["decision"] == "NO-GO":
        return {
            "status": "BLOCKED",
            "reason": risk["reason"]
        }

    # -----------------------------------------------------
    # STEP 2: Recovery Agent
    # -----------------------------------------------------

    result = run_recovery_agent(payment)

    return {
        "status": "SUCCESS",
        "result": result
    }


# ---------------------------------------------------------
# RUN RECOVERY BATCH
# ---------------------------------------------------------

@app.post("/api/run-batch")
def run_batch():
    import sqlite3
    from database import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    payments = [
        dict(p)
        for p in conn.execute(
            "SELECT * FROM payments WHERE status='PENDING' LIMIT 10"
        ).fetchall()
    ]

    conn.close()

    results = []

    for payment in payments:

        # -------------------------------------------------
        # STEP 1: Risk Agent
        # -------------------------------------------------

        risk = run_risk_agent(payment)

        # -------------------------------------------------
        # STEP 2: Only recover if risk decision is GO
        # -------------------------------------------------

        if risk["decision"] == "GO":
            result = run_recovery_agent(payment)
            results.append(result)

    return {
        "processed": len(results),
        "results": results
    }


# ---------------------------------------------------------
# METRICS
# ---------------------------------------------------------

@app.get("/api/metrics")
def get_metrics():
    import sqlite3
    from database import DB_PATH

    conn = sqlite3.connect(DB_PATH)

    # Total payments
    total = conn.execute(
        "SELECT COUNT(*) FROM payments"
    ).fetchone()[0]

    # Recovery statistics
    recovered = conn.execute(
        """
        SELECT COUNT(*), SUM(amount_recovered)
        FROM recovery_results
        WHERE outcome='ATTEMPTED'
        """
    ).fetchone()

    conn.close()

    return {
        "total_payments": total,
        "recovery_attempted": recovered[0],
        "amount_recovered": recovered[1] or 0
    } 



@app.post("/api/run-growth")
def run_growth():
    results = []
    customers = [
        {"name": "Rahul Sharma", "last": "Running Shoes", "amount": 2999},
        {"name": "Priya Patel",  "last": "Yoga Mat",      "amount": 899},
        {"name": "Amit Singh",   "last": "Protein Powder", "amount": 1499},
    ]
    for c in customers:
        result = run_growth_agent(c['name'], c['last'], c['amount'])
        results.append(result)
    return {"processed": len(results), "results": results}

@app.post("/api/run-finance")
def run_finance():
    result = run_finance_agent()
    return result 


@app.get("/api/audit-trail")
def get_audit_trail():
    import sqlite3
    from database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    logs = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(l) for l in logs]

@app.post("/api/run-batch")
def run_batch_v2():
    import sqlite3
    from database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    payments = [dict(p) for p in conn.execute(
        "SELECT * FROM payments WHERE status='PENDING' LIMIT 10"
    ).fetchall()]
    conn.close()
    
    orchestrator = PayPulseOrchestrator()
    results = []
    for payment in payments:
        result = orchestrator.run(payment)
        results.append(result)
    
    return {"processed": len(results), "results": results}