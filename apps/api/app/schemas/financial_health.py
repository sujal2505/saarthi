"""Financial health schemas — matches frontend FinancialHealth type."""

from pydantic import BaseModel
from typing import List, Literal


class HealthComponents(BaseModel):
    """Individual component scores (0–100)."""
    income_stability: float
    savings: float
    expense_management: float
    debt_burden: float
    repayment_behavior: float
    liquidity: float


class FinancialHealthResponse(BaseModel):
    """Full financial health assessment."""
    score: float
    label: str
    change: float  # +/- from last period
    components: HealthComponents
    positive_factors: List[str]
    risk_factors: List[str]
    explanation: str


HealthComponentsResponse = HealthComponents

