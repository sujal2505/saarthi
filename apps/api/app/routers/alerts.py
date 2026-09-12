"""Alerts endpoint."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.alert import Alert as AlertModel
from app.schemas.alert import AlertResponse

router = APIRouter(prefix="/api/v1/customers", tags=["Alerts"])


@router.get("/{customer_id}/alerts", response_model=List[AlertResponse])
async def get_alerts(customer_id: str, db: Session = Depends(get_db)):
    """
    Get active financial alerts for a customer.

    Alerts are pre-generated and stored during data processing.
    Each alert includes severity, evidence, and actionable advice.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    alerts = db.query(AlertModel).filter(AlertModel.customer_id == customer_id).all()
    return [AlertResponse.model_validate(a) for a in alerts]
