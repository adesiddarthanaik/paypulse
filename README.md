# PayPulse 🚀
### AI-Powered Merchant Intelligence — Built on Razorpay APIs

> **Razorpay Buildathon 2026 Submission**  
> Covers all 4 tracks: AI Revenue Recovery · AI Risk Manager · AI Growth & Agentic Commerce · AI Finance Controller

[![Live Demo](https://img.shields.io/badge/Live%20Demo-paypulse--seven.vercel.app-blue?style=for-the-badge)](https://paypulse-seven.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-green?style=for-the-badge)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js-black?style=for-the-badge)](https://nextjs.org)

---

## 🎯 The Problem

Indian merchants on Razorpay lose crores every month to:
- **Failed payments** with no automated recovery
- **Fraudulent transactions** that slip past manual review
- **Untapped upsell opportunities** left on the table
- **Finance reconciliation** done manually in spreadsheets

**No existing tool connects all 4 of these problems in one AI-native system.**

---

## 💡 The Solution

PayPulse is a fully agentic merchant intelligence platform that runs **4 specialized AI agents** on top of Razorpay's payment data — recovering lost revenue, blocking fraud, driving growth, and reconciling finances **autonomously**.

---

## 📊 Impact Numbers

| Metric | Value |
|--------|-------|
| 💰 Total Revenue Recovered | ₹2,51,518 |
| 🔄 Recovery Attempts | 90 payments |
| 📦 Payments Processed | 3,300+ |
| 🛡️ Fraud Blocks | Auto-blocked high-risk transactions |
| ⚡ Agent Response Time | < 2 seconds per decision |
| 🧪 Harness Test Accuracy | Graded A across 10 test cases |
| 🤖 AI Agents Deployed | 4 specialized agents |
| 📋 Audit Logs Generated | Every decision logged with reasoning |

---

## 🤖 The 4 AI Agents

### 💰 1. AI Revenue Recovery Agent
- Detects failed payments and diagnoses root cause automatically
- Generates **personalized Hinglish recovery messages** per customer
- Creates real **Razorpay payment links** via API
- Runs as a batch agent across all failed transactions
- **Result:** ₹2,51,518 recovered across 90 attempts

### 🛡️ 2. AI Risk Manager (with Human-in-the-Loop)
- Scores every payment on a **0–100 risk scale** in real time
- **Auto-approves** low risk (<40), **flags for human review** medium risk (40–70), **auto-blocks** high risk (>70)
- Multi-factor scoring: velocity, failure history, amount anomaly, device fingerprint
- Human-in-the-Loop queue with Approve/Reject decisions
- Full audit trail for every risk decision

### 📈 3. AI Growth Agent (Agentic Commerce)
- Analyzes customer purchase history from Razorpay payment data
- Generates **personalized upsell offers in Hinglish** per customer segment
- Creates Razorpay payment links for upsell products automatically
- Identifies high-value customers and cross-sell opportunities

### 📊 4. AI Finance Controller
- Reconciles settlement records against payment data
- Identifies exceptions: pending, failed, mismatched settlements
- Generates **AI-written financial analysis reports**
- Tracks total amounts, settled amounts, and pending reconciliations

---

## 🧪 Agent Evaluation Harness

PayPulse includes a built-in **evaluation harness** with 10 predefined test cases:
- Tests RecoveryAgent and RiskAgent against known expected outputs
- Measures accuracy, intervention correctness, and edge case handling
- Returns a **letter grade (A/B/C)** with pass/fail breakdown
- Demonstrates production-readiness and reliability

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│              (Vercel — paypulse-seven.vercel.app)        │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS API Calls
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│              (Lightning AI + Ngrok Tunnel)               │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Recovery    │  │  Risk        │  │  Growth      │  │
│  │  Agent       │  │  Agent       │  │  Agent       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Finance     │  │  Audit       │  │  Evaluation  │  │
│  │  Agent       │  │  Trail       │  │  Harness     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Groq LLM (llama-3.3-70b)               │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Razorpay API Integration               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python, Uvicorn |
| **AI/LLM** | Groq API (llama-3.3-70b-versatile) |
| **Payments** | Razorpay API (payments, payment links) |
| **Hosting** | Vercel (frontend) + Lightning AI (backend) |
| **Tunnel** | Ngrok |
| **Data** | 3,300+ synthetic Indian merchant payment records |

---

## 🚀 Live Demo

**Frontend:** https://paypulse-seven.vercel.app  
**API Docs:** https://nintendo-afternoon-grill.ngrok-free.dev/docs  
**Health Check:** https://nintendo-afternoon-grill.ngrok-free.dev/api/health

---

## ⚡ Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Razorpay API keys
- Groq API key

### Backend
```bash
git clone https://github.com/adesiddarthanaik/PayPulse.git
cd PayPulse/backend
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
GROQ_API_KEY=your_groq_api_key
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
GEMINI_API_KEY=your_gemini_api_key
EOF

uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd PayPulse/frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
```

Open http://localhost:3000

---

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/run-batch` | POST | Run Recovery Agent on all failed payments |
| `/api/run-growth` | POST | Run Growth Agent — generate upsell offers |
| `/api/run-finance` | POST | Run Finance Controller — reconcile settlements |
| `/api/run-harness` | POST | Run evaluation harness — 10 test cases |
| `/api/hitl-queue` | GET | Load Human-in-the-Loop review queue |
| `/api/hitl-decision/{id}` | POST | Approve or reject a flagged payment |
| `/api/audit-trail` | GET | Full audit log of all agent decisions |
| `/api/performance` | GET | Real-time metrics across all 4 agents |
| `/api/metrics` | GET | Recovery metrics summary |

---
## 👨‍💻 Built By

**Ade Siddartha Naik**  
B.Tech Information Technology — NIT Jalandhar (2023–2027)  
GitHub: [@adesiddarthanaik](https://github.com/adesiddarthanaik)  
Email: siddathaade@gmail.com

---

*Built for Razorpay Buildathon 2026 — "Your code speaks louder than your resume."*
