"""
Unit tests for the Financial Health Scoring Service.
"""

from app.services.financial_health import (
    CustomerFinancials,
    calculate_financial_health,
)


def test_healthy_financial_profile():
    """Test health calculation for a stable financial profile (Ananya)."""
    income = 58000.0
    expenses = 31800.0
    emi = 9500.0
    financials = CustomerFinancials(
        monthly_income=income,
        monthly_expenses=expenses,
        monthly_emi=emi,
        monthly_savings=income - expenses - emi,
        emergency_fund=60000.0,
        missed_emi_count=0,
        income_stability="stable",
    )

    result = calculate_financial_health(financials)

    assert 0 <= result.score <= 100
    assert result.score >= 70
    assert result.label in ("Stable", "Good", "Excellent")
    assert len(result.positive_factors) > 0
    assert result.explanation is not None
    assert result.components.repayment_behavior > 80


def test_stressed_financial_profile():
    """Test health calculation for financially stressed customer (Ramesh)."""
    income = 22000.0
    expenses = 18500.0
    emi = 4200.0
    financials = CustomerFinancials(
        monthly_income=income,
        monthly_expenses=expenses,
        monthly_emi=emi,
        monthly_savings=income - expenses - emi,
        emergency_fund=5000.0,
        missed_emi_count=1,
        income_stability="variable",
    )

    result = calculate_financial_health(financials)

    assert result.score < 55
    assert result.label in ("Poor", "Needs Attention", "Fair")
    assert len(result.risk_factors) > 0
    assert "savings" in result.explanation.lower() or "fair" in result.explanation.lower() or "health" in result.explanation.lower()


def test_zero_income_edge_case():
    """Test resilience against zero income."""
    income = 0.0
    expenses = 10000.0
    emi = 2000.0
    financials = CustomerFinancials(
        monthly_income=income,
        monthly_expenses=expenses,
        monthly_emi=emi,
        monthly_savings=income - expenses - emi,
        emergency_fund=0.0,
        missed_emi_count=2,
        income_stability="variable",
    )

    result = calculate_financial_health(financials)
    assert result.score < 40
    assert result.label in ("Poor", "Critical")
