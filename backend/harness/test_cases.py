TEST_CASES = [
    {
        "id": "T001",
        "agent": "RecoveryAgent",
        "description": "UPI timeout — should get retry intervention",
        "input": {"failure_code": "UPI_TIMEOUT", "amount": 299},
        "expected_intervention": "RETRY"
    },
    {
        "id": "T002",
        "agent": "RecoveryAgent",
        "description": "Bank decline — should get WhatsApp link",
        "input": {"failure_code": "BANK_DECLINE", "amount": 4999},
        "expected_intervention": "WHATSAPP_LINK"
    },
    {
        "id": "T003",
        "agent": "RecoveryAgent",
        "description": "Card expired — should get WhatsApp link",
        "input": {"failure_code": "CARD_EXPIRED", "amount": 1499},
        "expected_intervention": "WHATSAPP_LINK"
    },
    {
        "id": "T004",
        "agent": "RecoveryAgent",
        "description": "Subscription lapse — should get retry",
        "input": {"failure_code": "SUBSCRIPTION_LAPSE", "amount": 999},
        "expected_intervention": "RETRY"
    },
    {
        "id": "T005",
        "agent": "RiskAgent",
        "description": "Small amount — should auto approve",
        "input": {"failure_code": "UPI_TIMEOUT", "amount": 199},
        "expected_decision": "GO",
        "expected_risk_max": 39
    },
    {
        "id": "T006",
        "agent": "RiskAgent",
        "description": "High amount — should trigger review or block",
        "input": {"failure_code": "BANK_DECLINE", "amount": 15000},
        "expected_risk_min": 25
    },
    {
        "id": "T007",
        "agent": "RiskAgent",
        "description": "Very high amount — high risk score",
        "input": {"failure_code": "INSUFFICIENT_FUNDS", "amount": 75000},
        "expected_risk_min": 25
    },
    {
        "id": "T008",
        "agent": "RecoveryAgent",
        "description": "3 previous attempts — must escalate to human",
        "input": {"failure_code": "UPI_TIMEOUT", "amount": 499, "force_attempts": 3},
        "expected_intervention": "HUMAN_ESCALATION"
    },
    {
        "id": "T009",
        "agent": "RiskAgent",
        "description": "Zero amount — should handle gracefully",
        "input": {"failure_code": "BANK_DECLINE", "amount": 0},
        "expected_decision": "GO"
    },
    {
        "id": "T010",
        "agent": "RecoveryAgent",
        "description": "OTP timeout — should get retry",
        "input": {"failure_code": "OTP_TIMEOUT", "amount": 799},
        "expected_intervention": "RETRY"
    }
]