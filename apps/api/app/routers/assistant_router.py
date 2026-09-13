"""
apps/api/app/routers/assistant.py
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.services.assistant import get_assistant_response

router = APIRouter(prefix="/api/v1/assistant", tags=["assistant"])


class HistoryMessage(BaseModel):
    role: str   # "user" or "model"
    text: str


class ChatRequest(BaseModel):
    customer_id: str                          # sent from frontend
    message: str
    language: Optional[str] = "en"
    customer_name: Optional[str] = None
    history: Optional[list[HistoryMessage]] = []   # conversation so far


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
):
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    gemini_history = [
        {"role": msg.role, "parts": [{"text": msg.text}]}
        for msg in (body.history or [])
    ]

    reply = await get_assistant_response(
        customer_id=body.customer_id,
        user_message=body.message,
        conversation_history=gemini_history,
        customer_name=body.customer_name,
        language=body.language or "en",
        db=db,
    )

    return ChatResponse(reply=reply)