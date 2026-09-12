"""Transaction schemas — matches frontend Transaction, MonthlyTrend, SpendingCategory."""

from pydantic import BaseModel
from typing import Optional, Literal


VALID_CATEGORIES = [
    "Salary", "Groceries", "Rent", "Utilities", "Transport",
    "Healthcare", "Education", "Shopping", "Entertainment",
    "EMI", "Savings", "UPI Transfer", "Other",
]


class TransactionResponse(BaseModel):
    """Single transaction."""
    id: str
    date: str  # ISO date string
    merchant: str
    category: str
    amount: float
    type: Literal["credit", "debit"]
    channel: Optional[str] = None
    recurring: Optional[bool] = None
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class MonthlyTrendResponse(BaseModel):
    """Monthly income/expense/savings trend point."""
    month: str  # e.g. "Apr"
    income: float
    expenses: float
    savings: float


class SpendingCategoryResponse(BaseModel):
    """Spending breakdown by category."""
    category: str
    amount: float
    percentage: float
    color: str
    trend: Optional[Literal["up", "down", "stable"]] = None
    change_pct: Optional[float] = None
