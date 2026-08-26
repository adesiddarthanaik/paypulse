from agents.recovery_agent import run_recovery_agent
from agents.risk_agent import run_risk_agent
from agents.audit_agent import run_audit_agent

class PayPulseOrchestrator:
    def run(self, payment: dict) -> dict:
        run_audit_agent(payment['id'], "Orchestrator", f"Processing payment ₹{payment['amount']}")
        
        risk = run_risk_agent(payment)
        
        if risk['decision'] == "NO-GO":
            run_audit_agent(payment['id'], "Orchestrator", f"BLOCKED: {risk['reason']}")
            return {"status": "BLOCKED", "payment_id": payment['id'], "reason": risk['reason']}
        
        result = run_recovery_agent(payment)
        run_audit_agent(payment['id'], "Orchestrator", "RECOVERY_COMPLETE")
        
        return {"status": "SUCCESS", "result": result}