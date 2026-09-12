# Saarthi Finance — ML & Data Layer

## Overview
This directory contains the complete synthetic data generation and intelligence layer for the Saarthi Finance platform.

## What This Does

1. **Generates synthetic data** — 10 realistic Indian Tier 2/3 customer personas with 6 months of transactions, loans, and goals
2. **Preprocesses data** — validates, categorizes, and aggregates transactions
3. **Engineers features** — computes 20+ interpretable financial ratios per customer
4. **Scores financial health** — transparent weighted score (0–100) with component breakdown
5. **Segments customers** — 7 interpretable behavioral segments using rule-based logic
6. **Detects anomalies** — IQR + z-score based statistical detection
7. **Detects stress** — multi-signal stress detection with loan suppression
8. **Generates recommendations** — responsible, customer-benefit-first suggestions
9. **Produces alerts** — severity-graded, evidence-backed financial alerts
10. **Exports JSON fixtures** — for the FastAPI backend and frontend

## Quick Start

```bash
cd ml

# Install dependencies (optional — only pandas/sklearn for enhanced features)
pip install -r requirements.txt

# Step 1: Generate seed data
python src/generate_data.py

# Step 2: Run full pipeline and export fixtures
python src/export_fixtures.py

# Step 3: Run evaluation and tests
python notebooks/evaluate.py
```

## Output Files

```
data/seed/
├── customers.csv          — 10 demo personas
├── transactions.csv       — 6 months of transactions per customer
├── loans.csv              — Active loan records
└── goals.csv              — Financial goals

data/processed/
├── customer_features.json — 20+ features per customer
├── health_scores.json     — Scores with component explanations
├── segments.json          — Behavioral segments
├── stress_signals.json    — Stress detection results
├── recommendations.json   — Responsible recommendations
├── anomalies.json         — Detected anomalies
├── alerts.json            — Customer-facing alerts
├── dashboards.json        — Combined dashboard data per customer
├── dashboard_cust_001.json — Ananya's demo dashboard
└── transactions.json      — Processed transactions
```

## Demo Personas

| Customer | Scenario | Key Characteristic |
|---|---|---|
| cust_001 (Ananya Verma) | Stable income, rising expenses | Financial health 76/100 |
| cust_002 (Ramesh Patil) | EMI stressed, overdue loans | **Loan suppressed** |
| cust_003 (Meena Devi) | Growing saver | Goal-based savings opportunity |
| cust_004 (Arjun Kumar) | Unusual spending spike | Anomaly alert triggered |
| cust_005 (Sunita Rao) | Cash flow constrained | **Loan suppressed** |
| cust_006 (Priya Sharma) | Stable planner | Insurance recommendation |
| cust_007 (Mohan Das) | Irregular/seasonal income | Budget smoothing guidance |
| cust_008 (Kavitha Nair) | Growing saver, edu loan | Education loan opportunity |
| cust_009 (Rahul Gupta) | New to digital | Savings onboarding |
| cust_010 (Deepa Pillai) | Stable, retirement planning | Long-term investment |

## Data Contract (API Integration)

The backend should serve the dashboard fixture shape:

```json
{
  "customer": { "id": "cust_001", "name": "Ananya Verma", ... },
  "financial_health": { "score": 76, "label": "Stable", "components": {...}, ... },
  "cash_flow": { "monthly_income": 58000, "savings_rate": 28.8, ... },
  "recommendation": { "type": "savings", "title": "...", "loan_suppressed": false, ... },
  "stress": { "level": "low", "evidence": [...], ... },
  "alerts": [...],
  "recent_transactions": [...],
  "goals": [...],
  "monthly_trends": [...],
  "assistant_context": { "summary": "..." }
}
```

All fixtures follow this schema. See `data/processed/dashboard_cust_001.json` for the primary demo.

## Responsible AI Design

- **No protected attributes**: Caste, religion, gender, language, and location are NOT used as risk factors
- **Explainability**: Every score has component breakdown and plain-language explanation
- **Loan suppression**: Loan recommendations are automatically suppressed when stress score ≥ 2
- **Synthetic data only**: No real personal data is used
- **Human review flagged**: High-stress customers are flagged for human review
- **Disclaimer on all recommendations**: Financial guidance, not bank approval

## Module Reference

| Module | Purpose |
|---|---|
| `src/generate_data.py` | Synthetic data generation |
| `src/preprocess.py` | Validation, categorization, aggregation |
| `src/features.py` | Feature engineering |
| `src/health_score.py` | Financial health scoring |
| `src/segmentation.py` | Behavioral segmentation |
| `src/anomaly.py` | Anomaly detection |
| `src/stress.py` | Financial stress detection |
| `src/recommendations.py` | Recommendation engine |
| `src/alerts.py` | Alert generation |
| `src/export_fixtures.py` | Full pipeline + fixture export |
| `notebooks/evaluate.py` | Evaluation and testing |
