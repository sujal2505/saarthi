"""
Unit tests for Alert Generation Service.
"""

from app.schemas.financial_health import FinancialHealthResponse, HealthComponentsResponse
from app.schemas.cash_flow import CashFlowResponse
from app.schemas.transaction import SpendingCategoryResponse
from app.services.alerts import generate_alerts


def make_health():
    return FinancialHealthResponse(
        score=75,
        label="Stable",
        change=0,
        components=HealthComponentsResponse(
            income_stability=75,
            savings=75,
            expense_management=75,
            debt_burden=75,
            repayment_behavior=75,
            liquidity=75,
        ),
        positive_factors=["Stable income"],
        risk_factors=[],
        explanation="Testing",
    )


def test_unusual_spending_alert():
    """Verify alert generated when a spending category spikes > 15%."""
    cats = [
        SpendingCategoryResponse(
            category="Shopping",
            amount=3200,
            percentage=20.0,
            color="#d97706",
            trend="up",
            change_pct=24.0,
        ),
        SpendingCategoryResponse(
            category="Groceries",
            amount=4000,
            percentage=25.0,
            color="#0d7c6e",
            trend="stable",
        ),
    ]
    cash_flow = CashFlowResponse(
        monthly_income=50000,
        monthly_expenses=25000,
        monthly_emi=5000,
        monthly_savings=20000,
        savings_rate=40.0,
    )

    alerts = generate_alerts(
        health=make_health(),
        cash_flow=cash_flow,
        spending_categories=cats,
    )

    unusual = [a for a in alerts if a.type == "unusual_spending"]
    assert len(unusual) == 1
    assert "Shopping" in unusual[0].title
    assert "24%" in unusual[0].title


def test_negative_cash_flow_alert():
    """Verify high-severity alert when monthly savings < 0."""
    cash_flow = CashFlowResponse(
        monthly_income=20000,
        monthly_expenses=18000,
        monthly_emi=4000,
        monthly_savings=-2000,
        savings_rate=-10.0,
    )

    alerts = generate_alerts(
        health=make_health(),
        cash_flow=cash_flow,
        spending_categories=[],
    )

    cf_alerts = [a for a in alerts if a.type == "cash_flow"]
    assert len(cf_alerts) >= 1
    assert cf_alerts[0].severity in ("high", "critical")
    assert "Negative cash flow" in cf_alerts[0].title


def test_high_emi_risk_alert():
    """Verify alert triggered when EMI burden exceeds 45%."""
    cash_flow = CashFlowResponse(
        monthly_income=40000,
        monthly_expenses=18000,
        monthly_emi=20000,  # 50%
        monthly_savings=2000,
        savings_rate=5.0,
    )

    alerts = generate_alerts(
        health=make_health(),
        cash_flow=cash_flow,
        spending_categories=[],
    )

    emi_alerts = [a for a in alerts if a.type == "missed_emi_risk"]
    assert len(emi_alerts) == 1
    assert "EMI" in emi_alerts[0].title
