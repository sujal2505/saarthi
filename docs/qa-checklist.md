# Saarthi Finance — QA Test Checklist

> Run this checklist before submission. Mark each item as PASS, FAIL, or N/A.
> All FAIL items must be resolved or documented as known limitations.

---

## Environment Setup

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 1 | Backend starts without error | `uvicorn app.main:app` exits with "Application startup complete" | | |
| 2 | Database auto-seeds on first run | Customers, transactions, goals, alerts appear in DB | | |
| 3 | Health endpoint responds | `GET /health` returns `{"status": "ok"}` | | |
| 4 | OpenAPI docs accessible | `GET /docs` renders Swagger UI | | |
| 5 | Frontend builds without error | `npm run build` exits with code 0 | | |
| 6 | Frontend dev server starts | `npm run dev` opens on port 5173 | | |
| 7 | TypeScript type check passes | `npx tsc --noEmit` shows no errors | | |
| 8 | Lint passes | `npm run lint` shows no errors | | |

---

## Authentication

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 9 | Login screen loads | Mobile number field, language selector, demo login button visible | | |
| 10 | Demo login with valid number | Redirects to dashboard; auth token stored | | |
| 11 | Language selector shows 5 options | English, Hindi, Marathi, Tamil, Bengali | | |
| 12 | Login with invalid number | Appropriate error message shown | | |
| 13 | Logout clears session | User returned to login screen | | |
| 14 | Protected routes redirect | Visiting /dashboard without auth redirects to login | | |

---

## Dashboard

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 15 | Dashboard loads for Ananya (cust_001) | All sections populate within 3 seconds | | |
| 16 | Greeting shows customer name and city | "Good morning, Ananya — Indore" | | |
| 17 | Financial health score displays | Score 76, label "Stable", visible components | | |
| 18 | Component scores visible | Income stability, savings, expense management, debt burden, repayment, liquidity | | |
| 19 | Positive factors listed | At least 2 positive factors shown | | |
| 20 | Risk factors listed | At least 1 risk factor shown | | |
| 21 | Plain-language explanation visible | Non-technical narrative shown below score | | |
| 22 | Cash flow cards render | Monthly income, expenses, EMI, savings all displayed with ₹ formatting | | |
| 23 | Savings rate shown | 28.8% or equivalent displayed | | |
| 24 | Recommendation card visible | "Build a stronger emergency buffer" or equivalent | | |
| 25 | Warning on recommendation | Disclaimer "This is financial guidance, not loan approval" visible | | |
| 26 | Alert card visible | At least one alert shown with evidence and action | | |
| 27 | Recent transactions visible | At least 5 transactions with date, merchant, category, amount | | |
| 28 | Quick action buttons work | "View spending", "Plan a goal", "Explore borrowing", "Ask Saarthi" navigate correctly | | |

---

## Spending Analysis

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 29 | Spending page loads | No blank screen or error | | |
| 30 | Donut chart renders | Category-wise spending visible with legend | | |
| 31 | Monthly income/expense trend chart renders | 6-month bar or area chart visible | | |
| 32 | Recurring expenses listed | At least 3 recurring expenses (rent, EMI, subscriptions) | | |
| 33 | Insight cards visible | Behavioural insights in plain language | | |
| 34 | Hindi/English toggle works | Switching language changes insight text language | | |
| 35 | Category amounts in ₹ format | Rupee symbol and Indian number formatting (e.g., ₹11,000) | | |

---

## Responsible Borrowing

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 36 | Borrowing screen loads | No blank screen or error | | |
| 37 | Recommended loan category shown | "Emergency Savings Plan" or equivalent | | |
| 38 | Safe borrowing range displayed | Range shown with lower and upper bounds | | |
| 39 | Estimated EMI shown | Calculated EMI in ₹ format | | |
| 40 | Repayment burden percentage shown | e.g., "16.4% of income" | | |
| 41 | Recommendation confidence shown | e.g., "91% confidence" | | |
| 42 | "Why this is recommended" section visible | At least 3 reasons listed | | |
| 43 | Disclaimer warning clearly visible | Non-approval disclaimer text visible | | |
| 44 | No aggressive sales language | No "Apply Now", "Get Instant Approval", "Limited Time Offer" | | |
| 45 | Load stressed customer (cust_002) | Loan suppression message appears instead | | |
| 46 | Suppression reason shown for stressed customer | "High financial stress detected" or equivalent | | |

---

## Goal Planning

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 47 | Goals page loads | Existing goals shown as cards | | |
| 48 | Emergency fund goal visible | Progress bar, target, current amount, monthly contribution | | |
| 49 | Goal progress percentage correct | Matches (current / target) × 100 | | |
| 50 | On-track indicator shown | Green checkmark or "On Track" label | | |
| 51 | Goal creation form opens | Name, target amount, date, monthly contribution fields | | |
| 52 | New goal creates successfully | Appears in list after submission | | |
| 53 | Required monthly contribution calculated | Auto-calculates based on target, current, and date | | |
| 54 | Festival goal marked as off-track | Diwali goal shows warning for insufficient progress | | |

---

## What-If Simulator

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 55 | Simulator page loads | Sliders visible and interactive | | |
| 56 | Loan amount slider works | Adjusting changes EMI immediately | | |
| 57 | Interest rate slider works | Rate change recalculates total repayment | | |
| 58 | Tenure slider works | Longer tenure reduces EMI | | |
| 59 | Monthly EMI calculated correctly | Standard PMT formula: P × r(1+r)^n / ((1+r)^n - 1) | | |
| 60 | Total repayment = EMI × tenure | Verified | | |
| 61 | Total interest = total repayment − principal | Verified | | |
| 62 | EMI-to-income ratio displayed | Shown as percentage | | |
| 63 | New savings rate shown | Calculated after EMI deduction | | |
| 64 | Health impact shown | Delta shown (negative for new EMI) | | |
| 65 | Affordability warning appears when EMI > 40% income | Warning message shown in amber/red | | |
| 66 | High EMI triggers red warning | EMI > 50% shows red critical warning | | |
| 67 | Invalid inputs handled | 0 or negative values show validation message | | |

---

## AI Assistant

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 68 | Assistant page/drawer opens | Chat interface visible | | |
| 69 | Suggested questions visible | At least 3 starter questions shown | | |
| 70 | English question about savings | Relevant response with customer context | | |
| 71 | Hindi question: "Mere liye loan lena sahi rahega?" | Hindi response referencing health score | | |
| 72 | Response references actual customer data | Mentions score, savings rate, or EMI | | |
| 73 | Loan response includes disclaimer | Disclaimer text visible in response | | |
| 74 | EMI question answered | References safe 40% threshold | | |
| 75 | Spending question answered | Directs to Spending Analysis tab | | |
| 76 | Chat history maintained in session | Previous messages visible on scroll | | |
| 77 | Stressed customer (cust_002) gets suppression message | Hindi: loan suppression explained | | |

---

## Alerts

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 78 | Alerts page loads | At least 1 alert visible | | |
| 79 | Cash flow alert shown for rising expenses | Alert with evidence and action | | |
| 80 | Severity labels visible | Low, Medium, High, Critical with colour coding | | |
| 81 | Evidence text visible | Specific data shown (e.g., "₹29,200 → ₹31,800") | | |
| 82 | Action label clickable | "Review Expenses" or "Talk to Support" button present | | |
| 83 | Stressed customer has stress alert | cust_002 shows "Financial stress detected" alert | | |
| 84 | Fraud review alert uses review language | No accusatory "fraud detected" — only "review required" | | |
| 85 | Alerts sorted by severity | Critical/High alerts appear first | | |

---

## API Endpoints

| # | Endpoint | Expected Response | Status | Notes |
|---|---|---|---|---|
| 86 | `GET /health` | `{"status": "ok"}` | | |
| 87 | `POST /api/v1/auth/demo-login` | Token + customer_id returned | | |
| 88 | `GET /api/v1/customers/cust_001` | Customer profile JSON | | |
| 89 | `GET /api/v1/customers/cust_001/dashboard` | Full DashboardData JSON | | |
| 90 | `GET /api/v1/customers/cust_001/transactions` | Array of transactions | | |
| 91 | `GET /api/v1/customers/cust_001/spending` | Spending categories + trend | | |
| 92 | `GET /api/v1/customers/cust_001/recommendations` | Recommendation with explanation | | |
| 93 | `GET /api/v1/customers/cust_001/alerts` | Array of alerts | | |
| 94 | `GET /api/v1/customers/cust_001/goals` | Array of goals | | |
| 95 | `GET /api/v1/customers/cust_002/recommendations` | Loan SUPPRESSED response | | |
| 96 | `POST /api/v1/simulator/emi` | EMI, total repayment, health impact | | |
| 97 | `POST /api/v1/assistant/chat` | Reply in requested language | | |

---

## Responsible AI Checks

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 98 | Ananya gets savings recommendation, not loan | Recommendation type is "savings" | | |
| 99 | cust_002 (Ramesh) loan is suppressed | `suppressed: true` in response | | |
| 100 | Suppression reason is disclosed | `suppression_reason` field populated | | |
| 101 | No loan offered to score < 45 customer | Verified in recommendations response | | |
| 102 | No loan offered when EMI > 40% customer | Verified for cust_004 or similar | | |
| 103 | Recommendation includes `human_review_required` | Field present in all responses | | |
| 104 | All recommendations have `warning` field | Disclaimer text present | | |
| 105 | Alert is "review required" not "fraud detected" | Verified for fraud_review alert type | | |
| 106 | No API keys committed to git | `git log --all -- .env` shows no secrets | | |
| 107 | No real personal data present | All names are synthetic | | |

---

## Mobile and Accessibility

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 108 | Mobile layout (375px) | No horizontal overflow, navigation accessible | | |
| 109 | Tablet layout (768px) | Cards reflow, charts resize | | |
| 110 | Navigation works on mobile | Bottom nav or hamburger menu functional | | |
| 111 | Charts have labels or accessible summaries | No unlabelled data visualisations | | |
| 112 | Form fields have labels | All inputs labelled for screen readers | | |
| 113 | Contrast ratio acceptable | Text on background passes WCAG AA | | |
| 114 | Keyboard navigation works | Tab order logical, focus visible | | |

---

## Performance and Reliability

| # | Test | Expected | Status | Notes |
|---|---|---|---|---|
| 115 | Dashboard loads in under 3 seconds | On local network | | |
| 116 | API failure shows graceful fallback | Frontend shows mock data, not blank screen | | |
| 117 | Simulator invalid input handled | 0 or null values show validation | | |
| 118 | Long assistant message renders correctly | No overflow or truncation | | |
| 119 | No console errors on dashboard load | Browser console clean | | |
| 120 | Build output under 2MB | `npm run build` output checked | | |

---

## Submission Verification

| # | Item | Status | Notes |
|---|---|---|---|
| 121 | README.md is complete and accurate | | |
| 122 | docs/architecture.md created | | |
| 123 | docs/responsible-ai.md created | | |
| 124 | docs/demo-script.md created | | |
| 125 | shared/api-contracts/api_contract.md up to date | | |
| 126 | .env.example present with all variables listed | | |
| 127 | .gitignore includes .env | | |
| 128 | No API keys or secrets in any committed file | | |
| 129 | Demo credentials documented in README | | |
| 130 | Backend requirements.txt is accurate | | |
| 131 | Frontend package.json scripts are accurate | | |
| 132 | All 4 demo customers seeded and accessible | | |
| 133 | Hackathon tag created: `git tag hackathon-final` | | |

---

## Known Limitations (Document Any FAIL Items Here)

| Item | Description | Workaround |
|---|---|---|
| | | |
| | | |

---

*QA checklist version 1.0 — Saarthi Finance Hackathon — Laptop 4*
*All PASS entries confirmed before submission.*
