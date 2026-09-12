"""
Unit tests for the EMI and Goal Simulator.
"""

from app.schemas.simulator import EMISimulatorInput, GoalSimulatorInput
from app.services.simulator import calculate_emi, project_goal


def test_standard_emi_calculation():
    """Verify reducing-balance EMI formula on standard input."""
    # Loan: 100,000 at 12% annual interest for 12 months
    # Standard formula yields ~8885 monthly EMI
    inp = EMISimulatorInput(
        loan_amount=100000.0,
        interest_rate=12.0,
        tenure_months=12,
        monthly_income=50000.0,
        existing_emi=0.0,
        monthly_expenses=20000.0,
    )
    result = calculate_emi(inp)

    assert 8800 <= result.monthly_emi <= 8950
    assert result.total_repayment > 100000
    assert result.total_interest > 0
    assert result.is_affordable is True
    assert result.warning is None


def test_unaffordable_loan_warning():
    """Verify affordability check flags high EMI relative to income."""
    inp = EMISimulatorInput(
        loan_amount=500000.0,
        interest_rate=14.0,
        tenure_months=12,
        monthly_income=30000.0,
        existing_emi=5000.0,
        monthly_expenses=20000.0,
    )
    result = calculate_emi(inp)

    assert result.is_affordable is False
    assert result.warning is not None
    assert result.health_impact < 0


def test_goal_projection_linear():
    """Verify target date estimation without interest."""
    inp = GoalSimulatorInput(
        target_amount=120000.0,
        current_savings=20000.0,
        monthly_contribution=10000.0,
        expected_return_rate=0.0,
    )
    result = project_goal(inp)

    # 100,000 needed at 10,000/month = 10 months
    assert result.months_to_goal == 10
    assert result.is_achievable is True
    assert result.total_contributions == 100000.0


def test_goal_already_achieved():
    inp = GoalSimulatorInput(
        target_amount=50000.0,
        current_savings=60000.0,
        monthly_contribution=2000.0,
        expected_return_rate=6.0,
    )
    result = project_goal(inp)
    assert result.months_to_goal == 0
    assert result.is_achievable is True
