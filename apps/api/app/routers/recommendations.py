"""Recommendations endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.schemas.recommendation import RecommendationResponse
from app.services.financial_health import CustomerFinancials, calculate_financial_health
from app.services.recommendations import generate_recommendations
from app.schemas.cash_flow import CashFlowResponse

router = APIRouter(prefix="/api/v1/customers", tags=["Recommendations"])


@router.get("/{customer_id}/recommendations", response_model=RecommendationResponse)
async def get_recommendations(customer_id: str, db: Session = Depends(get_db)):
    """
    Get personalized financial recommendation for a customer.

    Implements responsible lending rules:
    - Suppresses loan offers when financial stress is high
    - Enforces EMI burden thresholds
    - Includes affordability explanation for all borrowing suggestions

    This is decision support only — not a loan approval or rejection.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    # Compute financial health
    monthly_savings = customer.monthly_income - customer.existing_emi
    # Estimate expenses from transactions or use income - emi - savings
    expenses_estimate = max(0, customer.monthly_income - customer.existing_emi - max(0, customer.monthly_income * 0.2))

    cf = CustomerFinancials(
        monthly_income=customer.monthly_income,
        monthly_expenses=expenses_estimate,
        monthly_emi=customer.existing_emi,
        monthly_savings=customer.monthly_income - expenses_estimate - customer.existing_emi,
        income_stability=customer.income_stability,
        emergency_fund=customer.emergency_fund,
    )
    health = calculate_financial_health(cf)

    cash_flow = CashFlowResponse(
        monthly_income=customer.monthly_income,
        monthly_expenses=expenses_estimate,
        monthly_emi=customer.existing_emi,
        monthly_savings=cf.monthly_savings,
        savings_rate=round(cf.monthly_savings / customer.monthly_income * 100, 1) if customer.monthly_income > 0 else 0,
    )

    return generate_recommendations(health, cash_flow)
