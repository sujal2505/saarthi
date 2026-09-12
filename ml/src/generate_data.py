"""
Synthetic Data Generator for Saarthi Finance
Generates realistic Indian Tier 2/3/rural customer financial data.
All data is synthetic and does not represent real individuals.
"""

import csv
import random
import os
from datetime import date, timedelta
from typing import List, Dict

random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../../data/seed")

# ─────────────────────────────────────────────────────────────
# PERSONAS
# ─────────────────────────────────────────────────────────────
PERSONAS = [
    {
        "customer_id": "cust_001",
        "name": "Ananya Verma",
        "age": 28,
        "city": "Indore",
        "state": "Madhya Pradesh",
        "customer_segment": "Stable Planner",
        "preferred_language": "hi",
        "occupation": "School Teacher",
        "monthly_income": 58000,
        "dependents": 2,
        "financial_goal": "Emergency Fund",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_002",
        "name": "Ramesh Patil",
        "age": 35,
        "city": "Nashik",
        "state": "Maharashtra",
        "customer_segment": "EMI Stressed",
        "preferred_language": "mr",
        "occupation": "Auto Driver",
        "monthly_income": 32000,
        "dependents": 4,
        "financial_goal": "Debt Reduction",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_003",
        "name": "Meena Devi",
        "age": 31,
        "city": "Varanasi",
        "state": "Uttar Pradesh",
        "customer_segment": "Growing Saver",
        "preferred_language": "hi",
        "occupation": "Tailor",
        "monthly_income": 25000,
        "dependents": 1,
        "financial_goal": "Education Savings",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_004",
        "name": "Arjun Kumar",
        "age": 24,
        "city": "Patna",
        "state": "Bihar",
        "customer_segment": "High Discretionary Spender",
        "preferred_language": "hi",
        "occupation": "Delivery Executive",
        "monthly_income": 22000,
        "dependents": 0,
        "financial_goal": "First Investment",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_005",
        "name": "Sunita Rao",
        "age": 42,
        "city": "Vijayawada",
        "state": "Andhra Pradesh",
        "customer_segment": "Cash Flow Constrained",
        "preferred_language": "te",
        "occupation": "Street Vendor",
        "monthly_income": 18000,
        "dependents": 3,
        "financial_goal": "Home Repair",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_006",
        "name": "Priya Sharma",
        "age": 26,
        "city": "Jaipur",
        "state": "Rajasthan",
        "customer_segment": "Stable Planner",
        "preferred_language": "hi",
        "occupation": "Nurse",
        "monthly_income": 45000,
        "dependents": 1,
        "financial_goal": "Festival Savings",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_007",
        "name": "Mohan Das",
        "age": 50,
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "customer_segment": "Irregular Income",
        "preferred_language": "ta",
        "occupation": "Farmer",
        "monthly_income": 14000,
        "dependents": 5,
        "financial_goal": "Crop Insurance",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_008",
        "name": "Kavitha Nair",
        "age": 33,
        "city": "Thrissur",
        "state": "Kerala",
        "customer_segment": "Growing Saver",
        "preferred_language": "ml",
        "occupation": "Beautician",
        "monthly_income": 36000,
        "dependents": 2,
        "financial_goal": "Education Loan Repayment",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_009",
        "name": "Rahul Gupta",
        "age": 29,
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "customer_segment": "New to Digital",
        "preferred_language": "hi",
        "occupation": "Shopkeeper",
        "monthly_income": 28000,
        "dependents": 2,
        "financial_goal": "Business Expansion",
        "consent_status": "given",
    },
    {
        "customer_id": "cust_010",
        "name": "Deepa Pillai",
        "age": 38,
        "city": "Madurai",
        "state": "Tamil Nadu",
        "customer_segment": "Stable Planner",
        "preferred_language": "ta",
        "occupation": "Government Employee",
        "monthly_income": 62000,
        "dependents": 3,
        "financial_goal": "Retirement Planning",
        "consent_status": "given",
    },
]

# ─────────────────────────────────────────────────────────────
# CATEGORY PROFILES per persona
# ─────────────────────────────────────────────────────────────
# Each tuple: (category, monthly_amount_mean, monthly_amount_std, is_recurring, merchant_options)
CATEGORY_PROFILES: Dict[str, List] = {
    "cust_001": [  # Ananya — stable, moderate pressure
        ("Rent", 12000, 0, True, ["Landlord Transfer"]),
        ("Groceries", 5500, 400, True, ["DMart", "Big Bazaar", "Local Kirana"]),
        ("Utilities", 2200, 200, True, ["MPEZ", "Airtel", "BSNL"]),
        ("Transport", 1500, 300, False, ["Ola", "Auto Stand", "BRTS"]),
        ("Healthcare", 800, 600, False, ["MedPlus", "City Hospital"]),
        ("Education", 1500, 200, True, ["Byju's", "School Fee"]),
        ("Shopping", 2500, 1000, False, ["Myntra", "Amazon", "Ajio"]),
        ("Entertainment", 600, 300, False, ["Netflix", "PVR Cinema"]),
        ("EMI", 9500, 0, True, ["HDFC Bank EMI"]),
        ("Savings", 5000, 500, True, ["SBI RD"]),
        ("UPI Transfer", 1500, 500, False, ["PhonePe", "Google Pay"]),
    ],
    "cust_002": [  # Ramesh — irregular, EMI stressed
        ("Rent", 7000, 500, True, ["Landlord Transfer"]),
        ("Groceries", 6000, 1000, True, ["Local Kirana", "Reliance Fresh"]),
        ("Utilities", 1800, 400, True, ["Torrent Power", "BSNL"]),
        ("Transport", 2000, 800, False, ["Fuel Station", "Ola"]),
        ("Healthcare", 1500, 1200, False, ["District Hospital", "MedPlus"]),
        ("Education", 2000, 300, True, ["School Fee"]),
        ("Shopping", 1200, 800, False, ["Amazon", "Meesho"]),
        ("Entertainment", 400, 300, False, ["Hotstar"]),
        ("EMI", 13500, 0, True, ["Bajaj Finance EMI", "SBI EMI"]),
        ("UPI Transfer", 2000, 800, False, ["PhonePe", "Paytm"]),
    ],
    "cust_003": [  # Meena — growing saver
        ("Rent", 5000, 0, True, ["Landlord Transfer"]),
        ("Groceries", 3500, 300, True, ["Local Market", "Reliance Fresh"]),
        ("Utilities", 1200, 150, True, ["UP Power", "Jio"]),
        ("Transport", 800, 200, False, ["E-Rickshaw", "Bus Pass"]),
        ("Healthcare", 400, 300, False, ["Jan Aushadhi"]),
        ("Education", 800, 100, True, ["School Fee"]),
        ("Shopping", 1000, 500, False, ["Meesho", "Local Shop"]),
        ("Entertainment", 200, 150, False, ["YouTube Premium"]),
        ("Savings", 4000, 400, True, ["Post Office RD"]),
        ("UPI Transfer", 800, 400, False, ["PhonePe"]),
    ],
    "cust_004": [  # Arjun — high discretionary, unusual spending
        ("Rent", 6000, 0, True, ["Landlord Transfer"]),
        ("Groceries", 3000, 500, True, ["Swiggy", "Zomato", "Grocery Store"]),
        ("Utilities", 1000, 200, True, ["BSEB", "Jio"]),
        ("Transport", 1500, 600, False, ["Ola", "Rapido", "Fuel"]),
        ("Shopping", 5000, 2000, False, ["Amazon", "Flipkart", "Myntra", "Ajio"]),
        ("Entertainment", 2000, 1000, False, ["Netflix", "Spotify", "Gaming"]),
        ("UPI Transfer", 2000, 1000, False, ["PhonePe", "Google Pay"]),
        ("Healthcare", 300, 200, False, ["MedPlus"]),
    ],
    "cust_005": [  # Sunita — cash flow constrained
        ("Rent", 4000, 200, True, ["Landlord Transfer"]),
        ("Groceries", 5000, 800, True, ["Local Market", "Kirana"]),
        ("Utilities", 1500, 300, True, ["APEPDCL", "BSNL"]),
        ("Transport", 800, 300, False, ["Auto", "Bus"]),
        ("Healthcare", 1200, 1000, False, ["PHC", "District Hospital"]),
        ("Education", 1500, 200, True, ["School Fee"]),
        ("EMI", 4500, 0, True, ["MFI EMI"]),
        ("UPI Transfer", 1000, 600, False, ["PhonePe"]),
    ],
    "cust_006": [  # Priya — stable, goal saver
        ("Rent", 10000, 0, True, ["Landlord Transfer"]),
        ("Groceries", 4500, 300, True, ["DMart", "Local Market"]),
        ("Utilities", 1800, 200, True, ["JVVNL", "Airtel"]),
        ("Transport", 1200, 300, False, ["Ola", "Bus"]),
        ("Healthcare", 600, 400, False, ["Apollo Pharmacy"]),
        ("Shopping", 2000, 800, False, ["Myntra", "Amazon"]),
        ("Entertainment", 800, 300, False, ["Netflix", "PVR"]),
        ("Savings", 8000, 500, True, ["HDFC RD", "PPF"]),
        ("UPI Transfer", 1500, 500, False, ["PhonePe"]),
    ],
    "cust_007": [  # Mohan — irregular income, seasonal
        ("Groceries", 4000, 1500, True, ["Local Market", "Kirana"]),
        ("Utilities", 800, 300, True, ["TANGEDCO", "BSNL"]),
        ("Transport", 600, 300, False, ["Auto", "Bus"]),
        ("Healthcare", 1000, 1500, False, ["PHC", "Vaidya"]),
        ("Education", 1200, 200, True, ["School Fee"]),
        ("EMI", 3500, 0, True, ["Kisan Credit Card"]),
        ("UPI Transfer", 500, 400, False, ["PhonePe"]),
    ],
    "cust_008": [  # Kavitha — growing saver, edu loan
        ("Rent", 8000, 0, True, ["Landlord Transfer"]),
        ("Groceries", 4000, 400, True, ["Reliance Fresh", "Local Market"]),
        ("Utilities", 1600, 200, True, ["KSEB", "Airtel"]),
        ("Transport", 1000, 200, False, ["Bus", "Auto"]),
        ("Healthcare", 500, 300, False, ["Apollo Pharmacy"]),
        ("Shopping", 2000, 600, False, ["Amazon", "Meesho"]),
        ("Entertainment", 600, 200, False, ["Hotstar", "Spotify"]),
        ("EMI", 7000, 0, True, ["SBI Education Loan EMI"]),
        ("Savings", 3000, 300, True, ["Kerala Post RD"]),
        ("UPI Transfer", 1200, 400, False, ["PhonePe"]),
    ],
    "cust_009": [  # Rahul — new to digital, shopkeeper
        ("Groceries", 5000, 600, True, ["Local Supplier", "Wholesale Market"]),
        ("Utilities", 1400, 300, True, ["KESCO", "Jio"]),
        ("Transport", 1000, 300, False, ["Auto", "Bus"]),
        ("Healthcare", 600, 500, False, ["Govt Hospital"]),
        ("Shopping", 1500, 700, False, ["Amazon", "Meesho"]),
        ("Entertainment", 400, 200, False, ["YouTube"]),
        ("UPI Transfer", 3000, 1000, False, ["PhonePe", "Google Pay"]),
        ("Savings", 2000, 300, True, ["Post Office RD"]),
    ],
    "cust_010": [  # Deepa — stable, retirement planning
        ("Rent", 0, 0, True, ["Own House"]),
        ("Groceries", 6000, 400, True, ["DMart", "Reliance Fresh"]),
        ("Utilities", 2500, 300, True, ["TANGEDCO", "BSNL", "Airtel"]),
        ("Transport", 1500, 200, False, ["Auto", "Cab"]),
        ("Healthcare", 1500, 800, False, ["Apollo Hospital", "MedPlus"]),
        ("Education", 2500, 200, True, ["School Fee"]),
        ("Shopping", 3000, 1000, False, ["Amazon", "Local Shop"]),
        ("Entertainment", 1000, 300, False, ["Netflix", "PVR"]),
        ("EMI", 8000, 0, True, ["LIC Loan EMI"]),
        ("Savings", 12000, 500, True, ["NPS", "PPF", "SBI RD"]),
        ("UPI Transfer", 2000, 500, False, ["PhonePe", "Google Pay"]),
    ],
}


def generate_transactions(
    persona: Dict, months: int = 6
) -> List[Dict]:
    """Generate realistic monthly transactions for a customer."""
    cid = persona["customer_id"]
    profile = CATEGORY_PROFILES.get(cid, [])
    income = persona["monthly_income"]
    transactions = []
    tid_counter = 1

    # Start date: 6 months ago from a fixed reference
    ref_date = date(2025, 12, 31)
    start_date = ref_date - timedelta(days=months * 30)

    for month_offset in range(months):
        month_start = start_date + timedelta(days=month_offset * 30)

        # Add slight income variability for irregular earners
        income_variability = 1.0
        if persona["customer_segment"] in ("Irregular Income", "Cash Flow Constrained"):
            income_variability = random.uniform(0.6, 1.2)
        elif persona["customer_segment"] == "EMI Stressed":
            income_variability = random.uniform(0.85, 1.0)

        actual_income = income * income_variability

        # Salary credit on 1st-5th of month
        salary_date = month_start + timedelta(days=random.randint(0, 4))
        transactions.append(
            {
                "transaction_id": f"txn_{cid}_{tid_counter:04d}",
                "customer_id": cid,
                "date": salary_date.isoformat(),
                "amount": round(actual_income, 2),
                "transaction_type": "credit",
                "merchant": persona["occupation"] + " Salary",
                "category": "Salary",
                "channel": "NEFT",
                "recurring": True,
                "description": f"Salary credit {salary_date.strftime('%b %Y')}",
            }
        )
        tid_counter += 1

        # Expense transactions
        for cat_profile in profile:
            cat, mean_amt, std_amt, is_recurring, merchants = cat_profile
            if mean_amt == 0:
                continue

            # Introduce stress pattern for Ananya in last 2 months (increasing expenses)
            stress_multiplier = 1.0
            if cid == "cust_001" and month_offset >= 4 and cat in ("Groceries", "Utilities", "Shopping"):
                stress_multiplier = 1.15 + (month_offset - 4) * 0.05

            # Declining savings for cust_002
            if cid == "cust_002" and cat == "Savings":
                continue  # No savings

            # Arjun unusual spending spike in month 5
            if cid == "cust_004" and month_offset == 5 and cat == "Shopping":
                stress_multiplier = 2.5

            n_transactions = random.randint(1, 3) if not is_recurring else 1
            for _ in range(n_transactions):
                amt = max(100, random.gauss(mean_amt / n_transactions, std_amt / n_transactions if std_amt > 0 else 1))
                amt = round(amt * stress_multiplier, 2)
                txn_date = month_start + timedelta(days=random.randint(1, 28))
                merchant = random.choice(merchants)

                transactions.append(
                    {
                        "transaction_id": f"txn_{cid}_{tid_counter:04d}",
                        "customer_id": cid,
                        "date": txn_date.isoformat(),
                        "amount": amt,
                        "transaction_type": "debit",
                        "merchant": merchant,
                        "category": cat,
                        "channel": random.choice(["UPI", "NEFT", "Debit Card", "Cash"]),
                        "recurring": is_recurring,
                        "description": f"{cat} payment - {merchant}",
                    }
                )
                tid_counter += 1

    return transactions


def generate_loans() -> List[Dict]:
    """Generate loan records for customers with active EMIs."""
    return [
        {
            "loan_id": "loan_001",
            "customer_id": "cust_001",
            "loan_type": "Personal Loan",
            "principal": 200000,
            "outstanding_amount": 145000,
            "emi_amount": 9500,
            "interest_rate": 12.5,
            "tenure_months": 24,
            "next_due_date": "2026-01-05",
            "repayment_status": "current",
        },
        {
            "loan_id": "loan_002",
            "customer_id": "cust_002",
            "loan_type": "Personal Loan",
            "principal": 120000,
            "outstanding_amount": 98000,
            "emi_amount": 7500,
            "interest_rate": 18.0,
            "tenure_months": 18,
            "next_due_date": "2026-01-07",
            "repayment_status": "overdue_30",
        },
        {
            "loan_id": "loan_003",
            "customer_id": "cust_002",
            "loan_type": "Two Wheeler Loan",
            "principal": 80000,
            "outstanding_amount": 55000,
            "emi_amount": 6000,
            "interest_rate": 16.0,
            "tenure_months": 18,
            "next_due_date": "2026-01-10",
            "repayment_status": "current",
        },
        {
            "loan_id": "loan_004",
            "customer_id": "cust_005",
            "loan_type": "Microfinance Loan",
            "principal": 50000,
            "outstanding_amount": 38000,
            "emi_amount": 4500,
            "interest_rate": 22.0,
            "tenure_months": 12,
            "next_due_date": "2026-01-15",
            "repayment_status": "current",
        },
        {
            "loan_id": "loan_005",
            "customer_id": "cust_007",
            "loan_type": "Kisan Credit Card",
            "principal": 60000,
            "outstanding_amount": 45000,
            "emi_amount": 3500,
            "interest_rate": 9.0,
            "tenure_months": 24,
            "next_due_date": "2026-01-20",
            "repayment_status": "current",
        },
        {
            "loan_id": "loan_006",
            "customer_id": "cust_008",
            "loan_type": "Education Loan",
            "principal": 300000,
            "outstanding_amount": 220000,
            "emi_amount": 7000,
            "interest_rate": 10.5,
            "tenure_months": 48,
            "next_due_date": "2026-01-05",
            "repayment_status": "current",
        },
        {
            "loan_id": "loan_007",
            "customer_id": "cust_010",
            "loan_type": "LIC Policy Loan",
            "principal": 150000,
            "outstanding_amount": 90000,
            "emi_amount": 8000,
            "interest_rate": 10.0,
            "tenure_months": 18,
            "next_due_date": "2026-01-01",
            "repayment_status": "current",
        },
    ]


def generate_goals() -> List[Dict]:
    """Generate financial goals for customers."""
    return [
        {
            "goal_id": "goal_001",
            "customer_id": "cust_001",
            "goal_type": "Emergency Fund",
            "target_amount": 100000,
            "current_amount": 32000,
            "target_date": "2026-12-31",
            "monthly_contribution": 5000,
        },
        {
            "goal_id": "goal_002",
            "customer_id": "cust_003",
            "goal_type": "Education Savings",
            "target_amount": 150000,
            "current_amount": 45000,
            "target_date": "2028-06-30",
            "monthly_contribution": 4000,
        },
        {
            "goal_id": "goal_003",
            "customer_id": "cust_006",
            "goal_type": "Festival Savings",
            "target_amount": 30000,
            "current_amount": 18000,
            "target_date": "2025-10-15",
            "monthly_contribution": 8000,
        },
        {
            "goal_id": "goal_004",
            "customer_id": "cust_010",
            "goal_type": "Retirement Fund",
            "target_amount": 2000000,
            "current_amount": 650000,
            "target_date": "2032-12-31",
            "monthly_contribution": 12000,
        },
        {
            "goal_id": "goal_005",
            "customer_id": "cust_005",
            "goal_type": "Home Repair",
            "target_amount": 80000,
            "current_amount": 5000,
            "target_date": "2027-03-31",
            "monthly_contribution": 2000,
        },
        {
            "goal_id": "goal_006",
            "customer_id": "cust_009",
            "goal_type": "Business Expansion",
            "target_amount": 100000,
            "current_amount": 12000,
            "target_date": "2027-06-30",
            "monthly_contribution": 2000,
        },
        {
            "goal_id": "goal_007",
            "customer_id": "cust_004",
            "goal_type": "First Investment",
            "target_amount": 50000,
            "current_amount": 3000,
            "target_date": "2027-01-01",
            "monthly_contribution": 1000,
        },
    ]


def write_csv(data: List[Dict], filepath: str) -> None:
    if not data:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"  Written: {filepath}  ({len(data)} rows)")


def main():
    print("Generating Saarthi Finance synthetic datasets...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Customers
    write_csv(PERSONAS, os.path.join(OUTPUT_DIR, "customers.csv"))

    # Transactions
    all_transactions = []
    for persona in PERSONAS:
        all_transactions.extend(generate_transactions(persona, months=6))
    write_csv(all_transactions, os.path.join(OUTPUT_DIR, "transactions.csv"))

    # Loans
    write_csv(generate_loans(), os.path.join(OUTPUT_DIR, "loans.csv"))

    # Goals
    write_csv(generate_goals(), os.path.join(OUTPUT_DIR, "goals.csv"))

    print(f"\nDone! Seed data written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
