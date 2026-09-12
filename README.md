# Saarthi Finance

> **Banking that understands your next step.**

An explainable financial guidance and responsible lending-assistance platform for Bharat. Built at a 36-hour hackathon for customers in Tier 2, Tier 3, and rural India.

---

## The Problem

Banking infrastructure has gone digital. But for customers in Bharat:

- They receive the same product offers as metro customers, regardless of their actual financial situation
- Financial products are pushed, not explained — in English, not their language
- There is no early warning when finances are quietly coming under stress
- The question "should I take a loan right now?" has no trustworthy, personalised answer

---

## The Solution

Saarthi Finance starts with the customer's **financial reality**, then recommends the **safest next step** — explained simply, in their preferred language.

> **Key differentiator:** The platform knows **when not to recommend a loan.**

That directly addresses responsible lending, customer trust, explainability, and genuine personalisation.

---

## Product Identity

| | |
|---|---|
| **Product name** | Saarthi Finance |
| **Tagline** | Banking that understands your next step. |
| **Positioning** | Explainable financial guidance and responsible lending-assistance platform for Bharat |
| **Primary language** | Hindi, English, Marathi, Tamil, Bengali |
| **Demo customer** | Ananya Verma, Indore, Madhya Pradesh |

---

## Features

| Feature | Description |
|---|---|
| **Financial Health Score** | Transparent, component-wise 0–100 score with plain-language explanation |
| **Cash Flow Dashboard** | Income, expenses, EMI, and savings breakdown in real time |
| **Responsible Borrowing** | Safe loan amount ranges; loan recommendation suppressed during financial stress |
| **Spending Analysis** | Category-wise donut chart + monthly trend + behavioural insights |
| **Goal Planning** | Track and create savings goals with progress bars and monthly contribution calculation |
| **What-If Simulator** | EMI and savings sliders with live affordability warnings |
| **AI Assistant** | Hindi/English chat grounded in customer's actual dashboard data |
| **Financial Alerts** | Stress alerts with specific evidence and recommended action |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS + Recharts |
| Backend | Python 3.11 + FastAPI + Pydantic v2 + SQLModel |
| Database | SQLite (development), Supabase PostgreSQL (production) |
| ML / Data | Python + pandas + scikit-learn (rule-based, no black-box models) |
| Auth | Mock JWT (prototype), Supabase Auth (production) |
| AI Assistant | Deterministic template fallback; OpenAI-compatible LLM optional |
| Deployment | Vercel (frontend), Render / Railway (backend) |

---

## Repository Structure

```
saarthi-finance/
├── apps/
│   ├── web/                    # React + TypeScript frontend
│   │   └── src/
│   │       ├── pages/          # 8 screens
│   │       ├── data/           # Seed mock data
│   │       ├── lib/            # API client + auth context
│   │       └── types/          # Shared TypeScript types
│   └── api/                    # FastAPI backend
│       └── app/
│           ├── routers/        # 12 API routers
│           ├── services/       # Business logic
│           ├── schemas/        # Pydantic models
│           ├── models/         # SQLModel ORM models
│           ├── seed.py         # Auto-seed on startup
│           └── main.py         # FastAPI app entry
├── data/
│   ├── seed/                   # Synthetic CSV datasets
│   └── processed/              # ML-generated JSON fixtures
├── ml/
│   ├── src/                    # Intelligence modules
│   ├── notebooks/              # Evaluation scripts
│   └── README.md
├── docs/
│   ├── architecture.md         # System architecture + Mermaid diagrams
│   ├── responsible-ai.md       # AI governance documentation
│   ├── demo-script.md          # 4-minute presentation guide
│   └── qa-checklist.md         # 133-item QA checklist
├── shared/
│   └── api-contracts/          # API contract documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- npm or yarn

### 1. Clone and Configure

```bash
git clone <repository-url>
cd saarthi-finance
cp .env.example .env
```

Edit `.env` with your local settings.

### 2. ML / Data Layer (Laptop 3)

```bash
# Generate synthetic seed data
python ml/src/generate_data.py

# Run full pipeline and export fixtures
python ml/src/export_fixtures.py

# Evaluate pipeline
python -X utf8 ml/notebooks/evaluate.py
```

### 3. Backend (Laptop 2)

```bash
cd apps/api

# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend auto-seeds demo data on first startup.

### 4. Frontend (Laptop 1)

```bash
cd apps/web
npm install
npm run dev
```

Open: http://localhost:5173

### 5. Verify

```bash
# Backend health check
curl http://localhost:8000/health

# Dashboard data for demo customer
curl http://localhost:8000/api/v1/customers/cust_001/dashboard
```

---

## Demo Credentials

```
Mobile number:  9876543210
OTP:            123456
Customer:       Ananya Verma
City:           Indore, Madhya Pradesh
Language:       Hindi
```

**Alternative demo customers:**

| Name | ID | Health Score | Profile |
|---|---|---|---|
| Ananya Verma | cust_001 | 76 | Stable income, moderate expense pressure |
| Ramesh Patil | cust_002 | 38 | EMI stress — loan recommendation SUPPRESSED |
| Meena Devi | cust_003 | 82 | Growing saver — goal planning recommended |
| Arjun Kumar | cust_004 | 55 | Unusual spending pattern — alert triggered |

---

## Key API Endpoints

```
GET  /health
GET  /docs                                              # Interactive API documentation

POST /api/v1/auth/demo-login                            # Demo authentication

GET  /api/v1/customers/{id}                             # Customer profile
GET  /api/v1/customers/{id}/dashboard                   # Full dashboard data
GET  /api/v1/customers/{id}/transactions                # Transaction history
GET  /api/v1/customers/{id}/spending                    # Spending analysis
GET  /api/v1/customers/{id}/recommendations             # Responsible recommendation
GET  /api/v1/customers/{id}/alerts                      # Financial alerts
GET  /api/v1/customers/{id}/goals                       # Savings goals
POST /api/v1/customers/{id}/goals                       # Create goal

POST /api/v1/simulator/emi                              # EMI and affordability calculation
POST /api/v1/simulator/goal                             # Goal projection

POST /api/v1/assistant/chat                             # AI assistant (Hindi + English)
POST /api/v1/transactions/ingest                        # Load transaction CSV

GET  /api/v1/seed/reload                                # Reload demo data
```

---

## Environment Variables

```env
# Frontend (apps/web/.env)
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=false                 # Set to true for offline demo

# Backend (apps/api/.env)
DATABASE_URL=                       # Leave empty for SQLite (auto-created)
JWT_SECRET=saarthi-dev-secret
LLM_API_KEY=                        # Optional: OpenAI-compatible key
LOG_LEVEL=INFO
```

---

## Responsible AI Safeguards

| Safeguard | Implementation |
|---|---|
| **No protected attributes** | Caste, religion, gender, language, location not used in scoring |
| **Loan suppression** | Suppressed automatically when health score < 45 or EMI burden > 40% |
| **Explainability** | Every score, alert, and recommendation includes evidence + rationale |
| **Confidence disclosure** | Confidence level shown on all recommendations (0–1 scale) |
| **Human review flag** | Stressed customers flagged `human_review_required: true` |
| **No guarantee language** | Disclaimers on all loan-related outputs — guidance, not approval |
| **Affordability first** | Safe amount ranges shown, not maximum eligible amounts |
| **Synthetic data only** | No real personal data used in this demonstration |
| **Customer rights** | "Talk to Support" action on every alert for escalation |

See [`docs/responsible-ai.md`](docs/responsible-ai.md) for full governance documentation.

---

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for:
- High-level architecture diagram
- Data flow sequence diagram
- Intelligence engine flowchart
- Responsible recommendation engine decision tree
- Database ERD
- Deployment architecture

---

## Limitations

- All data is synthetic and for demonstration purposes only
- Recommendations are not a substitute for certified financial advice
- Credit eligibility depends on bureau data and institutional credit policies
- The AI assistant uses deterministic templates without a configured LLM API key
- No real-time transaction data integration in this prototype
- No bureau score (CIBIL / Experian) integration

---

## Future Scope

| Capability | Description |
|---|---|
| Account Aggregator integration | Real-time financial data via AA framework (NBFC-AA) |
| Bureau score integration | CIBIL / Experian API for full credit assessment |
| Regional language expansion | Odia, Kannada, Punjabi, Gujarati |
| Agent-assisted loan flow | Human advisor review before any credit decision |
| DPDP Act compliance audit trail | Full audit log with consent records |
| Production ML models | Trained on real (anonymised, consented) transaction data |
| UPI deep linking | One-tap savings goal transfers |
| WhatsApp assistant | Saarthi on WhatsApp for feature phone users |

---

## Documentation

| Document | Path |
|---|---|
| System Architecture | [`docs/architecture.md`](docs/architecture.md) |
| Responsible AI Governance | [`docs/responsible-ai.md`](docs/responsible-ai.md) |
| 4-Minute Demo Script | [`docs/demo-script.md`](docs/demo-script.md) |
| QA Test Checklist | [`docs/qa-checklist.md`](docs/qa-checklist.md) |
| API Contract | [`shared/api-contracts/api_contract.md`](shared/api-contracts/api_contract.md) |
| ML Data README | [`ml/README.md`](ml/README.md) |

---

## Team

Built at a 36-hour hackathon by Team Saarthi.

| Role | Responsibility |
|---|---|
| Laptop 1 | Frontend — React, TypeScript, Vite, all 8 screens |
| Laptop 2 | Backend — FastAPI, financial logic, database |
| Laptop 3 | Data and ML — synthetic data, scoring, segmentation |
| Laptop 4 | Architecture, documentation, QA, integration |

---

> *Saarthi* (सारथी) means **guide** or **charioteer** in Hindi — the one who helps you navigate your journey. In the Mahabharata, Lord Krishna served as Arjuna's Saarthi — not to fight for him, but to guide him wisely. That is exactly what this platform aims to do for every customer in Bharat.
