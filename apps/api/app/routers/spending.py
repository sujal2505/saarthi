"""Spending analysis endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import Customer
from app.schemas.transaction import SpendingCategoryResponse
from app.services.spending import get_spending_categories

router = APIRouter(prefix="/api/v1/customers", tags=["Spending"])


@router.get("/{customer_id}/spending", response_model=List[SpendingCategoryResponse])
async def get_spending(
    customer_id: str,
    months: int = Query(1, ge=1, le=12, description="Number of months to analyze"),
    db: Session = Depends(get_db),
):
    """
    Get category-wise spending breakdown with trends.

    Analyzes the specified number of months of transaction data.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    return get_spending_categories(db, customer_id, months)
