"""Assistant / Chat schemas — matches frontend ChatRequest / ChatResponse."""

from pydantic import BaseModel, Field
from typing import Literal


class ChatRequest(BaseModel):
    """Chat message from user to assistant."""
    customer_id: str
    message: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en")


class ChatResponse(BaseModel):
    """Assistant reply."""
    reply: str
    language: str = "en"
    disclaimer: str = "This is AI-generated financial guidance, not professional advice. Please consult a certified advisor."