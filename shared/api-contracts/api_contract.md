# Saarthi Finance — API Contract

> Version 1.0 — Hackathon Build
>
> This document defines the shared API response shapes used across the frontend (Laptop 1), backend (Laptop 2), and ML data layer (Laptop 3).
> All laptops must use these shapes exactly to avoid integration failures.

---

## Base URL

```
Development:  http://localhost:8000
Production:   https://saarthi-api.onrender.com   (example)
```

---

## Authentication

### POST /api/v1/auth/demo-login

**Request:**
```json
{
  "phone": "9876543210",
  "language": "hi"
}
```

**Response:**
```json
{
  "token": "demo-jwt-token-ananya",
  "customer_id": "cust_001",
  "name": "Ananya Verma",
  "preferred_language": "hi"
}
```

---

## Customer Profile

### GET /api/v1/customers/{customer_id}

**Response:**
```json
{
  "id": "cust_001",
  "name": "Ananya Verma",
  "city": "Indore",
  "state": "Madhya Pradesh",
  "preferred_language": "hi",
  "occupation": "School Teacher",
  "monthly_income": 58000,
  "dependents": 2,
  "customer_segment": "Stable Planner",
  "age": 34,
  "phone": "9876543210"
}
```

---

## Dashboard

### GET /api/v1/customers/{customer_id}/dashboard

**Full response shape (canonical):**

```json
{
  "customer": {
    "id": "cust_001",
    "name": "Ananya Verma",
    "city": "Indore",
    "state": "Madhya Pradesh",
    "preferred_language": "hi"
  },
  "financial_health": {
    "score": 76,
    "label": "Stable",
    "change": 3,
    "components": {
      "income_stability": 84,
      "savings": 72,
      "expense_management": 70,
      "debt_burden": 75,
      "repayment_behavior": 89,
      "liquidity": 68
    },
    "positive_factors": [
      "Income has remained stable for the last six months",
      "Savings rate is above the recommended minimum (28.8%)"
    ],
    "risk_factors": [
      "Household expenses have increased by 12% recently"
    ],
    "explanation": "Your financial health is stable. You have income that has remained stable for six months. However, household expenses have increased recently. Your savings rate of 28.8% is healthy."
  },
  "cash_flow": {
    "monthly_income": 58000,
    "monthly_expenses": 31800,
    "monthly_emi": 9500,
    "monthly_savings": 16700,
    "savings_rate": 28.8
  },
  "recommendation": {
    "type": "savings",
    "title": "Build a stronger emergency buffer",
    "product": "Emergency Savings Plan",
    "recommended_amount": 5000,
    "estimated_emi": null,
    "confidence": 0.91,
    "why": [
      "Your income is stable and predictable",
      "Your savings rate is currently healthy at 28.8%",
      "Household expenses have been rising — a buffer protects you",
      "A strong emergency fund is the foundation of financial health"
    ],
    "warning": "This is financial guidance, not a loan approval or financial product guarantee. Please consult a certified financial advisor before making major decisions.",
    "human_review_required": false,
    "suppressed": false,
    "suppression_reason": null,
    "loan_suppressed": false
  },
  "alerts": [
    {
      "id": "alert_a1b2c3d4",
      "type": "cash_flow",
      "severity": "medium",
      "title": "Monthly expenses rising steadily",
      "description": "Your household spending increased by ₹2,600 (9%) recently. If this trend continues, your savings rate may drop.",
      "evidence": "Previous: ₹29,200 → Current: ₹31,800",
      "action": "Review your recurring expenses and identify where you can cut back.",
      "action_label": "Review Expenses"
    }
  ],
  "recent_transactions": [
    {
      "id": "t001",
      "date": "2024-09-01",
      "merchant": "HDFC Salary Credit",
      "category": "Salary",
      "amount": 58000,
      "type": "credit",
      "channel": "NEFT",
      "recurring": true
    }
  ],
  "goals": [
    {
      "id": "g001",
      "type": "emergency_fund",
      "name": "Emergency Fund",
      "target_amount": 150000,
      "current_amount": 60000,
      "target_date": "2025-06-30",
      "monthly_contribution": 5000,
      "progress_pct": 40.0,
      "months_remaining": 18,
      "on_track": true
    }
  ],
  "monthly_trend": [
    { "month": "Apr", "income": 58000, "expenses": 28500, "savings": 20000 },
    { "month": "May", "income": 58000, "expenses": 29200, "savings": 19300 },
    { "month": "Jun", "income": 58000, "expenses": 30100, "savings": 18400 },
    { "month": "Jul", "income": 58000, "expenses": 31000, "savings": 17500 },
    { "month": "Aug", "income": 58000, "expenses": 31500, "savings": 17000 },
    { "month": "Sep", "income": 58000, "expenses": 31800, "savings": 16700 }
  ],
  "spending_categories": [
    { "category": "Rent", "amount": 11000, "percentage": 34.6, "color": "#1a2332", "trend": "stable" },
    { "category": "EMI", "amount": 9500, "percentage": 29.9, "color": "#e8770a", "trend": "stable" },
    { "category": "Groceries", "amount": 3950, "percentage": 12.4, "color": "#0d7c6e", "trend": "up", "change_pct": 8 },
    { "category": "Shopping", "amount": 3200, "percentage": 10.1, "color": "#d97706", "trend": "up", "change_pct": 24 }
  ],
  "assistant_context": {
    "summary": "Ananya has stable income, healthy savings rate, and moderate expense pressure. Loan offers are not suppressed."
  }
}
```

---

## Transactions

### GET /api/v1/customers/{customer_id}/transactions

**Query parameters:**
- `start_date` (optional): ISO date string e.g., `2024-09-01`
- `end_date` (optional): ISO date string
- `category` (optional): Transaction category name

**Response:**
```json
[
  {
    "id": "t001",
    "date": "2024-09-01",
    "merchant": "HDFC Salary Credit",
    "category": "Salary",
    "amount": 58000,
    "type": "credit",
    "channel": "NEFT",
    "recurring": true,
    "description": "Monthly salary credit"
  }
]
```

**Valid categories:**
`Salary`, `Groceries`, `Rent`, `Utilities`, `Transport`, `Healthcare`, `Education`, `Shopping`, `Entertainment`, `EMI`, `Savings`, `UPI Transfer`, `Other`

---

## Spending Analysis

### GET /api/v1/customers/{customer_id}/spending

**Response:**
```json
{
  "categories": [
    {
      "category": "Rent",
      "amount": 11000,
      "percentage": 34.6,
      "color": "#1a2332",
      "trend": "stable",
      "change_pct": 0
    }
  ],
  "monthly_trend": [
    { "month": "Apr", "income": 58000, "expenses": 28500, "savings": 20000 }
  ],
  "recurring_expenses": [
    {
      "merchant": "Indore Apartment Rent",
      "category": "Rent",
      "amount": 11000,
      "channel": "NEFT"
    }
  ],
  "insights": [
    "Shopping spend increased by 24% this month compared to your usual pattern.",
    "Your rent is the largest expense at 34.6% of total spending."
  ]
}
```

---

## Recommendations

### GET /api/v1/customers/{customer_id}/recommendations

**Response — healthy customer:**
```json
{
  "type": "savings",
  "title": "Build a stronger emergency buffer",
  "product": "Emergency Savings Plan",
  "recommended_amount": 5000,
  "estimated_emi": null,
  "confidence": 0.91,
  "why": [
    "Your income is stable and predictable",
    "Your savings rate is currently healthy at 28.8%"
  ],
  "warning": "This is financial guidance, not a loan approval.",
  "human_review_required": false,
  "suppressed": false,
  "suppression_reason": null,
  "loan_suppressed": false,
  "category": "savings",
  "not_recommended": ["Personal Loan", "Credit Card"],
  "not_recommended_reason": "Existing EMI burden is moderate; adding new debt would reduce your savings safety margin."
}
```

**Response — stressed customer (loan suppressed):**
```json
{
  "type": "restructure",
  "title": "Focus on stabilizing before borrowing",
  "product": "Financial Counselling Support",
  "recommended_amount": 0,
  "estimated_emi": null,
  "confidence": 0.95,
  "why": [
    "New debt would increase stress significantly",
    "Income instability makes repayments unpredictable",
    "Current EMI burden is already at risk level"
  ],
  "warning": "A loan recommendation is not suitable at this time. Saarthi recommends speaking with a financial counsellor.",
  "human_review_required": true,
  "suppressed": true,
  "suppression_reason": "High financial stress detected. Loan offers suppressed to protect customer.",
  "loan_suppressed": true
}
```

---

## Alerts

### GET /api/v1/customers/{customer_id}/alerts

**Response:**
```json
[
  {
    "id": "alert_a1b2c3d4",
    "type": "cash_flow",
    "severity": "medium",
    "title": "Monthly expenses rising steadily",
    "description": "Your household spending increased by ₹2,600 (9%) recently.",
    "evidence": "Previous: ₹29,200 → Current: ₹31,800",
    "action": "Review your recurring expenses and identify where you can cut back.",
    "action_label": "Review Expenses"
  }
]
```

**Alert types:** `cash_flow`, `unusual_spending`, `missed_emi_risk`, `savings_decline`, `fraud_review`, `stress`, `expense_surge`
**Severity values:** `low`, `medium`, `high`, `critical`

---

## Goals

### GET /api/v1/customers/{customer_id}/goals

**Response:**
```json
[
  {
    "id": "g001",
    "type": "emergency_fund",
    "name": "Emergency Fund",
    "target_amount": 150000,
    "current_amount": 60000,
    "target_date": "2025-06-30",
    "monthly_contribution": 5000,
    "progress_pct": 40.0,
    "months_remaining": 18,
    "on_track": true
  }
]
```

**Goal types:** `emergency_fund`, `education`, `home_repair`, `festival`, `vehicle`, `custom`

### POST /api/v1/customers/{customer_id}/goals

**Request:**
```json
{
  "type": "education",
  "name": "Online Certification",
  "target_amount": 35000,
  "current_amount": 5000,
  "target_date": "2025-03-31",
  "monthly_contribution": 3000
}
```

**Response:** Same as GET single goal, with assigned `id`, `progress_pct`, `months_remaining`, `on_track`.

---

## Simulator

### POST /api/v1/simulator/emi

**Request:**
```json
{
  "loan_amount": 100000,
  "interest_rate": 12.5,
  "tenure_months": 24,
  "customer_id": "cust_001",
  "monthly_savings_delta": 0
}
```

**Response:**
```json
{
  "monthly_emi": 4736,
  "total_repayment": 113664,
  "total_interest": 13664,
  "emi_to_income_ratio": 0.25,
  "new_savings_rate": 22.0,
  "health_impact": -5,
  "is_affordable": true,
  "warning": null
}
```

**Warning triggers:**
- EMI-to-income ratio > 50%: "Combined EMI would exceed 50% of income — this significantly strains your finances."
- EMI-to-income ratio > 40%: "Combined EMI burden is high. Consider a smaller loan amount or longer tenure."
- New savings rate < 10%: "This loan would reduce your savings rate below 10%. Try increasing the tenure."

### POST /api/v1/simulator/goal

**Request:**
```json
{
  "target_amount": 50000,
  "current_amount": 10000,
  "monthly_contribution": 3000
}
```

**Response:**
```json
{
  "months_to_target": 13,
  "target_date_estimate": "2025-10-01",
  "total_contribution": 40000,
  "on_track": true,
  "required_monthly": 3000
}
```

---

## AI Assistant

### POST /api/v1/assistant/chat

**Request:**
```json
{
  "customer_id": "cust_001",
  "message": "Mere liye abhi loan lena sahi rahega?",
  "language": "hi",
  "customer_name": "Ananya"
}
```

**Response:**
```json
{
  "reply": "Ananya ji, aapka financial health score 76 hai jo stable hai. Lekin naya loan lene se pehle emergency fund aur budget zaroor check karein. Yeh guidance hai, formal loan approval nahi.\n\n*Disclaimer: Yeh sirf financial guidance hai. Loan approval ke liye bank se sampark karein.*",
  "language": "hi",
  "grounded_on": ["financial_health_score", "savings_rate", "emi_ratio"],
  "disclaimer": "This response is AI-generated financial guidance. It is not formal financial advice or a lending decision."
}
```

---

## Health Check

### GET /health

**Response:**
```json
{
  "status": "ok",
  "platform": "Saarthi Finance",
  "version": "1.0.0",
  "database": "connected"
}
```

---

## Error Format

All API errors return a consistent shape:

```json
{
  "error": "Not Found",
  "message": "Customer cust_999 not found",
  "path": "/api/v1/customers/cust_999/dashboard"
}
```

**HTTP status codes used:**
- 200: Success
- 201: Created
- 400: Bad request / validation error
- 401: Unauthenticated
- 404: Resource not found
- 422: Pydantic validation failure
- 500: Internal server error

---

## Pagination (Transactions)

Transactions endpoint supports optional pagination:

```
GET /api/v1/customers/cust_001/transactions?skip=0&limit=20
```

Default: `skip=0`, `limit=50`. Maximum `limit=200`.

---

## CORS Configuration

The backend allows requests from:
- `http://localhost:5173` (Vite dev)
- `http://localhost:3000` (Next.js dev)
- `http://127.0.0.1:5173`
- Any `localhost` or `127.0.0.1` origin with any port (via regex)

Production origins must be configured via environment variable.

---

*API contract version 1.0 — Saarthi Finance Hackathon — shared/api-contracts*
