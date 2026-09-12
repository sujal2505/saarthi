"""Saarthi Finance — Pydantic Schemas."""

from app.schemas.auth import DemoLoginRequest, DemoLoginResponse  # noqa: F401
from app.schemas.customer import CustomerResponse  # noqa: F401
from app.schemas.financial_health import HealthComponents, FinancialHealthResponse  # noqa: F401
from app.schemas.cash_flow import CashFlowResponse  # noqa: F401
from app.schemas.transaction import (  # noqa: F401
    TransactionResponse,
    MonthlyTrendResponse,
    SpendingCategoryResponse,
)
from app.schemas.recommendation import RecommendationResponse  # noqa: F401
from app.schemas.alert import AlertResponse  # noqa: F401
from app.schemas.goal import GoalResponse, GoalCreate  # noqa: F401
from app.schemas.simulator import (  # noqa: F401
    EMISimulatorInput,
    EMISimulatorOutput,
    GoalSimulatorInput,
    GoalSimulatorOutput,
)
from app.schemas.assistant import ChatRequest, ChatResponse  # noqa: F401
from app.schemas.dashboard import DashboardResponse  # noqa: F401
