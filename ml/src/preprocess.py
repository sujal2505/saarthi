"""
Data Preprocessing Module — Saarthi Finance
Handles schema validation, categorization, monthly aggregation, and recurring detection.
"""

import csv
import os
from collections import defaultdict
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import math


# ─────────────────────────────────────────────────────────────
# SCHEMA DEFINITIONS
# ─────────────────────────────────────────────────────────────
CUSTOMER_SCHEMA = {
    "customer_id": str,
    "name": str,
    "age": int,
    "city": str,
    "state": str,
    "customer_segment": str,
    "preferred_language": str,
    "occupation": str,
    "monthly_income": float,
    "dependents": int,
    "financial_goal": str,
    "consent_status": str,
}

TRANSACTION_SCHEMA = {
    "transaction_id": str,
    "customer_id": str,
    "date": str,
    "amount": float,
    "transaction_type": str,
    "merchant": str,
    "category": str,
    "channel": str,
    "recurring": bool,
    "description": str,
}

LOAN_SCHEMA = {
    "loan_id": str,
    "customer_id": str,
    "loan_type": str,
    "principal": float,
    "outstanding_amount": float,
    "emi_amount": float,
    "interest_rate": float,
    "tenure_months": int,
    "next_due_date": str,
    "repayment_status": str,
}

VALID_CATEGORIES = {
    "Salary", "Groceries", "Rent", "Utilities", "Transport",
    "Healthcare", "Education", "Shopping", "Entertainment",
    "EMI", "Savings", "UPI Transfer", "Other",
}

KEYWORD_CATEGORY_MAP = {
    "rent": "Rent", "landlord": "Rent",
    "grocery": "Groceries", "kirana": "Groceries", "dmart": "Groceries",
    "reliance fresh": "Groceries", "big bazaar": "Groceries", "market": "Groceries",
    "electricity": "Utilities", "mpez": "Utilities", "apepdcl": "Utilities",
    "tangedco": "Utilities", "kesco": "Utilities", "jvvnl": "Utilities",
    "kseb": "Utilities", "bsnl": "Utilities", "airtel": "Utilities",
    "jio": "Utilities", "torrent": "Utilities", "power": "Utilities",
    "ola": "Transport", "rapido": "Transport", "auto": "Transport",
    "bus": "Transport", "fuel": "Transport", "brts": "Transport",
    "hospital": "Healthcare", "medplus": "Healthcare", "pharmacy": "Healthcare",
    "apollo": "Healthcare", "phc": "Healthcare", "vaidya": "Healthcare",
    "school fee": "Education", "byjus": "Education", "byju": "Education",
    "tuition": "Education",
    "amazon": "Shopping", "flipkart": "Shopping", "myntra": "Shopping",
    "meesho": "Shopping", "ajio": "Shopping",
    "netflix": "Entertainment", "hotstar": "Entertainment", "spotify": "Entertainment",
    "pvr": "Entertainment", "gaming": "Entertainment", "youtube": "Entertainment",
    "emi": "EMI", "bajaj finance": "EMI", "loan emi": "EMI",
    "salary": "Salary", "neft": "Salary",
    "rd": "Savings", "ppf": "Savings", "nps": "Savings", "savings": "Savings",
    "post office": "Savings",
    "phonepe": "UPI Transfer", "google pay": "UPI Transfer",
    "paytm": "UPI Transfer", "upi": "UPI Transfer",
    "swiggy": "Groceries", "zomato": "Groceries",
}


def parse_bool(val) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes")


def cast_row(row: Dict, schema: Dict) -> Tuple[Optional[Dict], Optional[str]]:
    """Cast row values to schema types. Returns (cast_row, error_msg)."""
    result = {}
    for field, dtype in schema.items():
        raw = row.get(field, "")
        if raw is None or raw == "":
            result[field] = None
            continue
        try:
            if dtype == bool:
                result[field] = parse_bool(raw)
            else:
                result[field] = dtype(raw)
        except (ValueError, TypeError) as e:
            return None, f"Field '{field}': {e}"
    return result, None


def validate_and_load_csv(filepath: str, schema: Dict) -> Tuple[List[Dict], List[str]]:
    """Load and validate CSV. Returns (valid_rows, errors)."""
    valid_rows = []
    errors = []
    seen_ids = set()
    id_field = list(schema.keys())[0]

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row_id = row.get(id_field, f"row_{i}")
            # Duplicate check
            if row_id in seen_ids:
                errors.append(f"Row {i}: Duplicate {id_field} '{row_id}' skipped.")
                continue
            seen_ids.add(row_id)

            cast, err = cast_row(row, schema)
            if err:
                errors.append(f"Row {i} ({row_id}): {err}")
                continue
            valid_rows.append(cast)

    return valid_rows, errors


def infer_category(merchant: str, description: str, existing_category: str) -> str:
    """Infer or verify category from merchant/description text."""
    if existing_category in VALID_CATEGORIES:
        return existing_category

    text = f"{merchant} {description}".lower()
    for keyword, cat in KEYWORD_CATEGORY_MAP.items():
        if keyword in text:
            return cat

    return "Other"


def categorize_transactions(transactions: List[Dict]) -> List[Dict]:
    """Ensure all transactions have valid categories."""
    for t in transactions:
        t["category"] = infer_category(
            t.get("merchant", "") or "",
            t.get("description", "") or "",
            t.get("category", "") or "",
        )
    return transactions


def detect_recurring(transactions: List[Dict]) -> List[Dict]:
    """
    Mark transactions as recurring if they appear monthly with similar amounts.
    Uses merchant + category + approximate amount matching.
    """
    # Group by customer → merchant → month → amount
    customer_merchant_months: Dict[str, Dict[str, Dict[str, List[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    for t in transactions:
        if t.get("transaction_type") == "debit":
            month_key = t["date"][:7]  # YYYY-MM
            merchant = t.get("merchant", "Unknown")
            customer_merchant_months[t["customer_id"]][merchant][month_key].append(
                t["amount"]
            )

    recurring_keys = set()
    for cid, merchants in customer_merchant_months.items():
        for merchant, months in merchants.items():
            if len(months) >= 3:  # Appears in ≥3 months → likely recurring
                recurring_keys.add((cid, merchant))

    for t in transactions:
        key = (t["customer_id"], t.get("merchant", "Unknown"))
        if key in recurring_keys and not t.get("recurring"):
            t["recurring"] = True

    return transactions


def aggregate_monthly(transactions: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Aggregate transactions per customer per month.
    Returns {customer_id: [{month, income, expenses, savings, emi, savings_contrib, category_breakdown}]}
    """
    # {cid: {month: {income, expenses, emi, savings, categories}}}
    agg: Dict[str, Dict[str, Dict]] = defaultdict(lambda: defaultdict(lambda: {
        "income": 0.0,
        "expenses": 0.0,
        "emi": 0.0,
        "savings": 0.0,
        "categories": defaultdict(float),
    }))

    for t in transactions:
        cid = t["customer_id"]
        month = t["date"][:7]
        amt = t.get("amount") or 0.0
        cat = t.get("category", "Other")
        ttype = t.get("transaction_type", "debit")

        if ttype == "credit" and cat == "Salary":
            agg[cid][month]["income"] += amt
        elif ttype == "debit":
            if cat == "EMI":
                agg[cid][month]["emi"] += amt
            elif cat == "Savings":
                agg[cid][month]["savings"] += amt
            else:
                agg[cid][month]["expenses"] += amt
            agg[cid][month]["categories"][cat] += amt

    result: Dict[str, List[Dict]] = {}
    for cid, months in agg.items():
        monthly_list = []
        for month, data in sorted(months.items()):
            monthly_list.append({
                "month": month,
                "income": round(data["income"], 2),
                "expenses": round(data["expenses"], 2),
                "emi": round(data["emi"], 2),
                "savings": round(data["savings"], 2),
                "net_cash_flow": round(data["income"] - data["expenses"] - data["emi"], 2),
                "category_breakdown": dict(data["categories"]),
            })
        result[cid] = monthly_list

    return result


def load_all_data(seed_dir: str) -> Dict:
    """Load and validate all seed CSVs. Returns a data bundle."""
    print("Loading and validating seed data...")

    customers, c_err = validate_and_load_csv(os.path.join(seed_dir, "customers.csv"), CUSTOMER_SCHEMA)
    transactions, t_err = validate_and_load_csv(os.path.join(seed_dir, "transactions.csv"), TRANSACTION_SCHEMA)
    loans, l_err = validate_and_load_csv(os.path.join(seed_dir, "loans.csv"), LOAN_SCHEMA)

    # Goals schema is simpler
    goals = []
    try:
        goals, g_err = validate_and_load_csv(os.path.join(seed_dir, "goals.csv"), {
            "goal_id": str, "customer_id": str, "goal_type": str,
            "target_amount": float, "current_amount": float,
            "target_date": str, "monthly_contribution": float,
        })
    except Exception as e:
        print(f"  Goals load warning: {e}")

    all_errors = c_err + t_err + l_err
    if all_errors:
        print(f"  Validation warnings ({len(all_errors)}):")
        for err in all_errors[:10]:
            print(f"    {err}")

    transactions = categorize_transactions(transactions)
    transactions = detect_recurring(transactions)
    monthly = aggregate_monthly(transactions)

    print(f"  Customers: {len(customers)}, Transactions: {len(transactions)}, "
          f"Loans: {len(loans)}, Goals: {len(goals)}")

    return {
        "customers": customers,
        "transactions": transactions,
        "loans": loans,
        "goals": goals,
        "monthly_aggregates": monthly,
    }


if __name__ == "__main__":
    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")
    data = load_all_data(seed_dir)
    print("Preprocessing complete.")
