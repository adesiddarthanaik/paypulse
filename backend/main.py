import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents.growth_agent import run_growth_agent
from agents.finance_agent import run_finance_agent
from agents.orchestrator import PayPulseOrchestrator
from agents.recovery_agent import run_recovery_agent
from agents.risk_agent import run_risk_agent
from database import DB_PATH, init_db
from synthetic_data import seed_payments


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

    # STEP 1: Risk Agent
    risk = run_risk_agent(payment)

    # If risk agent says NO-GO, stop recovery
    if risk["decision"] == "NO-GO":
        return {
            "status": "BLOCKED",
            "reason": risk["reason"]
        }

    # STEP 2: Recovery Agent
    result = run_recovery_agent(payment)

    return {
        "status": "SUCCESS",
        "result": result
    }


# ---------------------------------------------------------
# RUN RECOVERY BATCH
# ---------------------------------------------------------

from agents.graph import payment_graph

@app.post("/api/run-batch")
def run_batch():
    import sqlite3
    from database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    payments = [dict(p) for p in conn.execute(
        "SELECT * FROM payments WHERE status='PENDING' LIMIT 10"
    ).fetchall()]
    conn.close()

    results = []
    for payment in payments:
        state = payment_graph.invoke({
            "payment": payment,
            "risk_result": None,
            "similar_cases": None,
            "recovery_result": None,
            "final_status": None,
            "confidence": None
        })
        
        risk = state.get('risk_result', {})
        
        if risk.get('decision') == 'HUMAN_REVIEW':
            conn = sqlite3.connect(DB_PATH)
            conn.execute('''INSERT OR IGNORE INTO hitl_queue
                (payment_id, risk_score, factors, timestamp)
                VALUES (?,?,?,?)''',
                (payment['id'], risk.get('risk_score', 0),
                 str(risk.get('factors', [])),
                 datetime.now().isoformat())
            )
            conn.execute(
                "UPDATE payments SET status='PENDING_REVIEW' WHERE id=?",
                (payment['id'],)
            )
            conn.commit()
            conn.close()
            results.append({
                "status": "HUMAN_REVIEW",
                "payment_id": payment['id'],
                "risk_score": risk.get('risk_score'),
                "confidence": state.get('confidence'),
                "factors": risk.get('factors')
            })
            continue

        if risk.get('decision') == 'NO-GO':
            results.append({
                "status": "BLOCKED",
                "payment_id": payment['id'],
                "risk_score": risk.get('risk_score'),
                "confidence": state.get('confidence'),
                "factors": risk.get('factors')
            })
            continue

        recovery = state.get('recovery_result', {})
        recovery['confidence'] = state.get('confidence')
        recovery['similar_cases'] = state.get('similar_cases', [])
        results.append({"status": "SUCCESS", "result": recovery})

    return {"processed": len(results), "results": results}

# ---------------------------------------------------------
# HITL QUEUE & DECISIONS
# ---------------------------------------------------------

@app.get("/api/hitl-queue")
def get_hitl_queue():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    items = conn.execute(
        "SELECT h.*, p.amount, p.customer_name, p.failure_code FROM hitl_queue h JOIN payments p ON h.payment_id = p.id WHERE h.status='PENDING'"
    ).fetchall()
    conn.close()
    return [dict(i) for i in items]


@app.post("/api/hitl-decision/{payment_id}")
def hitl_decision(payment_id: str, decision: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Update HITL queue
    conn.execute(
        "UPDATE hitl_queue SET status='REVIEWED', reviewer_decision=? WHERE payment_id=?",
        (decision, payment_id)
    )
    
    # Log human decision
    conn.execute('''INSERT INTO audit_log
        (payment_id, agent, decision, reasoning, timestamp)
        VALUES (?,?,?,?,?)''',
        (payment_id, "Human", decision, "Manual review decision", datetime.now().isoformat())
    )
    conn.commit()
    
    result = {"status": "updated", "decision": decision}
    
    # If approved → run recovery
    if decision == "APPROVE":
        payment = dict(conn.execute(
            "SELECT * FROM payments WHERE id=?", (payment_id,)
        ).fetchone())
        conn.close()
        recovery = run_recovery_agent(payment)
        result["recovery"] = recovery
    else:
        # If rejected → permanently block
        conn.execute(
            "UPDATE payments SET status='PERMANENTLY_BLOCKED' WHERE id=?",
            (payment_id,)
        )
        conn.commit()
        conn.close()
    
    return result


# ---------------------------------------------------------
# AUDIT TRAIL
# ---------------------------------------------------------

@app.get("/api/audit-trail")
def get_audit_trail():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    logs = conn.execute(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(l) for l in logs]


# ---------------------------------------------------------
# METRICS & PERFORMANCE
# ---------------------------------------------------------

@app.get("/api/metrics")
def get_metrics():
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


@app.get("/api/performance")
def get_performance():
    conn = sqlite3.connect(DB_PATH)
    
    # Recovery metrics
    total = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
    attempted = conn.execute("SELECT COUNT(*) FROM recovery_results").fetchone()[0]
    amount = conn.execute("SELECT SUM(amount_recovered) FROM recovery_results").fetchone()[0] or 0
    
    # Risk metrics
    blocked = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE agent='RiskAgent' AND decision LIKE '%NO-GO%'"
    ).fetchone()[0]
    approved = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE agent='RiskAgent' AND decision LIKE '%GO%'"
    ).fetchone()[0]
    human_review = conn.execute(
        "SELECT COUNT(*) FROM hitl_queue"
    ).fetchone()[0]
    
    # Memory metrics
    customers = conn.execute("SELECT COUNT(*) FROM customer_memory").fetchone()[0]
    escalated = conn.execute(
        "SELECT COUNT(*) FROM customer_memory WHERE escalation_level >= 3"
    ).fetchone()[0]
    
    # Finance metrics
    finance_logs = conn.execute(
        "SELECT COUNT(*) FROM audit_log WHERE agent='FinanceAgent'"
    ).fetchone()[0]
    
    conn.close()
    
    return {
        "recovery": {
            "total_payments": total,
            "attempted": attempted,
            "amount_recovered": round(amount, 2),
            "recovery_rate": round((attempted/total)*100, 1) if total > 0 else 0
        },
        "risk": {
            "blocked": blocked,
            "approved": approved,
            "human_review": human_review
        },
        "memory": {
            "customers_tracked": customers,
            "escalated": escalated
        },
        "finance": {
            "reconciliations": finance_logs
        }
    }


# ---------------------------------------------------------
# OTHER AGENTS
# ---------------------------------------------------------

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