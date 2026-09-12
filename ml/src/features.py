"""
Feature Engineering Module — Saarthi Finance
Generates interpretable financial features from monthly aggregated data.
All features are computed without using protected attributes (caste, religion, gender, etc.)
"""

import math
import statistics
from typing import Dict, List, Optional


def safe_mean(values: List[float]) -> float:
    return statistics.mean(values) if values else 0.0


def safe_stdev(values: List[float]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def compute_features(
    customer: Dict,
    monthly_data: List[Dict],
    loans: List[Dict],
) -> Dict:
    """
    Compute interpretable financial features for a customer.

    Args:
        customer: Customer profile dict
        monthly_data: List of monthly aggregates [{month, income, expenses, emi, savings, ...}]
        loans: List of loan records for this customer

    Returns:
        Dict of features with explanations
    """
    if not monthly_data:
        return _empty_features(customer["customer_id"])

    # Sort by month
    monthly = sorted(monthly_data, key=lambda x: x["month"])
    n = len(monthly)

    incomes = [m["income"] for m in monthly]
    expenses = [m["expenses"] for m in monthly]
    emis = [m["emi"] for m in monthly]
    savings = [m["savings"] for m in monthly]
    net_flows = [m["net_cash_flow"] for m in monthly]

    mean_income = safe_mean(incomes)
    mean_expenses = safe_mean(expenses)
    mean_emi = safe_mean(emis)
    mean_savings = safe_mean(savings)
    mean_net = safe_mean(net_flows)

    # ── Income stability ─────────────────────────────────────
    income_cv = safe_stdev(incomes) / mean_income if mean_income > 0 else 1.0
    income_stability = max(0.0, 1.0 - income_cv)  # 0–1

    # ── Savings rate ─────────────────────────────────────────
    declared_income = customer.get("monthly_income", mean_income) or mean_income
    # Savings = explicit savings + positive net cash flow
    effective_savings = [
        m["savings"] + max(0, m["net_cash_flow"] - m["savings"])
        for m in monthly
    ]
    mean_effective_savings = safe_mean(effective_savings)
    savings_rate = mean_effective_savings / declared_income if declared_income > 0 else 0.0

    # ── Expense-to-income ratio ───────────────────────────────
    expense_ratio = (mean_expenses + mean_emi) / mean_income if mean_income > 0 else 1.0
    expense_ratio = min(expense_ratio, 1.5)  # cap at 150%

    # ── EMI-to-income ratio ───────────────────────────────────
    # Use declared income for consistency
    emi_from_loans = sum(l.get("emi_amount", 0) for l in loans)
    emi_ratio = emi_from_loans / declared_income if declared_income > 0 else 0.0

    # ── Debt-to-income ────────────────────────────────────────
    total_outstanding = sum(l.get("outstanding_amount", 0) for l in loans)
    annual_income = declared_income * 12
    dti_ratio = total_outstanding / annual_income if annual_income > 0 else 0.0

    # ── Expense volatility ────────────────────────────────────
    expense_cv = safe_stdev(expenses) / mean_expenses if mean_expenses > 0 else 0.0

    # ── Balance / cash-flow trend ─────────────────────────────
    # Positive trend = improving, negative = declining
    if n >= 3:
        recent_net = safe_mean(net_flows[-2:])
        earlier_net = safe_mean(net_flows[:2])
        cashflow_trend = (recent_net - earlier_net) / max(abs(earlier_net), 1)
    else:
        cashflow_trend = 0.0

    # ── Savings trend ─────────────────────────────────────────
    if n >= 3:
        recent_sav = safe_mean(savings[-2:])
        earlier_sav = safe_mean(savings[:2])
        savings_trend = (recent_sav - earlier_sav) / max(earlier_sav, 1)
    else:
        savings_trend = 0.0

    # ── Emergency fund estimate (months of expenses covered) ──
    # Proxy: savings balance = cumulative savings over period
    cumulative_savings = sum(savings)
    monthly_need = mean_expenses + mean_emi
    emergency_months = cumulative_savings / monthly_need if monthly_need > 0 else 0.0
    emergency_months = min(emergency_months, 12)  # cap at 12 months

    # ── Repayment reliability ─────────────────────────────────
    overdue_loans = [l for l in loans if l.get("repayment_status", "").startswith("overdue")]
    repayment_reliability = 1.0 - (len(overdue_loans) / max(len(loans), 1))

    # ── Cash-flow consistency ─────────────────────────────────
    negative_months = sum(1 for nf in net_flows if nf < 0)
    cashflow_consistency = 1.0 - (negative_months / n)

    # ── Recent behaviour change ───────────────────────────────
    # Flags if expenses increased meaningfully in last 2 months
    if n >= 4:
        recent_exp = safe_mean(expenses[-2:])
        earlier_exp = safe_mean(expenses[:-2])
        expense_surge = (recent_exp - earlier_exp) / max(earlier_exp, 1)
    else:
        expense_surge = 0.0

    return {
        "customer_id": customer["customer_id"],
        # Raw averages
        "avg_monthly_income": round(mean_income, 2),
        "avg_monthly_expenses": round(mean_expenses, 2),
        "avg_monthly_emi": round(mean_emi, 2),
        "avg_monthly_savings": round(mean_savings, 2),
        "avg_net_cash_flow": round(mean_net, 2),
        "declared_monthly_income": declared_income,
        # Ratios (0–1 scale)
        "income_stability": round(income_stability, 4),
        "savings_rate": round(max(0.0, savings_rate), 4),
        "expense_ratio": round(expense_ratio, 4),
        "emi_ratio": round(emi_ratio, 4),
        "dti_ratio": round(dti_ratio, 4),
        "expense_volatility": round(expense_cv, 4),
        "repayment_reliability": round(repayment_reliability, 4),
        "cashflow_consistency": round(cashflow_consistency, 4),
        # Trends (negative = worsening)
        "cashflow_trend": round(cashflow_trend, 4),
        "savings_trend": round(savings_trend, 4),
        "expense_surge": round(expense_surge, 4),
        # Liquidity
        "emergency_fund_months": round(emergency_months, 2),
        # Loan context
        "total_outstanding_debt": round(total_outstanding, 2),
        "emi_amount_total": round(emi_from_loans, 2),
        "overdue_loan_count": len(overdue_loans),
        "total_loan_count": len(loans),
        # Data quality
        "months_of_data": n,
    }


def _empty_features(customer_id: str) -> Dict:
    return {
        "customer_id": customer_id,
        "avg_monthly_income": 0, "avg_monthly_expenses": 0,
        "avg_monthly_emi": 0, "avg_monthly_savings": 0,
        "avg_net_cash_flow": 0, "declared_monthly_income": 0,
        "income_stability": 0, "savings_rate": 0, "expense_ratio": 0,
        "emi_ratio": 0, "dti_ratio": 0, "expense_volatility": 0,
        "repayment_reliability": 1.0, "cashflow_consistency": 0,
        "cashflow_trend": 0, "savings_trend": 0, "expense_surge": 0,
        "emergency_fund_months": 0, "total_outstanding_debt": 0,
        "emi_amount_total": 0, "overdue_loan_count": 0, "total_loan_count": 0,
        "months_of_data": 0,
    }


def compute_all_features(
    customers: List[Dict],
    monthly_aggregates: Dict[str, List[Dict]],
    loans: List[Dict],
) -> List[Dict]:
    """Compute features for all customers."""
    loan_by_customer: Dict[str, List[Dict]] = {}
    for loan in loans:
        cid = loan["customer_id"]
        loan_by_customer.setdefault(cid, []).append(loan)

    features = []
    for customer in customers:
        cid = customer["customer_id"]
        monthly = monthly_aggregates.get(cid, [])
        cust_loans = loan_by_customer.get(cid, [])
        feat = compute_features(customer, monthly, cust_loans)
        features.append(feat)

    return features


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_all_data

    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")
    data = load_all_data(seed_dir)

    features = compute_all_features(
        data["customers"],
        data["monthly_aggregates"],
        data["loans"],
    )

    for f in features:
        cid = f["customer_id"]
        print(f"\n{cid}: income_stability={f['income_stability']}, "
              f"savings_rate={f['savings_rate']:.1%}, "
              f"emi_ratio={f['emi_ratio']:.1%}, "
              f"emergency_months={f['emergency_fund_months']:.1f}")
