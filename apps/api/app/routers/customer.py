"""Customer profile endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerResponse

router = APIRouter(prefix="/api/v1/customers", tags=["Customer"])


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str, db: Session = Depends(get_db)):
    """
    Get customer profile.

    Returns demographic information, preferred language, and basic financial context.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}/features")
async def get_customer_features(customer_id: str):
    """
    Get 24 engineered ML features for a customer from Laptop 3 ML layer.
    
    Includes income stability, expense volatility, EMI ratio, savings trend,
    repayment reliability, and emergency fund buffer metrics.
    """
    import json
    from pathlib import Path

    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "processed" / "customer_features.json",
        Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "customer_features.json",
        Path("data/processed/customer_features.json"),
        Path("../../data/processed/customer_features.json"),
    ]
    for p in candidates:
        if p.is_file():
            try:
                with open(p, encoding="utf-8") as f:
                    features_list = json.load(f)
                    for item in features_list:
                        if item.get("customer_id") == customer_id:
                            return {"customer_id": customer_id, "features": item}
            except Exception:
                pass
    raise HTTPException(status_code=404, detail=f"Features for customer {customer_id} not found")

