# Saarthi Finance — Pitch Deck Outline

> 6-slide presentation for hackathon judges
> Each slide has a title, 3–5 talking points, and a key visual suggestion.

---

## Slide 1: The Problem

**Title:** Banking is Digital. Trust is Not.

**Talking points:**
- India has 500M+ digital banking users, but product offers are identical for Indore and Mumbai
- Financial products are pushed in English to customers who think in Hindi
- No early warning when a customer's finances are quietly coming under stress
- Customers are sold the maximum loan they qualify for, not the loan that actually helps them
- The result: debt traps, customer distrust, and financial exclusion in Bharat

**Key visual:** Map of India with Tier 2/3 city highlights — contrast between digital reach and genuine personalisation gap

---

## Slide 2: Saarthi Finance — The Solution

**Title:** Banking that understands your next step.

**Talking points:**
- Starts with the customer's real financial situation — income, spending, savings, obligations
- Recommends the **safest next step**, not the most profitable product
- Explains every decision in plain language, in the customer's own language
- Detects early signs of financial stress and acts protectively, not predatorily
- Key differentiator: **The platform knows when NOT to recommend a loan**

**Key visual:** Dashboard screenshot — Ananya Verma's financial health score, cash flow summary, and recommendation card

---

## Slide 3: How the Intelligence Engine Works

**Title:** Transparent Intelligence, Not a Black Box

**Talking points:**
- 6-component weighted financial health score — every component is disclosed
- Rule-based responsible recommendation engine — no hidden model, no proxy discrimination
- Loan suppression when stress is detected — automatic, rule-enforced, logged
- Behavioural segmentation into 7 interpretable segments
- Statistical anomaly detection using IQR + rolling median — no opaque ML

**Key visual:** Recommendation decision tree diagram (from docs/architecture.md) showing loan suppression flow

---

## Slide 4: Customer Journey

**Title:** Ananya's Journey in 4 Minutes

**Talking points:**
- Logs in with mobile number, selects Hindi language
- Sees her health score (76/100), cash flow, and rising expense alert
- Views responsible borrowing screen — safe range shown, no aggressive upsell
- Asks in Hindi: "Mere liye abhi loan lena sahi rahega?"
- Assistant responds with her actual data, ends with disclaimer
- Tests loan scenario in simulator — warning appears before she commits

**Key visual:** Customer journey flow diagram — 6 steps from login to informed decision

---

## Slide 5: Responsible AI and Compliance

**Title:** Responsible by Design, Not by Disclaimer

| Principle | Implementation |
|---|---|
| No protected attributes | Caste, religion, gender excluded from all scoring |
| Loan suppression | Auto-suppressed when health score < 45 or EMI > 40% |
| Explainability | Evidence shown for every score, alert, recommendation |
| Human review | Stressed customers flagged for advisor escalation |
| Privacy | Synthetic data; DPDP Act-aligned design; consent at login |
| Inclusivity | Hindi, Marathi, Tamil, Bengali, English |

**Talking points:**
- Designed for DPDP Act readiness — consent, purpose limitation, data minimisation
- Aligned with RBI responsible lending principles
- Compatible with Account Aggregator framework for future integration
- Audit log for every scoring and recommendation decision

**Key visual:** Responsible AI principles wheel or table as above

---

## Slide 6: Impact and Future Scalability

**Title:** Personalisation That Scales Across Bharat

**Talking points:**
- Stack: React + FastAPI + Supabase — deployable on Vercel and Render in hours
- AA framework integration ready for 500M+ consented financial profiles
- Multi-language expansion: 8 languages target within 6 months of production deployment
- Business model: Financial institutions license Saarthi as a responsible advisory layer
- Reduces default risk by protecting customers from unaffordable debt
- Builds long-term customer trust — the most durable competitive advantage in banking

**Feature comparison:**

| Feature | Traditional Banking App | Saarthi Finance |
|---|---|---|
| Product recommendation | Same for all customers | Based on individual financial reality |
| Language | English / Hindi | 5 languages + expanding |
| Loan offer during stress | Still shown | Automatically suppressed |
| Explanation | None | Component-by-component rationale |
| Financial simulator | None | Live EMI + affordability calculator |
| Early warning | None | Proactive alerts with evidence |

**Key visual:** Before/after comparison — generic banking app vs. Saarthi personalised dashboard

---

## Key Phrases to Memorise

> "Most banking apps show the same products to everyone. Saarthi starts with the customer's reality."

> "The platform knows when not to recommend a loan. That is responsible lending."

> "Every score, every recommendation, every alert includes evidence — not just a number."

> "We built this for Ananya in Indore, not for a persona in a slide deck."

> "Financial trust is not built through a better UI. It is built through better decisions."

---

*Pitch outline version 1.0 — Saarthi Finance Hackathon — Laptop 4*
