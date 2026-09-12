"""
Saarthi Finance — Data Ingestion Service.

Handles:
- CSV file parsing and validation
- Transaction categorization
- Storage of processed data
- Customer summary generation
"""

from __future__ import annotations

import csv
import io
import uuid
import datetime
from typing import List, Dict, Tuple

from sqlalchemy.orm import Session

from app.models.transaction import Transaction as TransactionModel


VALID_CATEGORIES = {
    "Salary", "Groceries", "Rent", "Utilities", "Transport",
    "Healthcare", "Education", "Shopping", "Entertainment",
    "EMI", "Savings", "UPI Transfer", "Other",
}

# Keyword-based auto-categorization rules
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Salary": ["salary", "credit", "payroll", "wage"],
    "Groceries": ["grocery", "fresh", "mart", "d-mart", "bigbasket", "reliance fresh"],
    "Rent": ["rent", "apartment", "housing"],
    "Utilities": ["electricity", "water", "gas", "broadband", "bsnl", "jio", "airtel"],
    "Transport": ["uber", "ola", "rapido", "petrol", "fuel", "metro", "bus"],
    "Healthcare": ["pharmacy", "hospital", "clinic", "doctor", "medical", "apollo"],
    "Education": ["school", "college", "tuition", "byju", "course", "education"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio", "shopping", "bazaar"],
    "Entertainment": ["netflix", "hotstar", "spotify", "zomato", "swiggy", "movie"],
    "EMI": ["emi", "loan", "repayment"],
    "Savings": ["savings", "rd", "fd", "deposit", "investment", "mutual fund"],
    "UPI Transfer": ["upi transfer", "transfer", "sent to"],
}


def auto_categorize(merchant: str, description: str = "") -> str:
    """Categorize a transaction based on merchant name and description."""
    text = f"{merchant} {description}".lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "Other"


def validate_and_parse_csv(content: str) -> Tuple[List[Dict], List[str]]:
    """
    Parse and validate a CSV file.

    Expected columns: date, merchant, category (optional), amount, type, channel, description
    Returns (valid_rows, errors).
    """
    reader = csv.DictReader(io.StringIO(content))
    rows: List[Dict] = []
    errors: List[str] = []

    required_fields = {"date", "merchant", "amount", "type"}
    if reader.fieldnames:
        missing = required_fields - set(f.strip().lower() for f in reader.fieldnames)
        if missing:
            errors.append(f"Missing required columns: {', '.join(missing)}")
            return rows, errors

    for i, row in enumerate(reader, start=2):  # start=2 because row 1 is header
        # Normalize keys
        row = {k.strip().lower(): v.strip() for k, v in row.items()}

        try:
            # Validate date
            date_str = row.get("date", "")
            try:
                parsed_date = datetime.date.fromisoformat(date_str)
            except ValueError:
                errors.append(f"Row {i}: Invalid date '{date_str}'")
                continue

            # Validate amount
            amount_str = row.get("amount", "0")
            try:
                amount = float(amount_str)
                if amount < 0:
                    errors.append(f"Row {i}: Amount cannot be negative ({amount})")
                    continue
            except ValueError:
                errors.append(f"Row {i}: Invalid amount '{amount_str}'")
                continue

            # Validate type
            txn_type = row.get("type", "").lower()
            if txn_type not in ("credit", "debit"):
                errors.append(f"Row {i}: Invalid type '{txn_type}' (must be credit/debit)")
                continue

            # Category — auto-detect if missing or invalid
            merchant = row.get("merchant", "Unknown")
            category = row.get("category", "")
            if category not in VALID_CATEGORIES:
                category = auto_categorize(merchant, row.get("description", ""))

            rows.append({
                "date": parsed_date,
                "merchant": merchant,
                "category": category,
                "amount": amount,
                "type": txn_type,
                "channel": row.get("channel", ""),
                "description": row.get("description", ""),
                "recurring": row.get("recurring", "").lower() in ("true", "1", "yes"),
            })

        except Exception as e:
            errors.append(f"Row {i}: Unexpected error — {str(e)}")

    return rows, errors


def ingest_transactions(
    db: Session,
    customer_id: str,
    content: str,
) -> Dict:
    """
    Ingest a CSV file of transactions for a customer.

    Returns a summary of the ingestion.
    """
    rows, errors = validate_and_parse_csv(content)

    inserted = 0
    for row in rows:
        txn = TransactionModel(
            id=f"txn_{uuid.uuid4().hex[:12]}",
            customer_id=customer_id,
            date=row["date"],
            merchant=row["merchant"],
            category=row["category"],
            amount=row["amount"],
            type=row["type"],
            channel=row["channel"],
            description=row["description"],
            recurring=row["recurring"],
        )
        db.add(txn)
        inserted += 1

    db.commit()

    return {
        "customer_id": customer_id,
        "total_rows_parsed": len(rows) + len(errors),
        "inserted": inserted,
        "errors": errors,
        "error_count": len(errors),
    }
