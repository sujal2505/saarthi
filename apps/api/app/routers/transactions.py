"""Transaction list endpoint."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse

router = APIRouter(prefix="/api/v1/customers", tags=["Transactions"])


@router.get("/{customer_id}/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    customer_id: str,
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=200, description="Max results"),
    db: Session = Depends(get_db),
):
    """
    List transactions for a customer.

    Supports filtering by date range and category.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    query = db.query(Transaction).filter(Transaction.customer_id == customer_id)

    if category:
        query = query.filter(Transaction.category == category)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    txns = query.order_by(Transaction.date.desc()).limit(limit).all()

    return [
        TransactionResponse(
            id=t.id,
            date=t.date.isoformat(),
            merchant=t.merchant,
            category=t.category,
            amount=t.amount,
            type=t.type,
            channel=t.channel,
            recurring=t.recurring,
            description=t.description,
        )
        for t in txns
    ]
