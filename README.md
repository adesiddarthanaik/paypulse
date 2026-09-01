# PayPulse 🚀
### AI-Powered Merchant Intelligence — Built on Razorpay APIs

> **Razorpay Buildathon 2026 — Track 5 (Open Track)**
> One unified AI agent system covering all 4 buildathon tracks.

---

## The Problem

15-18% of all digital payments in India fail. Merchants lose crores of rupees silently every day — to failed payments, fraud, abandoned checkouts, and unreconciled settlements. They have no intelligent system to fight back.

**PayPulse fixes this.**

---

## What is PayPulse?

PayPulse is a multi-agent AI system that autonomously manages every money problem a Razorpay merchant faces — recovery, risk, growth, and finance — in one unified platform.

```
Failed Payment → PayPulse → Money Recovered
Suspicious Transaction → PayPulse → Risk Scored + Human Review
Idle Customer → PayPulse → Personalized Upsell Generated
Settlement Mismatch → PayPulse → Exception Detected + Report
```

---

## Live Demo

| Service | URL |
|---------|-----|
| Dashboard | Coming Soon |
| API Docs | Coming Soon |
| GitHub | https://github.com/adesiddarthanaik/paypulse |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Next.js Dashboard                  │
│         Recovery │ Risk │ Growth │ Finance │ Audit   │
└─────────────────────┬───────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────┐
│                   FastAPI Backend                    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              LangGraph Agent Graph                   │
│                                                      │
│   Payment → [Risk Node] → [RAG Node] → [Recovery]   │
│                  ↓                         ↓         │
│            HITL Queue              [Audit Node]      │
└──────┬───────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────┐
│  Groq LLM (allam-2-7b)  │  ChromaDB (RAG Memory)   │
│  SQLite (Audit + Memory) │  Razorpay Test APIs      │
└─────────────────────────────────────────────────────┘
```

---

## 4 AI Agents

### 💰 Recovery Agent — Track 3
Detects failed payments, diagnoses root cause using LLM, and executes the right recovery intervention automatically.

**Capabilities:**
- Classifies failure type: UPI Timeout, Bank Decline, Card Expired, OTP Timeout, Insufficient Funds, Subscription Lapse
- Generates personalized Hinglish WhatsApp messages per failure type
- Creates real Razorpay payment links via test API
- 4-level escalation system with hard stopping rules (max 3 attempts)
- Customer memory — remembers past interactions, escalates intelligently

**Example Output:**
```
"Aapka UPI payment timeout ho gaya. Iss link se abhi complete karein 👇 rzp.io/l/xK92mP"
Escalation Level: 2 | Memory Used: true | Confidence: 85%
```

---

### 🛡️ Risk Agent — Track 2
Dynamic risk scoring engine that evaluates every payment before recovery is attempted.

**Capabilities:**
- Risk score 0-100 with explainable factors (amount, failure pattern, time of day, velocity)
- Three-tier decision: AUTO APPROVE → HUMAN REVIEW → AUTO BLOCK
- Full Human-in-the-Loop (HITL) — flagged payments appear in review queue
- Human Approve → triggers RecoveryAgent automatically
- Human Reject → permanently blocks payment
- Every decision logged with reasoning in audit trail

**Risk Factor Example:**
```
Risk Score: 72/100
• High amount: +25
• Suspicious failure code: +20
• Multiple previous attempts: +20
• Unusual transaction time: +15
Decision: HUMAN_REVIEW → Awaiting approval
```

---

### 📈 Growth Agent — Track 1
Analyzes customer purchase history and generates personalized upsell offers in Hinglish.

**Capabilities:**
- Customer segmentation based on purchase history
- Next-best-offer recommendation via LLM
- Hinglish personalized messages
- Real Razorpay payment links for upsell offers

**Example Output:**
```
Customer: Rahul Sharma (bought Running Shoes)
Recommendation: Yoga Mat — "Rahul bhai, running ke saath yoga 
mat bhi lelo — sirf ₹899 mein!"
```

---

### 📊 Finance Agent — Track 4
Automated settlement reconciliation with AI-powered exception detection.

**Capabilities:**
- Multi-record batch reconciliation (50+ records)
- Matches settlements, identifies pending and failed
- AI classifies each exception with likely cause and confidence score
- Generates daily finance summary report
- 96.7% match rate on synthetic dataset

---

## Key Technical Features

### LangGraph Agent Graph
```python
Payment → Risk Node → RAG Node → Recovery Node → Audit Node
              ↓
         HITL Queue (if HUMAN_REVIEW)
```
Proper state machine with conditional routing. Not just Python functions — a real agent graph.

### RAG Memory (ChromaDB)
Every processed payment is stored as a vector embedding. When a new payment arrives, the agent retrieves the 3 most similar past cases and uses them to inform its decision.

### Customer Memory Layer
SQLite-backed memory tracks every customer interaction:
- Total failures, total attempts
- Last intervention used
- Escalation level
- Last contact timestamp

### Human-in-the-Loop (HITL)
Medium-risk payments (score 40-70) are never auto-processed. They go to a human review queue. The merchant can Approve (triggers recovery) or Reject (permanently blocks). Every decision is audited.

### Confidence Scores
Every agent decision returns a confidence percentage:
```json
{
  "decision": "BLOCK",
  "risk_score": 82,
  "confidence": 95,
  "factors": [...]
}
```

### Audit Trail
Every agent decision — diagnosis, intervention, reasoning, outcome — is logged with timestamp. Judges and merchants can trace exactly why the AI did what it did.

---

## Tech Stack

| Layer | Technology | Cost |
|-------|-----------|------|
| Frontend | Next.js 14 + Tailwind CSS | Free |
| Backend | FastAPI + Python | Free |
| Agent Framework | LangGraph | Free |
| LLM | Groq API (allam-2-7b) | Free tier |
| Vector DB | ChromaDB + Sentence Transformers | Free |
| Database | SQLite | Free |
| Payments | Razorpay Test Mode | Free |
| Deploy FE | Vercel | Free |
| Deploy BE | Railway | Free |
| **Total** | | **₹0** |

---

## Results (Demo)

```
Total Payments Processed:    400
Recovery Attempted:           30
Amount Recovered:        ₹1,48,378
Recovery Rate:               7.5%
Customers Tracked (Memory):    6
Risk Decisions Made:          40
Human Reviews Flagged:         7
Finance Match Rate:          96.7%
```

---

## How to Run Locally

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python synthetic_data.py     # seed 50 payments
uvicorn main:app --reload    # starts on :8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                  # starts on :3000
```

### Environment Variables
Create `backend/.env` :
```
GROQ_API_KEY=your_groq_key
RAZORPAY_KEY_ID=your_rzp_key
RAZORPAY_KEY_SECRET=your_rzp_secret
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run-batch` | Run all agents on pending payments |
| POST | `/api/run-growth` | Run growth agent |
| POST | `/api/run-finance` | Run finance agent |
| GET | `/api/metrics` | Get recovery metrics |
| GET | `/api/audit-trail` | Get full audit log |
| GET | `/api/hitl-queue` | Get human review queue |
| POST | `/api/hitl-decision/{id}` | Approve or reject payment |
| GET | `/api/performance` | Get agent performance stats |

---

## Why PayPulse Wins

**Problem taste** — Every Razorpay merchant loses money to failed payments. This is real, measurable, and urgent.

**Build quality** — LangGraph state machine, RAG memory, HITL, confidence scores, audit trail. Production-grade architecture.

**AI judgment** — The AI decides when NOT to act (stopping rules, HITL for medium risk). That's the right use of AI.

**Failure recovery** — Stopping rules, escalation levels, permanent blocks, and human oversight handle every edge case gracefully.

**India-first** — Hinglish messages, UPI failure patterns, Indian merchant workflows. Not a generic global product.

---

## Built By

**Ade Siddartha Naik**
B.Tech Information Technology — NIT Jalandhar (2023-2027)
GitHub: [@adesiddarthanaik](https://github.com/adesiddarthanaik)

---

*Built for Razorpay Buildathon 2026 — Track 5 (Open Track)*
