"""Dashboard endpoint — assembles the full dashboard payload with ML intelligence."""

from typing import List, Optional
import datetime
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.transaction import Transaction as TransactionModel
from app.models.alert import Alert as AlertModel
from app.models.goal import Goal as GoalModel
from app.schemas.dashboard import DashboardResponse, AssistantContext
from app.schemas.customer import CustomerResponse
from app.schemas.transaction import (
    TransactionResponse,
    MonthlyTrendResponse,
    SpendingCategoryResponse,
)
from app.schemas.alert import AlertResponse
from app.schemas.goal import GoalResponse
from app.schemas.cash_flow import CashFlowResponse
from app.schemas.financial_health import FinancialHealthResponse, HealthComponents
from app.schemas.recommendation import RecommendationResponse
from app.services.financial_health import CustomerFinancials, calculate_financial_health
from app.services.spending import get_spending_categories, get_monthly_trends, CATEGORY_COLORS
from app.services.recommendations import generate_recommendations
from app.services.alerts import generate_alerts

router = APIRouter(prefix="/api/v1/customers", tags=["Dashboard"])

_CACHED_DASHBOARDS: Optional[dict] = None

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _format_month_label(m_str: str) -> str:
    try:
        parts = m_str.split("-")
        return MONTH_NAMES[int(parts[1]) - 1]
    except Exception:
        return m_str


def _load_ml_dashboards() -> dict:
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


@router.get("/{customer_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard(customer_id: str, db: Session = Depends(get_db)):
    """
    Get the full customer dashboard.

    Integrates ML models from Laptop 3 (health scoring, stress detection, loan suppression)
    with database records for transactions and goals.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    ml_dashboards = _load_ml_dashboards()
    ml_data = ml_dashboards.get(customer_id)

    # ---- Recent transactions from DB ----
    recent_txns = (
        db.query(TransactionModel)
        .filter(TransactionModel.customer_id == customer_id)
        .order_by(TransactionModel.date.desc())
        .limit(50)
        .all()
    )

    # ---- Cash flow ----
    if ml_data and "cash_flow" in ml_data:
        cf_raw = ml_data["cash_flow"]
        m_inc = float(cf_raw.get("monthly_income", customer.monthly_income))
        m_exp = float(cf_raw.get("avg_monthly_expenses", cf_raw.get("monthly_expenses", 0)))
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
    else:
        income_total = sum(t.amount for t in recent_txns if t.type == "credit")
        expense_total = sum(t.amount for t in recent_txns if t.type == "debit" and t.category != "Savings")
        monthly_income = income_total if income_total > 0 else customer.monthly_income
        monthly_expenses = expense_total if expense_total > 0 else max(0, customer.monthly_income * 0.55)
        monthly_emi = customer.existing_emi
        monthly_savings = monthly_income - monthly_expenses - monthly_emi
        savings_rate = round((monthly_savings / monthly_income) * 100, 1) if monthly_income > 0 else 0

        cash_flow = CashFlowResponse(
            monthly_income=round(monthly_income),
            monthly_expenses=round(monthly_expenses),
            monthly_emi=round(monthly_emi),
            monthly_savings=round(monthly_savings),
            savings_rate=savings_rate,
        )

    # ---- Financial Health ----
    if ml_data and "financial_health" in ml_data:
        fh = ml_data["financial_health"]
        comps = fh.get("components", {})
        health = FinancialHealthResponse(
            score=float(fh.get("score", 70)),
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
            explanation=fh.get("plain_explanation") or fh.get("explanation", "Financial health is evaluated based on income stability and obligations."),
        )
    else:
        cf = CustomerFinancials(
            monthly_income=cash_flow.monthly_income,
            monthly_expenses=cash_flow.monthly_expenses,
            monthly_emi=cash_flow.monthly_emi,
            monthly_savings=cash_flow.monthly_savings,
            income_stability=customer.income_stability,
            emergency_fund=customer.emergency_fund,
            prev_month_expenses=cash_flow.monthly_expenses * 0.95,
            prev_health_score=customer.financial_health_score or 0,
        )
        health = calculate_financial_health(cf)

    # ---- Recommendation ----
    if ml_data and "recommendation" in ml_data:
        rec_raw = ml_data["recommendation"]
        is_suppressed = bool(rec_raw.get("loan_suppressed") or rec_raw.get("suppressed"))
        recommendation = RecommendationResponse(
            type=rec_raw.get("type", "savings"),
            title=rec_raw.get("title", ""),
            product=rec_raw.get("product", ""),
            recommended_amount=float(rec_raw.get("recommended_amount") or 0),
            estimated_emi=float(rec_raw.get("estimated_emi")) if rec_raw.get("estimated_emi") else None,
            confidence=float(rec_raw.get("confidence", 0.88)),
            why=rec_raw.get("why", []),
            warning=rec_raw.get("warning", "Financial guidance only. Not a loan approval."),
            human_review_required=bool(rec_raw.get("requires_human_review") or is_suppressed),
            requires_human_review=bool(rec_raw.get("requires_human_review") or is_suppressed),
            suppressed=is_suppressed,
            loan_suppressed=is_suppressed,
            suppression_reason=rec_raw.get("not_recommended_reason") or rec_raw.get("suppression_reason"),
            category=rec_raw.get("category"),
            not_recommended=rec_raw.get("not_recommended"),
            not_recommended_reason=rec_raw.get("not_recommended_reason"),
        )
    else:
        recommendation = generate_recommendations(health, cash_flow)

    # ---- Spending categories ----
    spending_categories = []
    if ml_data and "monthly_trends" in ml_data and ml_data["monthly_trends"]:
        last_m = ml_data["monthly_trends"][-1]
        breakdown = last_m.get("category_breakdown", {})
        total_exp = sum(v for k, v in breakdown.items() if k not in ("Savings", "Income")) or 1
        spending_categories = [
            SpendingCategoryResponse(
                category=cat,
                amount=round(amt),
                percentage=round((amt / total_exp) * 100, 1),
                color=CATEGORY_COLORS.get(cat, "#4a5568"),
                trend="up" if cat in ("Shopping", "Groceries", "UPI Transfer") else "stable",
            )
            for cat, amt in sorted(breakdown.items(), key=lambda x: -x[1])
            if amt > 0 and cat not in ("Savings", "Income")
        ]
    if not spending_categories:
        spending_categories = get_spending_categories(db, customer_id, months=1)
    if not spending_categories:
        spending_categories = _default_spending_categories(cash_flow.monthly_expenses)

    # ---- Monthly trends ----
    monthly_trend = []
    raw_trends = (ml_data.get("monthly_trends") or ml_data.get("monthly_data")) if ml_data else None
    if raw_trends:
        monthly_trend = [
            MonthlyTrendResponse(
                month=_format_month_label(m.get("month", "")),
                income=round(float(m.get("income", 0))),
                expenses=round(float(m.get("expenses", 0))),
                savings=round(float(m.get("savings", 0))),
            )
            for m in raw_trends
        ]
    else:
        monthly_trend = get_monthly_trends(db, customer_id, months=6)
    if not monthly_trend or all(t.income == 0 for t in monthly_trend):
        monthly_trend = _default_monthly_trends(cash_flow.monthly_income, cash_flow.monthly_expenses)

    # ---- Alerts ----
    stored_alerts = db.query(AlertModel).filter(AlertModel.customer_id == customer_id).all()
    if stored_alerts:
        alerts = [AlertResponse.model_validate(a) for a in stored_alerts]
    elif ml_data and "alerts" in ml_data and ml_data["alerts"]:
        alerts = [
            AlertResponse(
                id=a["id"],
                type=a.get("type", "cash_flow"),
                severity=a.get("severity", "medium"),
                title=a.get("title", "Financial Alert"),
                description=a.get("description", ""),
                evidence=a.get("evidence", ""),
                action=a.get("recommended_action") or a.get("action", "Review Details"),
                action_label=a.get("secondary_action") or a.get("action_label", "Review"),
            )
            for a in ml_data["alerts"]
        ]
    else:
        alerts = generate_alerts(health, cash_flow, spending_categories, cash_flow.monthly_expenses * 0.95)

    # ---- Goals ----
    goals_db = db.query(GoalModel).filter(GoalModel.customer_id == customer_id).all()
    goals = [
        GoalResponse(
            id=g.id,
            type=g.type,
            name=g.name,
            target_amount=g.target_amount,
            current_amount=g.current_amount,
            target_date=g.target_date.isoformat() if isinstance(g.target_date, datetime.date) else str(g.target_date),
            monthly_contribution=g.monthly_contribution,
            progress_pct=g.progress_pct,
            months_remaining=g.months_remaining,
            on_track=g.on_track,
        )
        for g in goals_db
    ]

    # ---- Recent transactions ----
    recent = [
        TransactionResponse(
            id=t.id,
            date=t.date.isoformat() if isinstance(t.date, datetime.date) else str(t.date),
            merchant=t.merchant,
            category=t.category,
            amount=t.amount,
            type=t.type,
            channel=t.channel,
            recurring=t.recurring,
            description=t.description,
        )
        for t in recent_txns[:10]
    ]

    # ---- Assistant context ----
    if ml_data and "assistant_context" in ml_data:
        summary_text = ml_data["assistant_context"].get("summary", "")
    else:
        emi_ratio = round(cash_flow.monthly_emi / cash_flow.monthly_income * 100, 1) if cash_flow.monthly_income > 0 else 0
        summary_text = (
            f"{customer.name} has {'stable' if customer.income_stability == 'stable' else 'variable'} "
            f"income of ₹{cash_flow.monthly_income:,.0f}/month, "
            f"savings rate of {cash_flow.savings_rate}%, "
            f"and EMI burden of {emi_ratio}%."
        )

    return DashboardResponse(
        customer=CustomerResponse.model_validate(customer),
        financial_health=health,
        cash_flow=cash_flow,
        recommendation=recommendation,
        alerts=alerts,
        recent_transactions=recent,
        goals=goals,
        assistant_context=AssistantContext(summary=summary_text),
        monthly_trend=monthly_trend,
        spending_categories=spending_categories,
    )


def _default_spending_categories(monthly_expenses: float):
    defaults = [
        ("Rent", 0.35), ("EMI", 0.30), ("Groceries", 0.12),
        ("Shopping", 0.08), ("Transport", 0.05), ("Utilities", 0.06),
        ("Healthcare", 0.02), ("Entertainment", 0.02),
    ]
    return [
        SpendingCategoryResponse(
            category=cat, amount=round(monthly_expenses * pct),
            percentage=round(pct * 100, 1),
            color=CATEGORY_COLORS.get(cat, "#95a5a6"),
            trend="stable",
        )
        for cat, pct in defaults
    ]


def _default_monthly_trends(monthly_income: float, monthly_expenses: float):
    today = datetime.date.today()
    trends = []
    for i in range(6):
        d = today - datetime.timedelta(days=(5 - i) * 31)
        expense_variation = 1 + (i - 3) * 0.02
        exp = round(monthly_expenses * expense_variation)
        trends.append(
            MonthlyTrendResponse(
                month=MONTH_NAMES[d.month - 1],
                income=round(monthly_income),
                expenses=exp,
                savings=round(monthly_income - exp),
            )
        )
    return trends
