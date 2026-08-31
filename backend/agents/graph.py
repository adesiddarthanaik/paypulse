from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.risk_agent import run_risk_agent
from agents.recovery_agent import run_recovery_agent
from agents.audit_agent import run_audit_agent

class PaymentState(TypedDict):
    payment: dict
    risk_result: Optional[dict]
    recovery_result: Optional[dict]
    final_status: Optional[str]
    confidence: Optional[int]

def risk_node(state: PaymentState) -> PaymentState:
    risk = run_risk_agent(state['payment'])
    score = risk.get('risk_score', 0)
    confidence = 95 if score >= 70 else 65 if score >= 40 else 85
    return {**state, "risk_result": risk, "confidence": confidence}

def recovery_node(state: PaymentState) -> PaymentState:
    result = run_recovery_agent(state['payment'])
    return {**state, "recovery_result": result, "final_status": "SUCCESS"}

def audit_node(state: PaymentState) -> PaymentState:
    run_audit_agent(
        state['payment']['id'],
        state.get('final_status', 'UNKNOWN'),
        f"Confidence: {state.get('confidence')}% | Risk: {state.get('risk_result', {}).get('risk_score', 0)}/100"
    )
    return state

def route_after_risk(state: PaymentState) -> str:
    decision = state['risk_result']['decision']
    if decision in ["NO-GO", "HUMAN_REVIEW"]:
        return "audit"
    return "recovery"

def build_graph():
    graph = StateGraph(PaymentState)
    graph.add_node("risk", risk_node)
    graph.add_node("recovery", recovery_node)
    graph.add_node("audit", audit_node)
    graph.set_entry_point("risk")
    graph.add_conditional_edges("risk", route_after_risk, {
        "recovery": "recovery",
        "audit": "audit"
    })
    graph.add_edge("recovery", "audit")
    graph.add_edge("audit", END)
    return graph.compile()

payment_graph = build_graph()