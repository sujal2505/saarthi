"""
Alerts Generator — Saarthi Finance
Generates customer-facing financial alerts from stress signals, anomalies, and feature data.
Each alert includes severity, evidence, recommended action, and human-friendly wording.
"""

import uuid
from typing import Dict, List


ALERT_TYPES = {
    "cash_flow": "Monthly Cash Flow Alert",
    "unusual_spending": "Unusual Spending Detected",
    "savings_decline": "Savings Rate Declining",
    "emi_risk": "EMI Payment Risk",
    "potential_fraud": "Unusual Transaction — Please Review",
    "income_drop": "Income Reduction Detected",
    "expense_surge": "Expense Increase Detected",
    "new_merchant": "New Merchant Activity",
}


def _make_alert(
    customer_id: str,
    alert_type: str,
    severity: str,
    title: str,
    description: str,
    evidence: str,
    action: str,
    action_secondary: str = "Talk to support",
) -> Dict:
    return {
        "id": f"alert_{uuid.uuid4().hex[:8]}",
        "customer_id": customer_id,
        "type": alert_type,
        "severity": severity,  # low / medium / high / critical
        "title": title,
        "description": description,
        "evidence": evidence,
        "recommended_action": action,
        "secondary_action": action_secondary,
    }


def generate_alerts(
    customer: Dict,
    features: Dict,
    stress_result: Dict,
    anomalies: List[Dict],
    monthly_data: List[Dict],
) -> List[Dict]:
    """Generate all relevant alerts for a customer."""
    alerts = []
    cid = customer["customer_id"]
    stress_score = stress_result.get("stress_score", 0)

    # ── Cash flow alert ──────────────────────────────────────
    avg_net = features.get("avg_net_cash_flow", 0.0)
    cashflow_consistency = features.get("cashflow_consistency", 1.0)
    if avg_net < 0:
        alerts.append(_make_alert(
            cid, "cash_flow", "critical",
            "Monthly Cash Flow Is Negative",
            "Your average monthly expenses and EMIs exceed your income. This requires urgent attention.",
            f"Average net cash flow: ₹{avg_net:,.0f}/month",
            "Review and reduce non-essential expenses immediately.",
        ))
    elif cashflow_consistency < 0.60:
        alerts.append(_make_alert(
            cid, "cash_flow", "high",
            "Inconsistent Monthly Cash Flow",
            f"Your monthly cash flow is positive in only {cashflow_consistency:.0%} of months.",
            f"Cash flow is negative or near-zero in several recent months.",
            "Review recurring expenses to create more consistent cash surplus.",
        ))
    elif features.get("expense_surge", 0) > 0.10:
        surge = features.get("expense_surge", 0)
        alerts.append(_make_alert(
            cid, "cash_flow", "medium",
            "Your Monthly Expenses Are Rising",
            f"Household spending increased by approximately {surge:.0%} recently.",
            f"Expense surge of {surge:.0%} observed in recent months.",
            "Review recurring expenses to identify what has increased.",
        ))

    # ── EMI risk alert ───────────────────────────────────────
    overdue = features.get("overdue_loan_count", 0)
    emi_ratio = features.get("emi_ratio", 0.0)
    if overdue > 0:
        alerts.append(_make_alert(
            cid, "emi_risk", "critical",
            "Overdue Loan Payment Detected",
            f"You have {overdue} loan(s) with overdue payments. This may impact your credit profile.",
            f"{overdue} overdue loan(s) on record.",
            "Contact your lender immediately to discuss payment options or restructuring.",
        ))
    elif emi_ratio > 0.40:
        alerts.append(_make_alert(
            cid, "emi_risk", "high",
            "High EMI Burden — Risk of Missed Payment",
            f"Your EMI obligations are {emi_ratio:.0%} of your income, which is above the safe threshold.",
            f"EMI-to-income ratio: {emi_ratio:.0%} (recommended max: 30%)",
            "Avoid taking additional loans. Consider speaking to an advisor about EMI restructuring.",
        ))

    # ── Savings decline alert ────────────────────────────────
    savings_rate = features.get("savings_rate", 0.0)
    savings_trend = features.get("savings_trend", 0.0)
    if savings_rate < 0.05 and savings_trend < -0.05:
        alerts.append(_make_alert(
            cid, "savings_decline", "high",
            "Savings Rate Has Dropped Significantly",
            "Your monthly savings have declined and are now very low.",
            f"Savings rate: {savings_rate:.0%}, trend: declining",
            "Set up an automatic recurring deposit to protect your savings habit.",
        ))
    elif savings_rate < 0.10 and savings_trend < 0:
        alerts.append(_make_alert(
            cid, "savings_decline", "medium",
            "Savings Rate Is Below Recommended Level",
            f"Your current savings rate of {savings_rate:.0%} is below the recommended 10–15%.",
            f"Savings rate: {savings_rate:.0%}",
            "Try to increase your monthly savings by ₹500–₹1,000 this month.",
        ))

    # ── Anomaly-based alerts ─────────────────────────────────
    high_anomalies = [a for a in anomalies if a.get("severity") in ("high", "medium")]
    for anomaly in high_anomalies[:3]:  # Max 3 anomaly alerts
        atype = anomaly.get("anomaly_type", "unusual_spending")
        if atype == "unusual_amount":
            alerts.append(_make_alert(
                cid, "unusual_spending", anomaly["severity"],
                f"Unusual {anomaly['category']} Spending",
                anomaly["explanation"],
                anomaly["evidence"],
                "Review this transaction and confirm it was made by you.",
                "Flag this transaction for review",
            ))
        elif atype == "category_surge":
            alerts.append(_make_alert(
                cid, "expense_surge", anomaly["severity"],
                f"{anomaly['category']} Spending Increased by {anomaly['change_pct']:.0f}%",
                anomaly["explanation"],
                anomaly["evidence"],
                f"Review your {anomaly['category']} expenses for this month.",
            ))
        elif atype == "new_merchant":
            alerts.append(_make_alert(
                cid, "new_merchant", "low",
                f"New Merchant: {anomaly['merchant']}",
                anomaly["explanation"],
                anomaly["evidence"],
                "Confirm this transaction is authorized.",
                "Flag as unauthorized",
            ))
        elif atype == "income_drop":
            alerts.append(_make_alert(
                cid, "income_drop", anomaly["severity"],
                "Income Was Lower Than Usual",
                anomaly["explanation"],
                anomaly["evidence"],
                "Check if your salary or income payment was delayed or reduced.",
            ))

    return alerts


def generate_all_alerts(
    customers: List[Dict],
    all_features: List[Dict],
    stress_results: List[Dict],
    anomaly_results: Dict[str, List[Dict]],
    monthly_aggregates: Dict[str, List[Dict]],
) -> Dict[str, List[Dict]]:
    """Generate alerts for all customers."""
    feature_map = {f["customer_id"]: f for f in all_features}
    stress_map = {s["customer_id"]: s for s in stress_results}

    all_alerts = {}
    for customer in customers:
        cid = customer["customer_id"]
        alerts = generate_alerts(
            customer=customer,
            features=feature_map.get(cid, {}),
            stress_result=stress_map.get(cid, {"stress_score": 0}),
            anomalies=anomaly_results.get(cid, []),
            monthly_data=monthly_aggregates.get(cid, []),
        )
        all_alerts[cid] = alerts

    return all_alerts
