"""
Unit tests for the Responsible Recommendation Engine.

Verifies:
1. Loan suppression when financial health score < 45
2. Suppression when EMI-to-income > 40%
3. Savings prioritization when savings rate < 10%
4. Warning notices and non-binding guidance disclaimers
"""

from app.schemas.financial_health import FinancialHealthResponse, HealthComponentsResponse
from app.schemas.cash_flow import CashFlowResponse
from app.services.recommendations import generate_recommendations


def make_health(score: float) -> FinancialHealthResponse:
    return FinancialHealthResponse(
        score=score,
        label="Stable" if score >= 70 else "Poor",
        change=0,
        components=HealthComponentsResponse(
            income_stability=70,
            savings=70,
            expense_management=70,
            debt_burden=70,
            repayment_behavior=70,
            liquidity=70,
        ),
        positive_factors=["Stable income"],
        risk_factors=[],
        explanation="Test health status",
    )


def test_suppression_low_health_score():
    """Rule 1: If health score < 45, loans must be suppressed with counselling recommended."""
    health = make_health(score=40.0)
    cash_flow = CashFlowResponse(
        monthly_income=25000.0,
        monthly_expenses=20000.0,
        monthly_emi=4000.0,
        monthly_savings=1000.0,
        savings_rate=4.0,
    )

    rec = generate_recommendations(health, cash_flow)

    assert rec.suppressed is True
    assert rec.human_review_required is True
    assert rec.product == "Financial Counselling Support"
    assert rec.recommended_amount == 0
    assert rec.suppression_reason is not None


def test_suppression_high_emi_ratio():
    """Rule 2: If EMI-to-income ratio > 40%, suppress borrowing even if health score is moderate."""
    health = make_health(score=60.0)
    cash_flow = CashFlowResponse(
        monthly_income=50000.0,
        monthly_expenses=25000.0,
        monthly_emi=22000.0,  # 44% of income
        monthly_savings=3000.0,
        savings_rate=6.0,
    )

    rec = generate_recommendations(health, cash_flow)

    assert rec.suppressed is True
    assert rec.type in ("restructure", "savings")
    assert "EMI" in str(rec.why) or "debt" in str(rec.why).lower()


def test_healthy_customer_savings_focus():
    """Healthy customer should receive constructive savings or investment advice."""
    health = make_health(score=78.0)
    cash_flow = CashFlowResponse(
        monthly_income=58000.0,
        monthly_expenses=31800.0,
        monthly_emi=9500.0,
        monthly_savings=16700.0,
        savings_rate=28.8,
    )

    rec = generate_recommendations(health, cash_flow)

    assert rec.suppressed is False
    assert rec.type == "savings"
    assert rec.warning is not None  # Disclaimer always present
