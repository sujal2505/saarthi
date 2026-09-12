"""Demo authentication endpoint."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.customer import Customer
from app.schemas.auth import DemoLoginRequest, DemoLoginResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/demo-login", response_model=DemoLoginResponse)
async def demo_login(request: DemoLoginRequest, db: Session = Depends(get_db)):
    """
    Demo login endpoint.

    Returns a JWT-compatible token for a demo customer.
    In production, this would validate credentials against a secure store.
    Passwords are never stored in plain text.
    """
    # Find customer by phone or ID (demo mode)
    customer = (
        db.query(Customer)
        .filter((Customer.phone == request.phone) | (Customer.id == request.phone))
        .first()
    )

    if not customer:
        # If phone contains 2 or patil, pick cust_002
        if "2" in request.phone:
            customer = db.query(Customer).filter(Customer.id == "cust_002").first()
        elif "3" in request.phone:
            customer = db.query(Customer).filter(Customer.id == "cust_003").first()
        else:
            customer = db.query(Customer).first()

    if not customer:
        raise HTTPException(status_code=404, detail="No demo customers found. Run seed script first.")


    # Update language preference
    if request.language:
        customer.preferred_language = request.language
        db.commit()

    # Generate JWT token
    payload = {
        "sub": customer.id,
        "name": customer.name,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return DemoLoginResponse(token=token, customer_id=customer.id)
