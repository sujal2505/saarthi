"""Cash-flow schemas — matches frontend CashFlow type."""

from pydantic import BaseModel


class CashFlowResponse(BaseModel):
    """Monthly cash-flow summary."""
    monthly_income: float
    monthly_expenses: float
    monthly_emi: float
    monthly_savings: float
    savings_rate: float
