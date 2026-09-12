"""
Saarthi Finance — Simulator Service.

EMI calculation using standard reducing-balance formula.
Goal projection with compound interest.
Affordability analysis and health-impact estimation.
"""

from __future__ import annotations

import math
from typing import Optional

from app.schemas.simulator import (
    EMISimulatorInput,
    EMISimulatorOutput,
    GoalSimulatorInput,
    GoalSimulatorOutput,
)


def calculate_emi(input: EMISimulatorInput) -> EMISimulatorOutput:
    """
    Calculate EMI using the standard reducing-balance formula:
    EMI = P × r × (1+r)^n / ((1+r)^n - 1)

    Where:
        P = principal (loan_amount)
        r = monthly interest rate
        n = tenure in months
    """
    P = input.loan_amount
    annual_rate = input.interest_rate
    n = input.tenure_months

    # Monthly interest rate
    r = annual_rate / 100 / 12

    if r == 0:
        monthly_emi = P / n
    else:
        monthly_emi = (P * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)

    total_repayment = monthly_emi * n
    total_interest = total_repayment - P

    # Use provided values or defaults
    monthly_income = input.monthly_income or 58000  # default for demo
    existing_emi = input.existing_emi or 0
    monthly_expenses = input.monthly_expenses or 31800  # default for demo

    total_emi = existing_emi + monthly_emi
    emi_to_income_ratio = total_emi / monthly_income if monthly_income > 0 else 1.0

    new_savings = monthly_income - monthly_expenses - total_emi
    new_savings_rate = (new_savings / monthly_income * 100) if monthly_income > 0 else 0

    # Health impact estimation
    if emi_to_income_ratio > 0.5:
        health_impact = -18
    elif emi_to_income_ratio > 0.4:
        health_impact = -10
    elif emi_to_income_ratio > 0.3:
        health_impact = -5
    else:
        health_impact = -2

    is_affordable = emi_to_income_ratio < 0.45 and new_savings_rate > 10

    # Warning messages
    warning: Optional[str] = None
    if emi_to_income_ratio > 0.5:
        warning = (
            "Combined EMI would exceed 50% of income — "
            "this significantly strains your finances."
        )
    elif emi_to_income_ratio > 0.4:
        warning = (
            "Combined EMI burden is high. "
            "Consider a smaller loan amount or longer tenure."
        )
    elif new_savings_rate < 10:
        warning = (
            "This loan would reduce your savings rate below 10%. "
            "Try increasing the tenure."
        )

    return EMISimulatorOutput(
        monthly_emi=round(monthly_emi),
        total_repayment=round(total_repayment),
        total_interest=round(total_interest),
        emi_to_income_ratio=round(emi_to_income_ratio, 2),
        new_savings_rate=round(new_savings_rate, 1),
        health_impact=health_impact,
        is_affordable=is_affordable,
        warning=warning,
    )


def project_goal(input: GoalSimulatorInput) -> GoalSimulatorOutput:
    """
    Project savings goal timeline with optional compound interest.

    Uses monthly compounding formula:
    FV = PV × (1+r)^n + PMT × [((1+r)^n - 1) / r]
    """
    target = input.target_amount
    current = input.current_savings
    monthly = input.monthly_contribution
    annual_rate = input.expected_return_rate
    monthly_rate = annual_rate / 100 / 12

    remaining = target - current
    if remaining <= 0:
        return GoalSimulatorOutput(
            months_to_goal=0,
            total_contributions=0,
            total_interest_earned=0,
            final_amount=current,
            is_achievable=True,
            suggestion="Congratulations! You have already reached your goal.",
        )

    # Calculate months needed
    if monthly_rate > 0:
        # FV = PMT × [((1+r)^n - 1) / r]  (ignoring current savings initially)
        # We need: current × (1+r)^n + monthly × [((1+r)^n - 1) / r] >= target
        # Solve iteratively
        months = 0
        balance = current
        while balance < target and months < 600:  # cap at 50 years
            balance = balance * (1 + monthly_rate) + monthly
            months += 1
    else:
        months = math.ceil(remaining / monthly) if monthly > 0 else 999

    total_contributions = monthly * months
    # Compute actual final amount with interest
    if monthly_rate > 0 and months > 0:
        final_amount = current * math.pow(1 + monthly_rate, months) + \
            monthly * ((math.pow(1 + monthly_rate, months) - 1) / monthly_rate)
    else:
        final_amount = current + total_contributions

    total_interest = final_amount - current - total_contributions
    is_achievable = months <= 360  # achievable within 30 years

    # Calculate required monthly if not achievable in 5 years
    monthly_needed = None
    suggestion = None
    if months > 60:
        # What monthly contribution needed in 5 years?
        n_target = 60
        if monthly_rate > 0:
            fv_current = current * math.pow(1 + monthly_rate, n_target)
            remaining_for_pmt = target - fv_current
            if remaining_for_pmt > 0:
                monthly_needed = remaining_for_pmt * monthly_rate / (math.pow(1 + monthly_rate, n_target) - 1)
                monthly_needed = round(monthly_needed)
                suggestion = (
                    f"To reach your goal in 5 years, you would need to contribute "
                    f"₹{monthly_needed:,}/month instead of ₹{monthly:,.0f}/month."
                )
        else:
            monthly_needed = round(remaining / n_target)
            suggestion = f"To reach your goal in 5 years, contribute ₹{monthly_needed:,}/month."

    if suggestion is None and months <= 60:
        suggestion = f"You are on track to reach your goal in {months} months. Keep it up!"

    return GoalSimulatorOutput(
        months_to_goal=months,
        total_contributions=round(total_contributions),
        total_interest_earned=round(total_interest),
        final_amount=round(final_amount),
        monthly_contribution_needed=monthly_needed,
        is_achievable=is_achievable,
        suggestion=suggestion,
    )
