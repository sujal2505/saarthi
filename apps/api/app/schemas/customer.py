"""Customer schemas — matches frontend Customer type."""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal


class CustomerResponse(BaseModel):
    """Customer profile response."""
    id: str
    name: str
    city: str
    state: str
    address: Optional[str] = None
    preferred_language: str = "en"
    phone: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    dependents: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerUpdate(BaseModel):
    """Editable customer profile fields."""
    name: str = Field(..., min_length=2, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    address: Optional[str] = Field(default=None, max_length=300)
    preferred_language: str = Field(default="en", min_length=2, max_length=5)
    phone: Optional[str] = Field(default=None, max_length=20)
    age: Optional[int] = Field(default=None, ge=13, le=120)
    occupation: Optional[str] = Field(default=None, max_length=200)
    dependents: Optional[int] = Field(default=None, ge=0, le=30)
