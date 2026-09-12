"""
Responsible Recommendation Engine — Saarthi Finance
Generates explainable, customer-benefit-first financial product recommendations.

Key principles:
- Never recommend borrowing when financial stress is high
- Recommend safe amount ranges, not maximum eligible amounts
- Every recommendation includes a rationale and known limitations
- No predatory nudging or revenue-first recommendations
- Alternatives considered and explained
"""

import math
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────
# PRODUCT CATALOG
# ─────────────────────────────────────────────────────────────
PRODUCTS = {
    "emergency_savings": {
        "type": "savings",
        "title": "Build a Stronger Emergency Buffer",
        "product": "Emergency Savings Plan",
        "category": "Savings",
        "description": "A dedicated savings account or recurring deposit to cover 3–6 months of expenses.",
        "benefit": "Protects you from unexpected expenses without needing a loan.",
    },
    "goal_savings": {
        "type": "savings",
        "title": "Goal-Based Savings Plan",
        "product": "Recurring Deposit / Goal Plan",
        "category": "Savings",
        "description": "Regular monthly contribution toward a specific financial goal.",
        "benefit": "Helps you reach your financial goals systematically.",
    },
    "personal_loan": {
        "type": "loan",
        "title": "Personal Loan",
        "product": "Personal Loan",
        "category": "Borrowing",
        "description": "Unsecured loan for personal financial needs.",
        "benefit": "Provides liquidity for planned or urgent needs at manageable EMI.",
    },
    "education_loan": {
        "type": "loan",
        "title": "Education Loan",
        "product": "Education Loan",
        "category": "Borrowing",
        "description": "Loan for educational expenses with favorable interest rates.",
        "benefit": "Invests in future earning potential without depleting savings.",
    },
    "insurance": {
        "type": "protection",
        "title": "Term Insurance",
        "product": "Term Life Insurance",
        "category": "Protection",
        "description": "Affordable life insurance to protect financial dependents.",
        "benefit": "Ensures your family is financially protected in case of emergency.",
    },
    "credit_card": {
        "type": "credit",
        "title": "Low-Limit Credit Card",
        "product": "Starter Credit Card",
        "category": "Credit",
        "description": "A controlled credit card to build credit history with a low limit.",
        "benefit": "Helps build credit profile while managing risk through a low limit.",
    },
    "investment_starter": {
        "type": "investment",
        "title": "Micro-Investment Starter",
        "product": "SIP / Mutual Fund",
        "category": "Investment",
        "description": "Start investing small amounts monthly in a diversified mutual fund.",
        "benefit": "Builds long-term wealth through disciplined small investments.",
    },
    "debt_restructuring": {
        "type": "support",
        "title": "Loan Restructuring Support",
        "product": "EMI Relief or Restructuring",
        "category": "Support",
        "description": "Speak with a financial advisor to explore EMI restructuring options.",
        "benefit": "Reduces monthly EMI pressure and prevents default risk.",
    },
}


def _calculate_safe_loan_amount(
    monthly_income: float,
    current_emi: float,
    target_emi_ratio: float = 0.30,
) -> Tuple[float, float]:
    """
    Calculate the safe additional EMI room and corresponding loan amount.
    Assumes 12% interest, 24-month tenure for personal loans.
    """
    max_safe_emi = monthly_income * target_emi_ratio
    available_emi = max(0.0, max_safe_emi - current_emi)

    # Back-calculate principal from EMI
    # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    rate = 0.12 / 12  # monthly rate
    n = 24  # tenure months
    if rate > 0 and available_emi > 0:
        pv_factor = (math.pow(1 + rate, n) - 1) / (rate * math.pow(1 + rate, n))
        principal = available_emi * pv_factor
    else:
        principal = 0.0

    return round(available_emi, 2), round(principal / 1000) * 1000  # round to nearest 1000


def generate_recommendation(
    customer: Dict,
    features: Dict,
    stress_result: Dict,
    health_score: Dict,
    segment: str,
) -> Dict:
    """
    Generate a single primary responsible recommendation.

    Returns:
        Full recommendation dict aligned with the shared API contract.
    """
    income = customer.get("monthly_income", features.get("declared_monthly_income", 0))
    goal = customer.get("financial_goal", "")
    emi_ratio = features.get("emi_ratio", 0.0)
    savings_rate = features.get("savings_rate", 0.0)
    emergency_months = features.get("emergency_fund_months", 0.0)
    overdue = features.get("overdue_loan_count", 0)
    stress_score = stress_result.get("stress_score", 0)
    suppress_loan = stress_result.get("loan_recommendation_suppressed", False)
    cid = customer["customer_id"]

    # ── DECISION LOGIC ──────────────────────────────────────

    # Priority 1: EMI stress / overdue → debt restructuring
    if overdue > 0 or stress_score >= 3:
        prod_key = "debt_restructuring"
        confidence = 0.95
        why = [
            "You have overdue loan obligations that need immediate attention.",
            "Taking additional debt now would increase financial risk.",
            "Speaking with an advisor could help restructure your EMI burden.",
        ]
        not_recommended = ["personal_loan", "credit_card", "investment_starter"]
        not_recommended_reason = (
            "Borrowing more or investing while repayments are overdue increases financial risk. "
            "Stabilizing existing obligations is the priority."
        )
        safe_amount = None
        safe_emi = None

    # Priority 2: Low emergency fund → emergency savings
    elif emergency_months < 2 and savings_rate < 0.15:
        prod_key = "emergency_savings"
        monthly_shortfall = max(1000, income * 0.05)
        confidence = 0.91
        why = [
            f"Your emergency fund covers only ~{emergency_months:.1f} months of expenses.",
            "An emergency buffer is the most important financial safety net.",
            "Building savings first reduces the need for emergency borrowing.",
        ]
        not_recommended = ["personal_loan", "investment_starter"]
        not_recommended_reason = (
            "Without an emergency buffer, unexpected expenses may force high-cost emergency borrowing. "
            "Build savings first."
        )
        safe_amount = round(monthly_shortfall * 12)  # 12-month target
        safe_emi = round(monthly_shortfall)

    # Priority 3: Medium stress → goal savings
    elif suppress_loan and savings_rate >= 0.05:
        prod_key = "goal_savings"
        monthly_contrib = max(500, income * 0.08)
        confidence = 0.85
        why = [
            "Your finances are under some pressure right now.",
            "Building savings is safer than taking on additional debt.",
            "A goal-based savings plan helps achieve your target systematically.",
        ]
        not_recommended = ["personal_loan", "credit_card"]
        not_recommended_reason = (
            "Adding new loan obligations during a period of financial pressure is not recommended. "
            "Strengthening savings reduces long-term risk."
        )
        safe_amount = round(monthly_contrib * 12)
        safe_emi = round(monthly_contrib)

    # Priority 4: Goal-aligned loan if stress is low
    elif not suppress_loan and emi_ratio <= 0.25 and goal == "Education Savings":
        prod_key = "education_loan"
        safe_emi, safe_amount = _calculate_safe_loan_amount(income, features.get("emi_amount_total", 0))
        confidence = 0.82
        why = [
            "Your financial health score supports responsible borrowing.",
            "Education loans have favorable interest rates and tax benefits.",
            f"Your current EMI burden of {emi_ratio:.0%} leaves room for an additional EMI.",
        ]
        not_recommended = ["personal_loan", "investment_starter"]
        not_recommended_reason = "A personal loan for education would carry higher interest than an education-specific loan."

    # Priority 5: Insurance if dependents and no coverage
    elif customer.get("dependents", 0) >= 2 and not suppress_loan and savings_rate >= 0.10:
        prod_key = "insurance"
        confidence = 0.87
        why = [
            f"You have {customer.get('dependents', 0)} dependents who depend on your income.",
            "Term insurance is one of the most important financial protections for your family.",
            "Your current savings allow for a modest insurance premium.",
        ]
        not_recommended = ["investment_starter"]
        not_recommended_reason = "Protection comes before investment, especially for households with dependents."
        safe_amount = round(income * 100)  # Rule of thumb: 100x monthly income coverage
        safe_emi = round(income * 0.01)  # ~1% of income premium

    # Priority 6: Personal loan if healthy and need
    elif not suppress_loan and emi_ratio <= 0.20 and health_score.get("score", 0) >= 65:
        prod_key = "personal_loan"
        safe_emi, safe_amount = _calculate_safe_loan_amount(income, features.get("emi_amount_total", 0))
        confidence = 0.78
        why = [
            f"Your financial health score of {health_score.get('score', 0)} supports borrowing.",
            f"EMI burden of {emi_ratio:.0%} is well within safe limits.",
            "A personal loan can help achieve your financial goal with a manageable repayment plan.",
        ]
        not_recommended = ["credit_card"]
        not_recommended_reason = "A structured personal loan has lower and more predictable interest than revolving credit."

    # Default: goal savings
    else:
        prod_key = "goal_savings"
        monthly_contrib = max(500, income * 0.08)
        confidence = 0.75
        why = [
            "Building a consistent savings habit is the safest foundation for any financial goal.",
            f"Even ₹{round(monthly_contrib):,}/month can grow significantly over time.",
        ]
        not_recommended = []
        not_recommended_reason = ""
        safe_amount = round(monthly_contrib * 12)
        safe_emi = round(monthly_contrib)

    product = PRODUCTS[prod_key]

    # Build result
    result = {
        "customer_id": cid,
        "recommendation_type": product["type"],
        "title": product["title"],
        "product": product["product"],
        "category": product["category"],
        "description": product["description"],
        "customer_benefit": product["benefit"],
        "recommended_amount": safe_amount,
        "estimated_emi": safe_emi,
        "confidence": confidence,
        "why": why,
        "not_recommended": not_recommended,
        "not_recommended_reason": not_recommended_reason,
        "suitability_constraints": [
            "This recommendation is based on synthetic data for demonstration purposes.",
            "Actual eligibility depends on credit bureau data and bank policies.",
        ],
        "requires_human_review": stress_result.get("requires_human_review", False),
        "loan_suppressed": suppress_loan,
        "disclaimer": (
            "This is financial guidance, not a loan approval or financial advice. "
            "Please consult with a certified financial advisor before making borrowing decisions."
        ),
    }

    return result


def generate_all_recommendations(
    customers: List[Dict],
    all_features: List[Dict],
    stress_results: List[Dict],
    health_scores: List[Dict],
    segments: List[Dict],
) -> List[Dict]:
    """Generate recommendations for all customers."""
    feature_map = {f["customer_id"]: f for f in all_features}
    stress_map = {s["customer_id"]: s for s in stress_results}
    health_map = {h["customer_id"]: h for h in health_scores}
    segment_map = {s["customer_id"]: s["segment"] for s in segments}

    recommendations = []
    for customer in customers:
        cid = customer["customer_id"]
        rec = generate_recommendation(
            customer=customer,
            features=feature_map.get(cid, {}),
            stress_result=stress_map.get(cid, {"stress_score": 0, "loan_recommendation_suppressed": False}),
            health_score=health_map.get(cid, {}),
            segment=segment_map.get(cid, "Stable Planner"),
        )
        recommendations.append(rec)

    return recommendations


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_all_data
    from features import compute_all_features
    from health_score import compute_all_health_scores
    from stress import detect_all_stress
    from segmentation import compute_all_segments

    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")
    data = load_all_data(seed_dir)
    features = compute_all_features(data["customers"], data["monthly_aggregates"], data["loans"])
    scores = compute_all_health_scores(features)
    stress = detect_all_stress(features)
    segments = compute_all_segments(features)
    recs = generate_all_recommendations(data["customers"], features, stress, scores, segments)

    print("\nRecommendations:")
    for r in recs:
        suppressed = " [LOAN SUPPRESSED]" if r["loan_suppressed"] else ""
        print(f"\n  {r['customer_id']}: {r['title']} (confidence={r['confidence']:.0%}){suppressed}")
        for reason in r["why"]:
            print(f"    → {reason}")
