"""Alert schemas — matches frontend Alert type."""

from pydantic import BaseModel
from typing import Optional, Literal


class AlertResponse(BaseModel):
    """Financial alert."""
    id: str
    type: str
    severity: str
    title: str
    description: str
    evidence: Optional[str] = None
    action: str
    action_label: Optional[str] = None

    model_config = {"from_attributes": True}
