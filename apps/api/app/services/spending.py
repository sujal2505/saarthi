"""
Saarthi Finance — Spending Analysis Service.

Provides:
- Category-wise spending breakdown
- Monthly trends
- Recurring expense detection
"""

from __future__ import annotations

from collections import defaultdict
from typing import List, Dict
import datetime

from sqlalchemy.orm import Session

from app.models.transaction import Transaction as TransactionModel
from app.schemas.transaction import (
    SpendingCategoryResponse,
    MonthlyTrendResponse,
)

# Color palette for categories
CATEGORY_COLORS: Dict[str, str] = {
    "Salary": "#2ecc71",
    "Groceries": "#0d7c6e",
    "Rent": "#1a2332",
    "Utilities": "#2d7a4f",
    "Transport": "#4a5568",
    "Healthcare": "#c0392b",
    "Education": "#2980b9",
    "Shopping": "#d97706",
    "Entertainment": "#9b59b6",
    "EMI": "#e8770a",
    "Savings": "#27ae60",
    "UPI Transfer": "#3498db",
    "Other": "#95a5a6",
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def get_spending_categories(
    db: Session, customer_id: str, months: int = 1
) -> List[SpendingCategoryResponse]:
    """
    Get category-wise spending breakdown for the most recent N months.
    """
    cutoff = datetime.date.today() - datetime.timedelta(days=months * 31)

    txns = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.customer_id == customer_id,
            TransactionModel.type == "debit",
            TransactionModel.date >= cutoff,
            TransactionModel.category != "Savings",  # savings is not spending
        )
        .all()
    )

    totals: Dict[str, float] = defaultdict(float)
    for txn in txns:
        totals[txn.category] += txn.amount

    grand_total = sum(totals.values()) or 1.0

    # Also compute previous period for trend
    prev_cutoff = cutoff - datetime.timedelta(days=months * 31)
    prev_txns = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.customer_id == customer_id,
            TransactionModel.type == "debit",
            TransactionModel.date >= prev_cutoff,
            TransactionModel.date < cutoff,
            TransactionModel.category != "Savings",
        )
        .all()
    )
    prev_totals: Dict[str, float] = defaultdict(float)
    for txn in prev_txns:
        prev_totals[txn.category] += txn.amount

    categories: List[SpendingCategoryResponse] = []
    for cat, amount in sorted(totals.items(), key=lambda x: -x[1]):
        pct = round(amount / grand_total * 100, 1)
        prev_amount = prev_totals.get(cat, 0)

        trend = "stable"
        change_pct = None
        if prev_amount > 0:
            change = ((amount - prev_amount) / prev_amount) * 100
            change_pct = round(change, 1)
            if change > 10:
                trend = "up"
            elif change < -10:
                trend = "down"

        categories.append(
            SpendingCategoryResponse(
                category=cat,
                amount=round(amount),
                percentage=pct,
                color=CATEGORY_COLORS.get(cat, "#95a5a6"),
                trend=trend,
                change_pct=change_pct,
            )
        )

    return categories


def get_monthly_trends(
    db: Session, customer_id: str, months: int = 6
) -> List[MonthlyTrendResponse]:
    """
    Get monthly income/expense/savings trends for the last N months.
    """
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=months * 31)

    txns = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.customer_id == customer_id,
            TransactionModel.date >= cutoff,
        )
        .all()
    )

    # Aggregate by month
    monthly: Dict[str, Dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
    for txn in txns:
        key = MONTH_NAMES[txn.date.month - 1]
        if txn.type == "credit":
            monthly[key]["income"] += txn.amount
        else:
            monthly[key]["expenses"] += txn.amount

    # Build ordered results
    results: List[MonthlyTrendResponse] = []
    for i in range(months):
        d = today - datetime.timedelta(days=(months - 1 - i) * 31)
        month_name = MONTH_NAMES[d.month - 1]
        data = monthly.get(month_name, {"income": 0, "expenses": 0})
        savings = data["income"] - data["expenses"]
        results.append(
            MonthlyTrendResponse(
                month=month_name,
                income=round(data["income"]),
                expenses=round(data["expenses"]),
                savings=round(savings),
            )
        )

    return results


def detect_recurring_expenses(
    db: Session, customer_id: str, months: int = 3
) -> List[Dict]:
    """
    Detect recurring expenses by finding merchants with regular payments.
    """
    cutoff = datetime.date.today() - datetime.timedelta(days=months * 31)

    txns = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.customer_id == customer_id,
            TransactionModel.type == "debit",
            TransactionModel.date >= cutoff,
        )
        .all()
    )

    merchant_payments: Dict[str, List[float]] = defaultdict(list)
    for txn in txns:
        merchant_payments[txn.merchant].append(txn.amount)

    recurring = []
    for merchant, amounts in merchant_payments.items():
        if len(amounts) >= 2:
            avg = sum(amounts) / len(amounts)
            variance = sum((a - avg) ** 2 for a in amounts) / len(amounts)
            cv = (variance ** 0.5) / avg if avg > 0 else 1

            if cv < 0.3:  # low coefficient of variation → likely recurring
                recurring.append({
                    "merchant": merchant,
                    "average_amount": round(avg),
                    "frequency": len(amounts),
                    "is_recurring": True,
                })

    return recurring
