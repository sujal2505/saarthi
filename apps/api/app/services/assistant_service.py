"""
apps/api/app/services/assistant.py

Drop this file into: apps/api/app/services/assistant.py
It replaces the old hardcoded-answer assistant with a Gemini-powered one.
"""

import os
import json
import httpx
from typing import Optional
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.goal import Goal


# Matches the LLM_API_KEY variable in your .env.example
GEMINI_API_KEY = os.getenv("LLM_API_KEY", "")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


# ─── Gather customer context from DB ────────────────────────────────────────

def _build_financial_context(customer_id: str, db: Session) -> dict:
    """
    Pull real data for this customer and shape it into a context dict
    that becomes part of the system prompt.
    """
    customer: Optional[Customer] = (
        db.query(Customer).filter(Customer.id == customer_id).first()
    )
    if not customer:
        return {}

    # Last 30 transactions
    recent_txns = (
        db.query(Transaction)
        .filter(Transaction.customer_id == customer_id)
        .order_by(Transaction.date.desc())
        .limit(30)
        .all()
    )

    # Spending by category
    spending_by_category: dict[str, float] = {}
    for t in recent_txns:
        if t.amount < 0:          # expenses are negative
            cat = t.category or "Other"
            spending_by_category[cat] = spending_by_category.get(cat, 0) + abs(t.amount)

    total_income = sum(t.amount for t in recent_txns if t.amount > 0)
    total_expense = sum(abs(t.amount) for t in recent_txns if t.amount < 0)

    # Goals
    goals = db.query(Goal).filter(Goal.customer_id == customer_id).all()
    goals_data = [
        {
            "name": g.name,
            "target_amount": g.target_amount,
            "current_amount": g.current_amount,
            "deadline": str(g.deadline) if g.deadline else None,
            "progress_pct": round(
                (g.current_amount / g.target_amount * 100) if g.target_amount else 0, 1
            ),
        }
        for g in goals
    ]

    return {
        "customer_name": customer.name,
        "monthly_income": getattr(customer, "monthly_income", None),
        "credit_score": getattr(customer, "credit_score", None),
        "account_balance": getattr(customer, "account_balance", None),
        "recent_spending_by_category": spending_by_category,
        "last_30_days_income": round(total_income, 2),
        "last_30_days_expenses": round(total_expense, 2),
        "savings_rate_pct": (
            round((total_income - total_expense) / total_income * 100, 1)
            if total_income > 0 else 0
        ),
        "goals": goals_data,
    }


# ─── Build the system prompt ─────────────────────────────────────────────────

def _system_prompt(context: dict) -> str:
    ctx_json = json.dumps(context, indent=2, default=str)
    return f"""You are Saarthi, a friendly and knowledgeable personal finance assistant
built into a banking app. Your job is to help customers understand their own
financial situation in plain, simple language — no jargon, no intimidating
numbers without explanation.

Here is the real, live financial data for the customer you are talking to right now:

{ctx_json}

Guidelines:
- Always refer to the customer by name when you first address them.
- Use the actual numbers from the data above when answering. Never make up numbers.
- Explain things the way a trusted friend who happens to be a financial advisor would.
- Keep answers concise (2-4 short paragraphs at most) unless the customer asks for detail.
- If the customer asks about spending, refer to their real category breakdown.
- If the customer asks about goals, tell them exactly how far along each goal is.
- If the customer asks about borrowing or loans, use their credit score and balance data.
- If you don't have enough data to answer a specific question, say so honestly and
  suggest what they could check in the app.
- Never give generic advice that ignores their actual numbers.
- Respond in the same language the customer writes in.
"""


# ─── Main function called by the router ─────────────────────────────────────

async def get_assistant_response(
    customer_id: str,
    user_message: str,
    conversation_history: list[dict],  # [{"role": "user"|"model", "parts": [{"text": "..."}]}]
    db: Session,
) -> str:
    """
    Send the customer's question + full financial context to Gemini
    and return the assistant's reply as a string.
    """
    context = _build_financial_context(customer_id, db)
    system_prompt = _system_prompt(context)

    # Build message list: history + new user message
    messages = list(conversation_history)
    messages.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": messages,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        },
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return "Sorry, I couldn't process that right now. Please try again."