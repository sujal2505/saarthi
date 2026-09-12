"""
Financial Health Score Module — Saarthi Finance
Computes explainable, weighted financial health scores (0–100).
No protected attributes are used. Every component is transparent and explainable.
"""

from typing import Dict, List, Tuple


# ─────────────────────────────────────────────────────────────
# COMPONENT WEIGHTS (sum to 1.0)
# ─────────────────────────────────────────────────────────────
WEIGHTS = {
    "income_stability": 0.20,
    "savings": 0.20,
    "expense_management": 0.15,
    "debt_burden": 0.20,
    "repayment_behavior": 0.15,
    "liquidity": 0.10,
}

# Friendly labels for each score band
SCORE_LABELS = [
    (85, "Excellent"),
    (70, "Stable"),
    (55, "Moderate"),
    (40, "Needs Attention"),
    (0, "At Risk"),
]


def band_label(score: float) -> str:
    for threshold, label in SCORE_LABELS:
        if score >= threshold:
            return label
    return "At Risk"


def _score_income_stability(features: Dict) -> Tuple[float, str]:
    """Score income stability 0–100."""
    stability = features.get("income_stability", 0.5)
    months = features.get("months_of_data", 1)

    # More months of stable data = higher confidence
    data_confidence = min(months / 6, 1.0)
    raw = stability * data_confidence

    score = raw * 100
    if score >= 80:
        explanation = "Income has been consistent over the past months."
    elif score >= 60:
        explanation = "Income is mostly stable with minor fluctuations."
    else:
        explanation = "Income shows significant variability month to month."

    return min(100.0, score), explanation


def _score_savings(features: Dict) -> Tuple[float, str]:
    """Score savings behavior 0–100."""
    savings_rate = features.get("savings_rate", 0.0)
    savings_trend = features.get("savings_trend", 0.0)

    # 20%+ savings rate = 100, 0% = 0, with trend bonus
    base = min(savings_rate / 0.25, 1.0) * 100
    trend_bonus = max(0, savings_trend * 10)
    score = min(100.0, base + trend_bonus)

    if savings_rate >= 0.25:
        explanation = f"Savings rate of {savings_rate:.0%} is strong, above the recommended 20%."
    elif savings_rate >= 0.10:
        explanation = f"Savings rate of {savings_rate:.0%} is moderate. There is room to save more."
    elif savings_rate > 0:
        explanation = f"Savings rate of {savings_rate:.0%} is low. Building an emergency buffer is important."
    else:
        explanation = "No savings activity detected in the past months."

    return score, explanation


def _score_expense_management(features: Dict) -> Tuple[float, str]:
    """Score expense discipline 0–100."""
    expense_ratio = features.get("expense_ratio", 0.8)
    expense_surge = features.get("expense_surge", 0.0)
    volatility = features.get("expense_volatility", 0.2)

    # Lower ratio = better; 50% = 100, 100%+ = 0
    base = max(0.0, (1.0 - expense_ratio) * 200)
    surge_penalty = max(0, expense_surge * 20)
    vol_penalty = min(20, volatility * 30)

    score = min(100.0, max(0.0, base - surge_penalty - vol_penalty))

    if expense_ratio <= 0.60:
        explanation = f"Expenses are well-controlled at {expense_ratio:.0%} of income."
    elif expense_ratio <= 0.80:
        explanation = f"Expenses are at {expense_ratio:.0%} of income. Manage discretionary spending."
    else:
        explanation = f"Expenses are high at {expense_ratio:.0%} of income. Reducing non-essentials is advised."

    if expense_surge > 0.10:
        explanation += f" Note: Expenses increased by {expense_surge:.0%} recently."

    return score, explanation


def _score_debt_burden(features: Dict) -> Tuple[float, str]:
    """Score debt burden 0–100. Lower EMI ratio = better score."""
    emi_ratio = features.get("emi_ratio", 0.0)
    dti_ratio = features.get("dti_ratio", 0.0)

    # Safe EMI threshold = 30% of income
    # >50% = very stressed
    emi_score = max(0.0, (1.0 - emi_ratio / 0.50)) * 100
    dti_penalty = min(20, dti_ratio * 10)

    score = min(100.0, max(0.0, emi_score - dti_penalty))

    if emi_ratio == 0:
        explanation = "No active EMI obligations. Strong financial flexibility."
    elif emi_ratio <= 0.20:
        explanation = f"EMI burden is low at {emi_ratio:.0%} of income. Well within safe limits."
    elif emi_ratio <= 0.35:
        explanation = f"EMI burden is moderate at {emi_ratio:.0%} of income. Monitor for new obligations."
    else:
        explanation = f"EMI burden is high at {emi_ratio:.0%} of income. Exceeds the recommended 30% threshold."

    return score, explanation


def _score_repayment(features: Dict) -> Tuple[float, str]:
    """Score repayment reliability 0–100."""
    reliability = features.get("repayment_reliability", 1.0)
    overdue = features.get("overdue_loan_count", 0)
    total = features.get("total_loan_count", 0)

    score = reliability * 100

    if overdue == 0 and total == 0:
        explanation = "No loan history. Score reflects no repayment risk."
    elif overdue == 0:
        explanation = "All EMI payments are current. Excellent repayment record."
    else:
        explanation = f"{overdue} of {total} loan(s) have overdue payments. This impacts your credit profile."

    return score, explanation


def _score_liquidity(features: Dict) -> Tuple[float, str]:
    """Score emergency buffer / liquidity 0–100."""
    emergency_months = features.get("emergency_fund_months", 0.0)
    cashflow_consistency = features.get("cashflow_consistency", 0.5)

    # 6 months emergency = 100; 0 = 0
    emergency_score = min(emergency_months / 6, 1.0) * 70
    consistency_score = cashflow_consistency * 30

    score = min(100.0, emergency_score + consistency_score)

    if emergency_months >= 6:
        explanation = f"Emergency fund covers approximately {emergency_months:.0f} months of expenses. Excellent."
    elif emergency_months >= 3:
        explanation = f"Emergency fund covers ~{emergency_months:.1f} months. Target 6 months for full security."
    elif emergency_months >= 1:
        explanation = f"Emergency fund covers ~{emergency_months:.1f} month(s). Building this further is advised."
    else:
        explanation = "Emergency fund appears very limited. Prioritize building a financial safety net."

    return score, explanation


def compute_health_score(features: Dict) -> Dict:
    """
    Compute overall financial health score and component breakdown.

    Returns:
        {
          score: int 0-100,
          label: str,
          change: int (placeholder, needs historical comparison),
          components: {component: score},
          component_explanations: {component: str},
          positive_factors: [str],
          risk_factors: [str],
          plain_explanation: str,
        }
    """
    scorers = {
        "income_stability": _score_income_stability,
        "savings": _score_savings,
        "expense_management": _score_expense_management,
        "debt_burden": _score_debt_burden,
        "repayment_behavior": _score_repayment,
        "liquidity": _score_liquidity,
    }

    component_scores = {}
    component_explanations = {}
    for name, scorer in scorers.items():
        score, expl = scorer(features)
        component_scores[name] = round(score)
        component_explanations[name] = expl

    # Weighted total
    total = sum(
        component_scores[c] * WEIGHTS[c] for c in WEIGHTS
    )
    total = round(min(100, max(0, total)))

    label = band_label(total)

    # Identify positive factors and risk factors
    positives = []
    risks = []

    if component_scores["income_stability"] >= 75:
        positives.append("Income has remained stable over the review period.")
    if component_scores["savings"] >= 70:
        positives.append(f"Savings rate is healthy at {features.get('savings_rate', 0):.0%}.")
    if component_scores["repayment_behavior"] >= 90:
        positives.append("All EMI payments are up to date.")
    if component_scores["debt_burden"] >= 75:
        positives.append("Debt burden is within safe limits.")
    if component_scores["liquidity"] >= 65:
        positives.append("Emergency buffer provides reasonable financial security.")
    if component_scores["expense_management"] >= 70:
        positives.append("Expenses are well-managed relative to income.")

    if component_scores["income_stability"] < 60:
        risks.append("Income variability may impact financial planning.")
    if component_scores["savings"] < 50:
        risks.append("Savings rate is below recommended levels.")
    if component_scores["debt_burden"] < 55:
        risks.append("EMI obligations are high relative to income.")
    if component_scores["repayment_behavior"] < 80:
        risks.append("Overdue loans may affect creditworthiness.")
    if component_scores["liquidity"] < 45:
        risks.append("Limited emergency reserves increase vulnerability to shocks.")
    if features.get("expense_surge", 0) > 0.10:
        risks.append("Household expenses have increased recently — review recurring costs.")

    if not positives:
        positives.append("There is clear potential to improve financial health with guidance.")
    if not risks:
        risks.append("No major risks identified at this time.")

    plain_explanation = (
        f"Your financial health score is {total} out of 100, rated as '{label}'. "
        f"The score reflects your income patterns, spending discipline, savings habits, "
        f"debt obligations, and repayment track record. "
        f"Key strength: {positives[0]} "
        f"Area to watch: {risks[0]}"
    )

    return {
        "score": total,
        "label": label,
        "change": 0,  # Historical comparison requires prior period data
        "components": component_scores,
        "component_explanations": component_explanations,
        "positive_factors": positives,
        "risk_factors": risks,
        "plain_explanation": plain_explanation,
    }


def compute_all_health_scores(all_features: List[Dict]) -> List[Dict]:
    """Compute health scores for all customers."""
    results = []
    for features in all_features:
        score_data = compute_health_score(features)
        score_data["customer_id"] = features["customer_id"]
        results.append(score_data)
    return results


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_all_data
    from features import compute_all_features

    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")
    data = load_all_data(seed_dir)
    features = compute_all_features(data["customers"], data["monthly_aggregates"], data["loans"])
    scores = compute_all_health_scores(features)

    for s in scores:
        print(f"\n{s['customer_id']}: Score={s['score']} ({s['label']})")
        print(f"  Components: {s['components']}")
        print(f"  Positives: {s['positive_factors']}")
        print(f"  Risks: {s['risk_factors']}")
