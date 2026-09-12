"""Goal schemas — matches frontend Goal type."""

from pydantic import BaseModel
from typing import Optional, Literal


class GoalResponse(BaseModel):
    """Financial goal with progress tracking."""
    id: str
    type: str
    name: str
    target_amount: float
    current_amount: float
    target_date: str
    monthly_contribution: float
    progress_pct: float
    months_remaining: int
    on_track: bool


class GoalCreate(BaseModel):
    """Create a new financial goal."""
    type: str
    name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: str
    monthly_contribution: float
