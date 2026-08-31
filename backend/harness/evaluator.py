import uuid, time, sqlite3, os, json, re
from datetime import datetime
from database import DB_PATH
from harness.test_cases import TEST_CASES
from agents.risk_agent import run_risk_agent, calculate_risk_score
from agents.recovery_agent import run_recovery_agent

def make_test_payment(test_input: dict) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "merchant_id": "test_merchant",
        "customer_name": "Test Customer",
        "amount": test_input.get("amount", 999),
        "failure_code": test_input.get("failure_code", "UPI_TIMEOUT"),
        "status": "PENDING",
        "timestamp": datetime.now().isoformat()
    }

def parse_intervention(raw: str) -> str:
    try:
        json_match = re.search(r'\{.*?"intervention".*?\}', raw, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return parsed.get('intervention', '').strip()
    except:
        pass
    # Direct keyword match
    for keyword in ["WHATSAPP_LINK", "HUMAN_ESCALATION", "EMI_OFFER", "RETRY"]:
        if keyword in raw:
            return keyword
    return raw.strip()

def evaluate_risk_agent(test: dict) -> dict:
    payment = make_test_payment(test['input'])
    start = time.time()
    result = run_risk_agent(payment)
    elapsed = round(time.time() - start, 2)
    
    got_decision = result.get('decision', '')
    got_score = result.get('risk_score', 0)
    
    passed = True
    failures = []
    
    if 'expected_decision' in test:
        if got_decision != test['expected_decision']:
            passed = False
            failures.append(f"Decision: expected {test['expected_decision']}, got {got_decision}")
    
    if 'expected_risk_min' in test:
        if got_score < test['expected_risk_min']:
            passed = False
            failures.append(f"Risk score {got_score} below minimum {test['expected_risk_min']}")
    
    if 'expected_risk_max' in test:
        if got_score > test['expected_risk_max']:
            passed = False
            failures.append(f"Risk score {got_score} above maximum {test['expected_risk_max']}")
    
    return {
        "test_id": test['id'],
        "agent": "RiskAgent",
        "description": test['description'],
        "status": "PASS" if passed else "FAIL",
        "expected": {
            "decision": test.get('expected_decision'),
            "risk_min": test.get('expected_risk_min'),
            "risk_max": test.get('expected_risk_max')
        },
        "got": {"decision": got_decision, "risk_score": got_score},
        "failures": failures,
        "response_time": f"{elapsed}s"
    }

def evaluate_recovery_agent(test: dict) -> dict:
    payment = make_test_payment(test['input'])
    
    if test['input'].get('force_attempts', 0) >= 3:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''INSERT OR REPLACE INTO customer_memory
            (customer_name, total_failures, total_attempts,
             last_intervention, last_contact, escalation_level)
            VALUES (?,3,3,'WHATSAPP_LINK',?,3)''',
            ("Test Customer", datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    start = time.time()
    os.environ["HARNESS_MODE"] = "true"
    result = run_recovery_agent(payment)
    os.environ["HARNESS_MODE"] = "false"
    elapsed = round(time.time() - start, 2)
    
    got_intervention = parse_intervention(result.get('intervention', ''))
    
    passed = True
    failures = []
    
    if 'expected_intervention' in test:
        if got_intervention != test['expected_intervention']:
            passed = False
            failures.append(f"Expected {test['expected_intervention']}, got {got_intervention}")
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM customer_memory WHERE customer_name='Test Customer'")
    conn.commit()
    conn.close()
    
    return {
        "test_id": test['id'],
        "agent": "RecoveryAgent",
        "description": test['description'],
        "status": "PASS" if passed else "FAIL",
        "expected": {"intervention": test.get('expected_intervention')},
        "got": {"intervention": got_intervention, "escalation_level": result.get('escalation_level')},
        "failures": failures,
        "response_time": f"{elapsed}s"
    }

def run_harness() -> dict:
    results = []
    passed = 0
    failed = 0
    
    for test in TEST_CASES:
        try:
            if test['agent'] == "RiskAgent":
                result = evaluate_risk_agent(test)
            elif test['agent'] == "RecoveryAgent":
                result = evaluate_recovery_agent(test)
            else:
                continue
            
            results.append(result)
            if result['status'] == "PASS":
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            results.append({
                "test_id": test['id'],
                "agent": test['agent'],
                "description": test['description'],
                "status": "ERROR",
                "error": str(e),
                "response_time": "N/A"
            })
            failed += 1
    
    total = len(results)
    accuracy = round((passed/total)*100, 1) if total > 0 else 0
    
    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "accuracy": f"{accuracy}%",
        "grade": "A" if accuracy >= 90 else "B" if accuracy >= 75 else "C",
        "results": results
    }