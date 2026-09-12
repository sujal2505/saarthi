"""Dashboard schemas — matches frontend DashboardData type."""

from pydantic import BaseModel
from typing import List

from app.schemas.customer import CustomerResponse
from app.schemas.financial_health import FinancialHealthResponse
from app.schemas.cash_flow import CashFlowResponse
from app.schemas.recommendation import RecommendationResponse
from app.schemas.alert import AlertResponse
from app.schemas.transaction import (
    TransactionResponse,
    MonthlyTrendResponse,
    SpendingCategoryResponse,
)
from app.schemas.goal import GoalResponse


class AssistantContext(BaseModel):
    """Brief assistant context summary."""
    summary: str


class DashboardResponse(BaseModel):
    """Full dashboard payload — matches frontend DashboardData exactly."""
    customer: CustomerResponse
    financial_health: FinancialHealthResponse
    cash_flow: CashFlowResponse
    recommendation: RecommendationResponse
    alerts: List[AlertResponse]
    recent_transactions: List[TransactionResponse]
    goals: List[GoalResponse]
    assistant_context: AssistantContext
    monthly_trend: List[MonthlyTrendResponse]
    spending_categories: List[SpendingCategoryResponse]
