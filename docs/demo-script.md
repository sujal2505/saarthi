# Saarthi Finance — Demo Script

> 4-minute presentation for hackathon judges
> Narrator: Laptop 4 lead or any team member
> Customer persona: Ananya Verma, Indore, Madhya Pradesh

---

## Pre-Demo Checklist

Before presenting:

- [ ] Backend running: `uvicorn app.main:app --reload --port 8000`
- [ ] Frontend running: `npm run dev` (port 5173)
- [ ] Browser open to `http://localhost:5173`
- [ ] Backend health check: `curl http://localhost:8000/health`
- [ ] If backend unavailable: set `VITE_USE_MOCK=true` in frontend `.env`
- [ ] Browser in fullscreen
- [ ] Font size at 120% (Ctrl + on browser)
- [ ] Mobile view tested (F12 → responsive mode) for showing mobile layout

---

## 0:00 – 0:30 | Opening: The Problem

**[Show browser — open login screen]**

> "Every bank in India now has a mobile app. But digitisation is not the same as personalisation.
>
> A customer in Indore gets the same loan offer as a customer in Mumbai — without anyone understanding her actual financial situation, her real pressures, or what would genuinely help her.
>
> Saarthi Finance changes that."

**Key phrase to emphasise:**
> *"Personalisation that starts with the customer, not the product catalogue."*

---

## 0:30 – 1:00 | Introducing Ananya

**[Stay on Login screen. Point at the language selector and mobile number field.]**

> "Meet Ananya Verma. She lives in Indore, earns ₹58,000 per month, and manages her household carefully.
>
> She opens Saarthi Finance. She selects Hindi as her preferred language. She logs in with her mobile number — no complex passwords, no branch visits.
>
> This is how banking should feel for Bharat."

**[Click Demo Login]**

> "Ananya lands directly on her personalised dashboard. No advertisements. No push notifications. Just her financial reality."

---

## 1:00 – 1:45 | Dashboard: Financial Reality

**[Dashboard loads. Point to each section as you speak.]**

> "Her financial health score is 76 out of 100 — labelled Stable.

**[Point to health score card]**

> "But Saarthi does not just show a number. It explains why.
> - Her income has been stable for six months — that's positive.
> - Her savings rate is 28.8% — above the recommended 20%.
> - However, household expenses have risen over the last two months — that's a risk factor."

**[Point to cash flow cards]**

> "She earns ₹58,000. She spends ₹31,800 on household expenses, ₹9,500 on EMI, and saves ₹16,700 each month."

**[Point to recommendation card]**

> "Her top recommendation is not a loan. It is to build a stronger emergency buffer. And Saarthi explains exactly why."

**[Briefly scroll to transactions if time allows]**

> "Her recent transactions are categorised automatically — groceries, rent, transport, EMI — all visible at a glance."

---

## 1:45 – 2:20 | Responsible Borrowing: Safe Guidance

**[Navigate to Borrowing / Responsible Borrowing screen]**

> "Let's look at the responsible borrowing screen.

> Ananya's safe borrowing range is displayed — not the maximum she could borrow, but the amount that keeps her finances stable.

> The recommended EMI is shown alongside her current repayment burden.

> And notice this section."

**[Point to the 'Why this is recommended' and warning sections]**

> "Every recommendation includes:
> - Why it is suitable for Ananya specifically
> - The confidence level
> - And a clear disclaimer: this is financial guidance, not loan approval.

> We do not use aggressive sales language. We do not promise guaranteed approval.

> Saarthi's responsibility to the customer is stronger than its incentive to sell."

---

## 2:20 – 2:50 | Stress Alert: When NOT to Recommend a Loan

**[Navigate to Alerts screen]**

> "Now let us see what happens when a customer is under financial stress.

> Ananya's alerts show: her monthly expenses are rising. Shopping is 24% above her usual pattern. Cash flow is being squeezed.

> Here is our strongest technical differentiator."

**[Highlight the alert card with evidence and action]**

> "Each alert includes specific evidence — not vague warnings.

> And the recommended action is constructive: review recurring expenses, not 'apply for a loan to bridge the gap.'

> For customers with a health score below 45 — or an EMI burden above 40% — the system automatically suppresses all new loan offers and recommends counselling instead.

> **The platform knows when not to recommend a loan. That is responsible lending."**

---

## 2:50 – 3:30 | AI Assistant and Simulator

**[Navigate to AI Assistant]**

> "Ananya types in Hindi: 'Mere liye abhi loan lena sahi rahega?'
> Which means: Is it a good time for me to take a loan?"

**[Type the question or click a suggested question]**

> "Saarthi responds in Hindi, referencing her actual health score and savings rate.

> It does not say yes. It does not say no. It explains her situation and suggests using the simulator to test a scenario.

> And it ends with a clear disclaimer — every time."

**[Navigate to Simulator]**

> "Ananya opens the What-If Simulator. She adjusts the loan amount to ₹2,00,000 and the tenure to 24 months."

**[Drag sliders]**

> "The EMI recalculates instantly. Her new savings rate and health score impact are shown.

> If the EMI burden becomes unsafe, a warning appears immediately — before she commits to anything.

> This is what financial simulation should look like: educational, calm, and honest."

---

## 3:30 – 4:00 | Impact, Safeguards, and Scale

**[Return to Dashboard or show a slide]**

> "Let me summarise what Saarthi Finance demonstrates:

> First: **Personalisation** — every recommendation is based on the customer's actual income, spending, savings, and obligations.

> Second: **Explainability** — every score, every alert, every recommendation carries evidence and plain-language reasoning.

> Third: **Responsible lending** — the system suppresses loan offers when they would harm the customer. No protected attributes — caste, religion, gender, language — are used in any scoring decision.

> Fourth: **Vernacular inclusion** — Hindi, Marathi, Tamil, and Bengali are supported. The assistant responds in the customer's language.

> Fifth: **Scalability** — the stack is FastAPI + React + Supabase, deployable on Render and Vercel within hours.

> The design is DPDP-ready, aligned with RBI responsible lending principles, and built to grow with the Account Aggregator framework.

> Saarthi Finance is not about more aggressive selling.
> It is about earning the customer's trust — one honest recommendation at a time."

---

## Fallback Instructions

If the backend API is offline during the demo:
1. Set `VITE_USE_MOCK=true` in `apps/web/.env`
2. Restart the frontend with `npm run dev`
3. All screens will load from the offline mock dataset (Ananya Verma's data)
4. The simulator always computes locally — it will work regardless

If the frontend crashes:
1. Open `http://localhost:5173` again
2. The app retains auth state in localStorage
3. Reload if needed — mock data loads instantly

---

## Suggested Questions from Judges

| Question | Talking Point |
|---|---|
| How does the health score work? | Weighted formula across 6 components, all disclosed |
| What prevents bias? | No protected attributes in scoring; income-relative metrics used |
| Is this a real bank product? | Prototype with synthetic data; designed for production-ready architecture |
| How does the LLM work? | Deterministic fallback templates if no API key; grounded in customer's dashboard data |
| What about DPDP compliance? | See responsible-ai.md; designed for compliance, not yet certified |
| Can you show a stressed customer? | Load cust_002 (Ramesh Patil) — loans suppressed, counselling recommended |
| What's the business model? | Financial institutions license this as a responsible advisory layer |

---

## Demo Customer Quick Reference

| Customer | ID | Health Score | Segment | Loan Status |
|---|---|---|---|---|
| Ananya Verma | cust_001 | 76 | Stable planner | Safe borrowing possible |
| Ramesh Patil | cust_002 | 38 | EMI stressed | Loan SUPPRESSED |
| Meena Devi | cust_003 | 82 | Growing saver | Goal planning recommended |
| Arjun Kumar | cust_004 | 55 | High spender | Unusual activity alert |

To switch customers: change `customer_id` in localStorage or use the API directly:
```
GET /api/v1/customers/cust_002/dashboard
```

---

*Demo script version 1.0 — Saarthi Finance Hackathon — Laptop 4*
