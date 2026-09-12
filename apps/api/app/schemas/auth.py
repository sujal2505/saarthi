"""Authentication schemas."""

from pydantic import BaseModel, Field


class DemoLoginRequest(BaseModel):
    """Demo login request — phone number and language."""
    phone: str = Field(..., min_length=5, max_length=20, examples=["98XXXXX321"])
    language: str = Field(default="en", examples=["hi"])


class DemoLoginResponse(BaseModel):
    """Demo login response — JWT-compatible token and customer ID."""
    token: str
    customer_id: str
