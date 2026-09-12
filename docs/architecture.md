# Saarthi Finance — System Architecture

> **Banking that understands your next step.**
> An explainable financial guidance and responsible lending-assistance platform for Bharat.

---

## Overview

Saarthi Finance is a layered, event-driven platform that converts raw synthetic financial behaviour into explainable, actionable guidance. The architecture separates concerns clearly: data ingestion, feature engineering, intelligence (rules + optional ML), API service, and presentation.

The platform **never** makes automatic credit decisions. Every output carries:
- Input factors used
- Decision logic applied
- Confidence level
- Human-review flag when needed

---

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph Customer["Customer — Bharat"]
        C1[Mobile Browser / App]
    end

    subgraph Frontend["Frontend — React + Vite + TypeScript"]
        F1[Login Page]
        F2[Dashboard]
        F3[Spending Analysis]
        F4[Responsible Borrowing]
        F5[Goal Planning]
        F6[What-If Simulator]
        F7[AI Assistant]
        F8[Alerts Screen]
        F9[API Client Layer with Mock Fallback]
    end

    subgraph Backend["Backend — FastAPI + Python 3.11"]
        B1[Auth Router]
        B2[Customer Router]
        B3[Dashboard Router]
        B4[Transactions Router]
        B5[Spending Router]
        B6[Recommendations Router]
        B7[Alerts Router]
        B8[Goals Router]
        B9[Simulator Router]
        B10[Assistant Router]
        B11[Ingest Router]
    end

    subgraph Services["Service Layer"]
        S1[Financial Health Calculator]
        S2[Recommendation Engine]
        S3[Alert Generation Service]
        S4[Spending Analyser]
        S5[Simulator Engine]
        S6[AI Assistant Service]
        S7[Data Ingest and Categorisation]
    end

    subgraph Database["Database — SQLite / Supabase PostgreSQL"]
        D1[(Customers)]
        D2[(Transactions)]
        D3[(Loans)]
        D4[(Goals)]
        D5[(Alerts)]
    end

    subgraph DataLayer["Data and ML Layer — Python + pandas"]
        ML1[Synthetic Data Generator]
        ML2[Transaction Categoriser]
        ML3[Feature Engineering]
        ML4[Financial Health Scoring]
        ML5[Behavioural Segmentation]
        ML6[Anomaly Detection]
        ML7[Stress Signal Detector]
        ML8[Responsible Recommendation Engine]
        ML9[JSON Fixture Exporter]
    end

    subgraph ExternalOptional["External — Optional"]
        E1[OpenAI-Compatible LLM API]
        E2[Supabase Auth]
    end

    C1 --> F1
    F1 --> F2
    F2 --> F3
    F2 --> F4
    F2 --> F5
    F2 --> F6
    F2 --> F7
    F2 --> F8
    F9 -.->|HTTP + CORS| B1
    F9 -.->|HTTP + CORS| B3
    F9 -.->|HTTP + CORS| B6
    F9 -.->|HTTP + CORS| B7
    F9 -.->|HTTP + CORS| B9
    F9 -.->|HTTP + CORS| B10
    F9 -->|Mock fallback if offline| F2

    B1 --> S1
    B3 --> S1
    B3 --> S2
    B3 --> S3
    B3 --> S4
    B6 --> S2
    B7 --> S3
    B9 --> S5
    B10 --> S6
    B11 --> S7

    S1 --> D1
    S1 --> D2
    S2 --> D1
    S3 --> D5
    S4 --> D2
    S7 --> D2

    ML1 --> D1
    ML1 --> D2
    ML3 --> ML4
    ML4 --> ML7
    ML7 --> ML8
    ML8 --> ML9
    ML9 -->|JSON fixtures| B11

    S6 -.->|Optional| E1
    B1 -.->|Optional| E2
```

---

## Data Flow Sequence

```mermaid
sequenceDiagram
    actor Customer
    participant Frontend
    participant API
    participant Services
    participant DB

    Customer->>Frontend: Open app / Login
    Frontend->>API: POST /api/v1/auth/demo-login
    API-->>Frontend: JWT token + customer_id

    Customer->>Frontend: Navigate to Dashboard
    Frontend->>API: GET /api/v1/customers/cust_001/dashboard
    API->>DB: Fetch customer, transactions, goals
    DB-->>API: Raw data
    API->>Services: Calculate financial health
    API->>Services: Generate recommendations
    API->>Services: Generate alerts
    Services-->>API: Health score, recommendation, alerts
    API-->>Frontend: Complete DashboardData JSON
    Frontend-->>Customer: Render dashboard with insights

    Customer->>Frontend: Ask Hindi question in Assistant
    Frontend->>API: POST /api/v1/assistant/chat
    API->>Services: Ground response in customer profile
    Services-->>API: Contextualised reply with disclaimer
    API-->>Frontend: Hindi or English reply
    Frontend-->>Customer: Display response with disclaimer

    Customer->>Frontend: Use What-If Simulator
    Frontend->>API: POST /api/v1/simulator/emi
    API->>Services: Calculate EMI, affordability, health impact
    Services-->>API: SimulatorOutput with warnings
    API-->>Frontend: EMI result + affordability warning
    Frontend-->>Customer: Show results with safety alerts
```

---

## Intelligence Engine Flow

```mermaid
flowchart LR
    A[Customer Consent] --> B[Data Ingestion CSV or API]
    B --> C[Validation and Categorisation]
    C --> D[Feature Engineering\nSavings rate, EMI ratio,\nexpense volatility, trends]
    D --> E[Financial Profile\nMonthly aggregation,\nrecurring detection]
    E --> F[Behaviour Analysis\nBehavioural segment,\nanomaly detection]
    F --> G[Risk and Stress Signals\nDeclining savings,\nnegative cash flow,\nhigh EMI burden]
    G --> H{Responsible\nRecommendation\nEngine}
    H -->|Score lt 45 OR EMI gt 40pct| I[Loan Suppressed\nCounselling suggested]
    H -->|Savings rate lt 10pct| J[Savings Plan\nRecommended]
    H -->|Healthy profile| K[Safe Borrowing Range\nor Emergency Fund]
    I --> L[Personalised Dashboard\nand Assistant Response]
    J --> L
    K --> L
    L --> M[Feedback and Monitoring\nAudit log]
```

---

## Responsible Recommendation Engine

```mermaid
flowchart TD
    Input[Customer Profile\nand Cash Flow Data] --> R1{Financial Health\nScore below 45?}
    R1 -->|Yes| Suppress1[Suppress ALL loans\nRecommend counselling\nhuman review required]
    R1 -->|No| R2{EMI to Income\nratio above 40 percent?}
    R2 -->|Yes| Suppress2[Suppress new loans\nRecommend restructuring\nhuman review required]
    R2 -->|No| R3{Savings rate\nbelow 10 percent?}
    R3 -->|Yes| Rec1[Recommend savings plan\nconfidence 0.87]
    R3 -->|No| R4{Savings rate\n20 percent or above?}
    R4 -->|Yes| Rec2[Emergency savings buffer\nconfidence 0.91]
    R4 -->|No| R5{Savings rate\n15 percent or above?}
    R5 -->|Yes| Rec3[Term insurance\nconfidence 0.78]
    R5 -->|No| Rec4[Recurring deposit\nconfidence 0.82]

    Suppress1 --> Output[Output with why plus warning plus disclaimer]
    Suppress2 --> Output
    Rec1 --> Output
    Rec2 --> Output
    Rec3 --> Output
    Rec4 --> Output
```

---

## Component Reference

### Frontend — `apps/web`

| Component | Technology | Notes |
|---|---|---|
| Framework | React 18 + TypeScript | Strict mode |
| Build tool | Vite | Fast HMR, ESM output |
| Styling | Tailwind CSS | CSS variables for theme |
| Charts | Recharts | Donut, bar, area charts |
| Routing | React Router v6 | SPA with protected routes |
| State | Context API | AuthContext for session |
| API client | `lib/api.ts` | Real API + mock fallback |
| Mock data | `data/mockData.ts` | Ananya Verma persona |

**Pages:** LoginPage, DashboardPage, SpendingPage, BorrowingPage, GoalsPage, SimulatorPage, AssistantPage, AlertsPage

### Backend — `apps/api`

| Component | Technology | Notes |
|---|---|---|
| Framework | FastAPI 0.110+ | Auto OpenAPI docs at /docs |
| Validation | Pydantic v2 | Request/response schemas |
| ORM | SQLModel | SQLite / PostgreSQL compatible |
| Database | SQLite dev, Supabase prod | Auto-seeded on startup |
| Auth | Mock JWT | Supabase-compatible design |
| CORS | FastAPI middleware | localhost + 127.0.0.1 any port |
| Logging | Python stdlib | Structured with level config |
| Seed | `app/seed.py` | Auto-runs on startup |

### Data and ML — `ml/src`

| Module | Purpose |
|---|---|
| `generate_data.py` | Creates 10 customer synthetic datasets |
| `preprocess.py` | Schema validation, categorisation, deduplication |
| `features.py` | 11 engineered features per customer |
| `health_score.py` | Weighted, explainable 0–100 scoring |
| `segmentation.py` | Rule-based behavioural segments |
| `anomaly.py` | IQR + rolling median anomaly detection |
| `stress.py` | Multi-signal financial stress classifier |
| `recommendations.py` | Responsible product recommendation engine |
| `personas.py` | Named demo personas (Ananya, Ramesh, Meena, Arjun) |
| `export_fixtures.py` | Exports JSON for backend consumption |

---

## Financial Health Score Components

| Component | Weight | Scoring Logic |
|---|---|---|
| Income Stability | 18% | stable=85, variable=55, declining=30 adjusted by variance |
| Savings Rate | 18% | 30%+ gives 95; 20%+ gives 75; 10%+ gives 50; below 5% gives 20 |
| Expense Management | 15% | Expense/income: below 40% gives 90; above 80% gives below 20 |
| Debt Burden | 18% | EMI/income: below 10% gives 95; below 30% gives 75; above 50% gives below 20 |
| Repayment Behaviour | 15% | 0 missed gives 95; below 5% miss rate gives 80; above 20% gives below 25 |
| Liquidity | 16% | Emergency fund months: 6+ gives 95; 3+ gives 75; below 0.5 gives 15 |

---

## Database Entity Relationship

```mermaid
erDiagram
    Customer {
        string id PK
        string name
        string city
        string state
        string preferred_language
        string occupation
        float monthly_income
        int dependents
        string customer_segment
    }

    Transaction {
        string id PK
        string customer_id FK
        date date
        float amount
        string type
        string merchant
        string category
        string channel
        bool recurring
    }

    Loan {
        string id PK
        string customer_id FK
        string loan_type
        float principal
        float outstanding_amount
        float emi_amount
        float interest_rate
        int tenure_months
        string repayment_status
    }

    Goal {
        string id PK
        string customer_id FK
        string goal_type
        string name
        float target_amount
        float current_amount
        date target_date
        float monthly_contribution
    }

    Alert {
        string id PK
        string customer_id FK
        string type
        string severity
        string title
        string description
        string evidence
        string action
    }

    Customer ||--o{ Transaction : "has"
    Customer ||--o{ Loan : "holds"
    Customer ||--o{ Goal : "tracks"
    Customer ||--o{ Alert : "receives"
```

---

## Deployment Architecture

```mermaid
graph LR
    subgraph Local["Local Development"]
        L1[Frontend port 5173\nvite dev]
        L2[Backend port 8000\nuvicorn reload]
        L3[SQLite local file]
    end

    subgraph Production["Production Deployment"]
        P1[Vercel\nFrontend build]
        P2[Render or Railway\nPython API]
        P3[Supabase\nPostgreSQL]
    end

    L1 <-->|VITE_API_URL| L2
    L2 <-->|SQLAlchemy| L3
    P1 <-->|VITE_API_URL prod| P2
    P2 <-->|DATABASE_URL| P3
```

---

## Environment Variables

| Variable | Used By | Description |
|---|---|---|
| `VITE_API_URL` | Frontend | Backend base URL |
| `VITE_USE_MOCK` | Frontend | Force mock data when set to true |
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `BACKEND_URL` | Backend | Self-reference for links |
| `LLM_API_KEY` | Backend | OpenAI-compatible key, optional |
| `JWT_SECRET` | Backend | JWT signing secret |
| `LOG_LEVEL` | Backend | Logging verbosity |

---

## Frontend-to-Backend Integration Points

| Frontend function | Backend route | Fallback behaviour |
|---|---|---|
| `getDashboard(id)` | `GET /api/v1/customers/{id}/dashboard` | Returns MOCK_DASHBOARD |
| `demoLogin(phone)` | `POST /api/v1/auth/demo-login` | Returns mock token |
| `getAlerts(id)` | `GET /api/v1/customers/{id}/alerts` | Returns mock alerts |
| `getGoals(id)` | `GET /api/v1/customers/{id}/goals` | Returns mock goals |
| `calculateEmi(input)` | `POST /api/v1/simulator/emi` | Uses local JS formula |
| `sendMessage(req)` | `POST /api/v1/assistant/chat` | Uses template replies |

---

*Architecture version 1.0 — Saarthi Finance Hackathon Build — Laptop 4*
