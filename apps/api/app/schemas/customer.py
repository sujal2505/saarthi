"""Customer schemas — matches frontend Customer type."""

from pydantic import BaseModel
from typing import Optional, Literal


class CustomerResponse(BaseModel):
    """Customer profile response."""
    id: str
    name: str
    city: str
    state: str
    preferred_language: str = "en"
    phone: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    dependents: Optional[int] = None

    model_config = {"from_attributes": True}
