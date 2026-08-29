from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from agents.risk_agent import run_risk_agent
from agents.recovery_agent import run_recovery_agent
from agents.audit_agent import run_audit_agent
from tools.rag_memory import store_case, retrieve_similar_cases

class PaymentState(TypedDict):
    payment: dict
    risk_result: Optional[dict]
    similar_cases: Optional[list]
    recovery_result: Optional[dict]
    final_status: Optional[str]
    confidence: Optional[int]

def risk_node(state: PaymentState) -> PaymentState:
    payment = state['payment']
    risk = run_risk_agent(payment)
    
    # Confidence based on risk score
    score = risk.get('risk_score', 0)
    if score >= 70:
        confidence = 95
    elif score >= 40:
        confidence = 65
    else:
        confidence = 85
    
    return {
        **state,
        "risk_result": risk,
        "confidence": confidence
    }

def rag_node(state: PaymentState) -> PaymentState:
    payment = state['payment']
    similar = retrieve_similar_cases(
        payment['failure_code'],
        payment['amount']
    )
    return {**state, "similar_cases": similar}

def recovery_node(state: PaymentState) -> PaymentState:
    payment = state['payment']
    similar = state.get('similar_cases', [])
    
    # Inject similar cases into payment context
    payment['similar_cases'] = similar
    result = run_recovery_agent(payment)
    
    # Store in RAG
    store_case(
        payment['id'],
        payment['failure_code'],
        result.get('intervention', 'UNKNOWN'),
        'ATTEMPTED'
    )
    
    return {**state, "recovery_result": result, "final_status": "SUCCESS"}

def audit_node(state: PaymentState) -> PaymentState:
    payment = state['payment']
    run_audit_agent(
        payment['id'],
        state.get('final_status', 'UNKNOWN'),
        f"Confidence: {state.get('confidence')}% | Risk: {state.get('risk_result', {}).get('risk_score', 0)}/100"
    )
    return state

def route_after_risk(state: PaymentState) -> str:
    decision = state['risk_result']['decision']
    if decision == "NO-GO":
        return "audit"
    elif decision == "HUMAN_REVIEW":
        return "audit"
    else:
        return "rag"

def build_graph():
    graph = StateGraph(PaymentState)
    
    graph.add_node("risk", risk_node)
    graph.add_node("rag", rag_node)
    graph.add_node("recovery", recovery_node)
    graph.add_node("audit", audit_node)
    
    graph.set_entry_point("risk")
    graph.add_conditional_edges("risk", route_after_risk, {
        "rag": "rag",
        "audit": "audit"
    })
    graph.add_edge("rag", "recovery")
    graph.add_edge("recovery", "audit")
    graph.add_edge("audit", END)
    
    return graph.compile()

# Global graph instance
payment_graph = build_graph()