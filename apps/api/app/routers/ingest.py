"""Data ingestion endpoint."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.services.ingest import ingest_transactions

router = APIRouter(prefix="/api/v1/transactions", tags=["Data Ingestion"])


@router.post("/ingest")
async def ingest_csv(
    customer_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Ingest a CSV file of transactions for a customer.

    Expected CSV columns: date, merchant, category, amount, type, channel, description, recurring

    - date: YYYY-MM-DD format
    - amount: positive number
    - type: credit or debit
    - category: optional (auto-detected if missing)

    Returns a summary of inserted records and any validation errors.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")

    content = await file.read()
    try:
        content_str = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded CSV")

    result = ingest_transactions(db, customer_id, content_str)
    return result
