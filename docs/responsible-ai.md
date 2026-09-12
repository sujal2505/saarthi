# Saarthi Finance — Responsible AI Documentation

> This document describes the design principles, privacy safeguards, bias mitigations, and governance practices built into Saarthi Finance.
>
> **Important notice:** Saarthi Finance uses synthetic data only. It is a prototype built for a hackathon. This document describes the platform as designed, not as deployed in a production or regulated environment. Nothing in this document constitutes legal advice or a compliance certification.

---

## 1. Foundational Principle

Saarthi Finance is a **decision-support platform**, not an automated credit-decision engine.

Every recommendation, alert, and assistant response:
- Carries an explicit disclaimer that it is guidance and not approval
- Lists the input factors used
- States the confidence level
- Flags whether human review is required
- Avoids guaranteed lending or investment claims

The system is designed to inform and guide customers, not to replace human judgment or regulatory oversight.

---

## 2. Data Governance

### 2.1 Synthetic Data Only

All customer profiles, transactions, loans, and goals in this prototype are **entirely synthetic**. They were generated programmatically using Python scripts and represent realistic but fictional individuals. No real personal data has been used at any stage.

### 2.2 Consent and Purpose Limitation

The platform is designed with the following principles (as they would apply in a production deployment):

- **Explicit consent**: The customer actively initiates the session and sees a plain-language explanation of what data will be used and why
- **Purpose limitation**: Financial data is used only for providing personalized guidance to that customer — not for cross-selling unrelated products, not for sharing with third parties, not for profiling without consent
- **Data minimization**: Only data necessary to compute health scores, recommendations, and alerts is collected. The platform does not request sensitive attributes such as caste, religion, community affiliation, or political views

### 2.3 DPDP Act Readiness

The Digital Personal Data Protection Act 2023 (India) establishes obligations for data fiduciaries. Saarthi Finance is designed with the following DPDP-aligned principles:

| DPDP Principle | Platform Design |
|---|---|
| Notice | Customers see a clear data-use notice at login |
| Consent | Explicit consent required before data processing |
| Purpose limitation | Data used only for guidance to the same customer |
| Data minimisation | Minimum required fields collected |
| Storage limitation | Session-scoped access in prototype |
| Accuracy | Customers can flag incorrect data via assistant |
| Security | JWT auth, HTTPS in transit, structured access control |
| Grievance redressal | "Talk to Support" action in every alert |
| Rights of data principal | Correction and deletion flows designed in |

### 2.4 RBI-Aligned Data Principles

Following the Reserve Bank of India's data protection guidelines for regulated financial entities:

- Customer financial data is classified as sensitive personal data
- The platform does not store raw Aadhaar, PAN, or credit bureau data in this prototype
- Account Aggregator framework compatibility is included in the future roadmap
- Audit logging is implemented for all recommendation and scoring decisions

### 2.5 Data Localisation

In a production deployment, the platform would store all customer financial data in India-based data centers (Supabase India region or AWS ap-south-1), consistent with RBI data localisation requirements for payment and financial data.

---

## 3. Security Design

### 3.1 Authentication

- JWT-based authentication (mock for prototype, Supabase Auth for production)
- Tokens are short-lived and scoped to individual customers
- No plaintext password storage
- Demo credentials are clearly marked as demonstration-only

### 3.2 Encryption

- HTTPS in transit (enforced in all production deployments)
- Database encryption at rest (provided by Supabase / cloud provider)
- API keys are stored as environment variables, never committed to version control

### 3.3 Access Control

- Each API endpoint validates customer identity before returning data
- No cross-customer data leakage: every query is scoped to the authenticated customer ID
- Admin seed endpoints are separated and should be protected or removed in production

### 3.4 Audit Logging

The backend logs all events at structured levels:
- INFO: normal API requests, successful recommendations
- WARNING: unexpected customer data shapes, score edge cases
- ERROR: unhandled exceptions, database failures
- Every recommendation and score calculation logs: customer_id, input parameters, score components, recommendation type, confidence, human_review flag

---

## 4. Explainability

### 4.1 Financial Health Score

The financial health score is a **transparent weighted formula** — not a black box. Each component is individually scored and disclosed:

- `income_stability` (18% weight) — derived from declared income stability and variance
- `savings` (18% weight) — savings rate computed from income and expense data
- `expense_management` (15% weight) — expense-to-income ratio
- `debt_burden` (18% weight) — EMI-to-income ratio
- `repayment_behavior` (15% weight) — missed payment history
- `liquidity` (16% weight) — emergency fund coverage in months

Every score response includes:
- The overall score and label (Excellent / Good / Stable / Fair / Poor)
- Individual component scores
- Plain-language positive factors
- Plain-language risk factors
- A full narrative explanation

**Customers can see exactly why their score changed.**

### 4.2 Recommendations

Every recommendation response includes:
- `why`: a list of reasons grounded in the customer's actual data
- `confidence`: numeric confidence level (0–1)
- `warning`: disclaimer that this is guidance, not approval
- `human_review_required`: boolean flag
- `suppression_reason`: when a loan is suppressed, the reason is explicitly stated

### 4.3 Alerts

Every alert includes:
- `evidence`: the specific data point that triggered the alert (e.g., "Previous: ₹29,200 → Current: ₹31,800")
- `action`: a specific, actionable next step
- `severity`: low, medium, high, or critical
- The alert explicitly avoids accusatory language (e.g., fraud alerts say "review required" not "fraud detected")

### 4.4 Assistant

The AI assistant:
- References the customer's actual dashboard data in every response
- Includes a disclaimer in all responses related to borrowing or investment
- Does not impersonate a bank employee or claim authority to approve products
- Falls back to deterministic templates if no LLM API key is configured

---

## 5. Bias and Fairness

### 5.1 Protected Attributes

**The following attributes are explicitly excluded from all scoring, recommendation, and segmentation logic:**

- Caste or sub-caste
- Religion or community
- Gender or gender identity
- Language preference (used only for communication, not risk assessment)
- Geographic location (Tier 2/3/rural) used only for contextualisation, never as a negative risk factor
- Age (not used as a direct negative risk factor)

This is enforced in code: the financial health calculator accepts only income, expense, EMI, savings, and repayment data — no demographic attributes.

### 5.2 Proxy Discrimination Risk

Even without using protected attributes directly, proxy discrimination can occur through correlated variables (e.g., income level correlated with geography, geography correlated with caste). Mitigation measures:

- The platform uses income-relative metrics (savings rate, EMI-to-income ratio) rather than absolute amounts, which partially corrects for income disparity
- Behavioural segmentation is based on financial behaviour patterns, not demographics
- In a production deployment, periodic fairness audits would compare recommendation rates and score distributions across demographic groups using external demographic data

### 5.3 No Predatory Nudging

The platform is explicitly designed to avoid:
- Recommending high-interest products to financially stressed customers
- Upselling credit products when the customer cannot afford them
- Using aggressive urgency language in recommendations
- Recommending maximum eligible loan amounts instead of safe loan amounts

Loan recommendations include **safe amount ranges** based on affordability, not the maximum a customer could theoretically borrow.

### 5.4 Loan Offer Suppression

When a customer's financial health score is below 45, or their EMI-to-income ratio exceeds 40%, **all new loan recommendations are automatically suppressed**. The customer sees:
- A clear explanation that a loan is not recommended at this time
- The specific reason (stress level, EMI burden)
- A constructive alternative (counselling, savings, restructuring)
- A "Talk to Support" action

This is the key differentiator of the platform: **Saarthi knows when not to recommend a loan.**

---

## 6. Human Review

Any customer flagged for high stress or unusual patterns receives:
- `human_review_required: true` in the recommendation response
- An alert with `action_label: "Talk to Support"`
- An assistant response that explicitly suggests speaking with a financial counsellor

The platform does not attempt to resolve high-complexity financial situations autonomously. Human advisors are positioned as the appropriate escalation path.

---

## 7. Customer Rights and Correction

In a production deployment, customers have the right to:
- **Access**: View all data the platform holds about them
- **Correction**: Flag incorrect transactions or income data
- **Deletion**: Request deletion of their profile and history
- **Appeal**: Challenge an alert or recommendation they disagree with

The current prototype supports the correction workflow via the AI assistant and the "Talk to Support" action in every alert.

---

## 8. Model Drift and Monitoring

For production deployment, the following monitoring practices are recommended:

| Signal | Monitoring Approach |
|---|---|
| Score distribution shift | Weekly comparison of score percentile bands |
| Recommendation suppression rate | Track what % of customers have loans suppressed |
| Alert accuracy | Human review of flagged alerts monthly |
| Assistant response quality | Sampling + rating by financial domain experts |
| Fairness metrics | Quarterly comparison of score distributions across demographic groups |

---

## 9. Data Retention and Deletion

In production:
- Transaction history used for scoring: retained for 24 months
- Customer profile: retained while account is active + 12 months after closure
- Audit logs: retained for 36 months per RBI guidelines
- On deletion request: all personal data anonymised or deleted within 30 days

---

## 10. Limitations of This Prototype

| Limitation | Description |
|---|---|
| Synthetic data only | No real customer data — results are illustrative |
| No bureau integration | No CIBIL, Experian, or Equifax data used |
| No regulatory approval | Not a licensed financial advisory product |
| Rule-based ML | Financial health and recommendations use weighted rules, not learned models from real data |
| LLM fallback | Without an API key, the assistant uses templates which may feel limited |
| No production monitoring | Drift and fairness monitoring described above is not yet implemented |

---

## 11. Alignment with Responsible AI Principles

| Principle | Implementation |
|---|---|
| Transparency | All scores, recommendations, and alerts include explanation and evidence |
| Fairness | No protected attributes in scoring; suppression protects vulnerable customers |
| Accountability | Audit logs for all decisions; human review flags for stressed customers |
| Safety | Loan suppression during stress; affordability warnings in simulator |
| Privacy | Synthetic data only; DPDP-aligned design; consent at login |
| Inclusivity | Multi-language support (Hindi, Marathi, Tamil, Bengali, English) |
| Human oversight | Human review required flag; "Talk to Support" always available |

---

*Responsible AI documentation version 1.0 — Saarthi Finance Hackathon Build — Laptop 4*
*This document describes design intent. It does not constitute a legal or regulatory compliance certification.*
