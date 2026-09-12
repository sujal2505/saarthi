"""Goals endpoints — list and create."""

import uuid
import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.goal import Goal as GoalModel
from app.schemas.goal import GoalResponse, GoalCreate

router = APIRouter(prefix="/api/v1/customers", tags=["Goals"])


def _goal_to_response(g: GoalModel) -> GoalResponse:
    """Convert ORM goal to response schema."""
    return GoalResponse(
        id=g.id,
        type=g.type,
        name=g.name,
        target_amount=g.target_amount,
        current_amount=g.current_amount,
        target_date=g.target_date.isoformat() if isinstance(g.target_date, datetime.date) else g.target_date,
        monthly_contribution=g.monthly_contribution,
        progress_pct=g.progress_pct,
        months_remaining=g.months_remaining,
        on_track=g.on_track,
    )


@router.get("/{customer_id}/goals", response_model=List[GoalResponse])
async def get_goals(customer_id: str, db: Session = Depends(get_db)):
    """Get all financial goals for a customer."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    goals = db.query(GoalModel).filter(GoalModel.customer_id == customer_id).all()
    return [_goal_to_response(g) for g in goals]


@router.post("/{customer_id}/goals", response_model=GoalResponse, status_code=201)
async def create_goal(customer_id: str, goal: GoalCreate, db: Session = Depends(get_db)):
    """
    Create a new financial goal.

    The system automatically computes progress percentage,
    months remaining, and on-track status.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    new_goal = GoalModel(
        id=f"g{uuid.uuid4().hex[:8]}",
        customer_id=customer_id,
        type=goal.type,
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=datetime.date.fromisoformat(goal.target_date),
        monthly_contribution=goal.monthly_contribution,
    )
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return _goal_to_response(new_goal)
