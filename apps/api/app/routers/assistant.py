"""Assistant / chat endpoint — grounded in customer's actual ML intelligence."""

import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.schemas.assistant import ChatRequest, ChatResponse
from app.schemas.cash_flow import CashFlowResponse
from app.schemas.financial_health import FinancialHealthResponse, HealthComponents
from app.services.assistant import generate_response

router = APIRouter(prefix="/api/v1/assistant", tags=["Assistant"])

_CACHED_DASHBOARDS = None


def _load_dashboards():
    global _CACHED_DASHBOARDS
    if _CACHED_DASHBOARDS is not None:
        return _CACHED_DASHBOARDS
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed" / "dashboards.json",
        Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "dashboards.json",
        Path("data/processed/dashboards.json"),
        Path("../../data/processed/dashboards.json"),
    ]
    for p in candidates:
        if p.is_file():
            try:
                with open(p, encoding="utf-8") as f:
                    _CACHED_DASHBOARDS = json.load(f)
                    return _CACHED_DASHBOARDS
            except Exception:
                pass
    _CACHED_DASHBOARDS = {}
    return _CACHED_DASHBOARDS


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Financial assistant chat endpoint.

    Accepts a customer ID, message, and language preference.
    Grounded in the customer's actual ML dashboard data (exact score, EMI burden, suppression status).
    """
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {request.customer_id} not found")

    dashboards = _load_dashboards()
    ml_data = dashboards.get(request.customer_id)
    risk_factors = []
    health_change = 0
    emergency_months = None
    spending_categories = {}

    if ml_data:
        fh = ml_data.get("financial_health", {})
        comps = fh.get("components", {})
        health = FinancialHealthResponse(
            score=float(fh.get("score", customer.financial_health_score or 70)),
            label=fh.get("label", "Stable"),
            change=float(fh.get("change", 0)),
            components=HealthComponents(
                income_stability=float(comps.get("income_stability", 70)),
                savings=float(comps.get("savings", 70)),
                expense_management=float(comps.get("expense_management", 70)),
                debt_burden=float(comps.get("debt_burden", 70)),
                repayment_behavior=float(comps.get("repayment_behavior", 80)),
                liquidity=float(comps.get("liquidity", 60)),
            ),
            positive_factors=fh.get("positive_factors", []),
            risk_factors=fh.get("risk_factors", []),
            explanation=fh.get("plain_explanation") or fh.get("explanation", ""),
        )
        risk_factors = fh.get("risk_factors", [])
        health_change = float(fh.get("change", 0))
        cf_raw = ml_data.get("cash_flow", {})
        m_inc = float(cf_raw.get("monthly_income", customer.monthly_income))
        m_exp = float(cf_raw.get("avg_monthly_expenses", cf_raw.get("monthly_expenses", customer.monthly_income * 0.55)))
        m_emi = float(cf_raw.get("avg_monthly_emi", customer.existing_emi))
        m_sav = float(cf_raw.get("avg_monthly_savings", max(0, m_inc - m_exp - m_emi)))
        s_rate = float(cf_raw.get("savings_rate", 0))

        cash_flow = CashFlowResponse(
            monthly_income=round(m_inc),
            monthly_expenses=round(m_exp),
            monthly_emi=round(m_emi),
            monthly_savings=round(m_sav),
            savings_rate=round(s_rate, 1),
        )
        rec = ml_data.get("recommendation", {})
        is_suppressed = bool(rec.get("loan_suppressed") or rec.get("suppressed"))
        suppression_reason = rec.get("not_recommended_reason") or rec.get("suppression_reason")
        stress = ml_data.get("stress", {})
        for evidence in stress.get("evidence", []):
            if "month" in evidence.lower() and "cover" in evidence.lower():
                try:
                    emergency_months = float(evidence.split("covers only")[1].split("months")[0].strip())
                except (IndexError, ValueError):
                    pass
        spending_categories = {
            key: float(value)
            for key, value in cf_raw.get("last_month", {}).get("category_breakdown", {}).items()
            if key not in {"Salary", "Savings"}
        }
    else:
        m_exp = max(0, customer.monthly_income * 0.55)
        m_sav = customer.monthly_income - m_exp - customer.existing_emi
        s_rate = (m_sav / customer.monthly_income * 100) if customer.monthly_income > 0 else 0
        cash_flow = CashFlowResponse(
            monthly_income=round(customer.monthly_income),
            monthly_expenses=round(m_exp),
            monthly_emi=round(customer.existing_emi),
            monthly_savings=round(m_sav),
            savings_rate=round(s_rate, 1),
        )
        health = FinancialHealthResponse(
            score=float(customer.financial_health_score or 70),
            label="Stable" if (customer.financial_health_score or 70) >= 65 else "At Risk",
            change=0,
            components=HealthComponents(
                income_stability=70, savings=70, expense_management=70,
                debt_burden=70, repayment_behavior=80, liquidity=60,
            ),
            positive_factors=[],
            risk_factors=[],
            explanation="",
        )
        is_suppressed = (customer.financial_health_score or 70) < 45 or (customer.existing_emi / customer.monthly_income) > 0.4
        suppression_reason = "High financial stress detected."

    return generate_response(
        request=request,
        health=health,
        cash_flow=cash_flow,
        customer_name=customer.name.split()[0],
        full_name=customer.name,
        is_suppressed=is_suppressed,
        suppression_reason=suppression_reason,
        risk_factors=risk_factors,
        health_change=health_change,
        emergency_months=emergency_months,
        spending_categories=spending_categories,
    )