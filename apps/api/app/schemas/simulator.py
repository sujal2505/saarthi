"""Simulator schemas — matches frontend SimulatorInput / SimulatorOutput types."""

from pydantic import BaseModel, Field
from typing import Optional


class EMISimulatorInput(BaseModel):
    """EMI calculator input."""
    loan_amount: float = Field(..., gt=0, description="Loan principal in INR")
    interest_rate: float = Field(..., ge=0, le=50, description="Annual interest rate (%)")
    tenure_months: int = Field(..., gt=0, le=360, description="Loan tenure in months")
    monthly_income: Optional[float] = Field(None, description="Monthly income for ratio calculation")
    existing_emi: Optional[float] = Field(None, description="Existing EMI burden")
    monthly_expenses: Optional[float] = Field(None, description="Current monthly expenses")


class EMISimulatorOutput(BaseModel):
    """EMI calculator result — matches frontend SimulatorOutput."""
    monthly_emi: float
    total_repayment: float
    total_interest: float
    emi_to_income_ratio: float
    new_savings_rate: float
    health_impact: float  # delta to health score
    is_affordable: bool
    warning: Optional[str] = None


class GoalSimulatorInput(BaseModel):
    """Savings goal projection input."""
    target_amount: float = Field(..., gt=0)
    current_savings: float = Field(default=0, ge=0)
    monthly_contribution: float = Field(..., gt=0)
    expected_return_rate: float = Field(default=6.0, ge=0, le=30, description="Annual return rate (%)")


class GoalSimulatorOutput(BaseModel):
    """Savings goal projection result."""
    months_to_goal: int
    total_contributions: float
    total_interest_earned: float
    final_amount: float
    monthly_contribution_needed: Optional[float] = None
    is_achievable: bool
    suggestion: Optional[str] = None
