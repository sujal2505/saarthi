"""Recommendation schemas — matches frontend Recommendation type."""

from pydantic import BaseModel
from typing import List, Optional, Literal


class RecommendationResponse(BaseModel):
    """Product recommendation with responsible-lending safeguards."""
    type: str
    title: str
    product: str
    recommended_amount: Optional[float] = 0.0
    estimated_emi: Optional[float] = None
    confidence: float
    why: List[str]
    warning: str
    human_review_required: bool = False
    requires_human_review: Optional[bool] = False
    suppressed: Optional[bool] = None
    loan_suppressed: Optional[bool] = None
    suppression_reason: Optional[str] = None
    category: Optional[str] = None
    not_recommended: Optional[List[str]] = None
    not_recommended_reason: Optional[str] = None
