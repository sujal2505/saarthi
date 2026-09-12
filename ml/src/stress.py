"""
Financial Stress Detection Module — Saarthi Finance
Detects early warning signals of financial difficulty using rules and explainable logic.
When stress is detected, loan offers are suppressed and safer alternatives are recommended.
"""

from typing import Dict, List, Tuple


# Stress level thresholds
STRESS_LEVELS = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

STRESS_LABELS = {0: "none", 1: "low", 2: "medium", 3: "high", 4: "critical"}


def _check_emi_burden(features: Dict) -> Tuple[int, str]:
    emi_ratio = features.get("emi_ratio", 0.0)
    overdue = features.get("overdue_loan_count", 0)

    if overdue > 0 and emi_ratio > 0.40:
        return 3, f"EMI burden is critical at {emi_ratio:.0%} of income with {overdue} overdue loan(s)."
    elif overdue > 0:
        return 2, f"There are {overdue} overdue loan repayment(s). Immediate attention required."
    elif emi_ratio > 0.45:
        return 3, f"EMI obligations at {emi_ratio:.0%} of income exceed safe limits."
    elif emi_ratio > 0.35:
        return 2, f"EMI burden of {emi_ratio:.0%} is above the recommended 30% threshold."
    elif emi_ratio > 0.25:
        return 1, f"EMI burden of {emi_ratio:.0%} is approaching the safe limit. Monitor new obligations."
    return 0, ""


def _check_savings_decline(features: Dict) -> Tuple[int, str]:
    savings_rate = features.get("savings_rate", 0.0)
    savings_trend = features.get("savings_trend", 0.0)

    if savings_rate < 0.02 and savings_trend < -0.10:
        return 3, "Savings have collapsed and continue declining. Financial buffer is critically low."
    elif savings_rate < 0.05 and savings_trend < 0:
        return 2, "Savings rate is very low and declining. Ability to absorb financial shocks is limited."
    elif savings_rate < 0.10 and savings_trend < -0.05:
        return 1, f"Savings rate dropped to {savings_rate:.0%}. Trend is downward."
    return 0, ""


def _check_cashflow(features: Dict) -> Tuple[int, str]:
    cashflow_consistency = features.get("cashflow_consistency", 1.0)
    cashflow_trend = features.get("cashflow_trend", 0.0)
    avg_net = features.get("avg_net_cash_flow", 0.0)

    if avg_net < 0:
        return 3, "Monthly cash flow is negative on average — expenses exceed income."
    elif cashflow_consistency < 0.40 and cashflow_trend < -0.20:
        return 2, "Cash flow is frequently negative and worsening. Urgent budget review needed."
    elif cashflow_consistency < 0.60:
        return 1, f"Cash flow is positive in only {cashflow_consistency:.0%} of months."
    return 0, ""


def _check_expense_surge(features: Dict) -> Tuple[int, str]:
    expense_surge = features.get("expense_surge", 0.0)
    expense_ratio = features.get("expense_ratio", 0.5)

    if expense_surge > 0.30 and expense_ratio > 0.85:
        return 2, f"Expenses surged by {expense_surge:.0%} and are now {expense_ratio:.0%} of income."
    elif expense_surge > 0.20:
        return 1, f"Expenses increased by {expense_surge:.0%} recently. Review discretionary spending."
    return 0, ""


def _check_emergency_fund(features: Dict) -> Tuple[int, str]:
    emergency_months = features.get("emergency_fund_months", 0.0)

    if emergency_months < 0.5:
        return 2, "Emergency fund is critically low — less than 2 weeks of expenses covered."
    elif emergency_months < 1.0:
        return 1, f"Emergency fund covers only {emergency_months:.1f} months — build this as a priority."
    return 0, ""


def detect_stress(features: Dict) -> Dict:
    """
    Detect financial stress for a customer and generate intervention recommendations.

    Returns:
        {
            stress_level: str (none/low/medium/high/critical)
            stress_score: int (0-4)
            evidence: [str]
            confidence: float (0-1)
            loan_recommendation_suppressed: bool
            customer_intervention: str
            requires_human_review: bool
        }
    """
    checks = [
        _check_emi_burden(features),
        _check_savings_decline(features),
        _check_cashflow(features),
        _check_expense_surge(features),
        _check_emergency_fund(features),
    ]

    evidence = [msg for score, msg in checks if msg]
    stress_score = max((score for score, _ in checks), default=0)

    # Accumulate: multiple medium signals → escalate
    medium_count = sum(1 for score, _ in checks if score >= 2)
    if medium_count >= 3:
        stress_score = max(stress_score, 3)
    elif medium_count >= 2 and stress_score < 3:
        stress_score = max(stress_score, 2)

    stress_level = STRESS_LABELS.get(stress_score, "none")

    # Confidence: higher with more data months
    months_confidence = min(features.get("months_of_data", 1) / 6, 1.0)
    signal_confidence = min(len(evidence) / 3, 1.0)
    confidence = round((months_confidence * 0.5 + signal_confidence * 0.5), 2)

    # Loan suppression: suppress if medium or above
    suppress_loan = stress_score >= 2

    # Intervention messaging
    if stress_score == 0:
        intervention = "Your finances appear stable. Continue current savings and repayment habits."
    elif stress_score == 1:
        intervention = (
            "There are early signs of financial pressure. Review your recurring expenses "
            "and avoid new loan obligations for now."
        )
    elif stress_score == 2:
        intervention = (
            "Your finances need attention. Consider reducing discretionary spending and "
            "focus on building an emergency buffer before taking on new debt."
        )
    elif stress_score == 3:
        intervention = (
            "Your financial situation is under significant pressure. We recommend speaking "
            "with a financial counsellor before making any major financial decisions. "
            "Saarthi can help you create a recovery plan."
        )
    else:
        intervention = (
            "This is a critical financial situation. Please reach out to your bank for "
            "support options such as EMI restructuring or payment holidays. "
            "Do not take on any new loans at this time."
        )

    return {
        "customer_id": features.get("customer_id", ""),
        "stress_level": stress_level,
        "stress_score": stress_score,
        "evidence": evidence,
        "confidence": confidence,
        "loan_recommendation_suppressed": suppress_loan,
        "customer_intervention": intervention,
        "requires_human_review": stress_score >= 3,
    }


def detect_all_stress(all_features: List[Dict]) -> List[Dict]:
    """Run stress detection for all customers."""
    return [detect_stress(f) for f in all_features]


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_all_data
    from features import compute_all_features

    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")
    data = load_all_data(seed_dir)
    all_features = compute_all_features(data["customers"], data["monthly_aggregates"], data["loans"])
    stress_results = detect_all_stress(all_features)

    print("Stress Detection Results:")
    for s in stress_results:
        suppressed = "🔴 LOAN SUPPRESSED" if s["loan_recommendation_suppressed"] else "✅ Loans OK"
        print(f"\n  {s['customer_id']}: [{s['stress_level'].upper()}] {suppressed}")
        for e in s["evidence"]:
            print(f"    ⚠ {e}")
