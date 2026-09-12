"""
Behavioral Segmentation Module — Saarthi Finance
Assigns interpretable customer segments using rule-based logic.
Every segment has a clear explanation. No protected attributes are used.
"""

from typing import Dict, List, Tuple


# ─────────────────────────────────────────────────────────────
# SEGMENT DEFINITIONS
# ─────────────────────────────────────────────────────────────
SEGMENTS = {
    "Stable Planner": {
        "description": "Consistent income, controlled expenses, regular savings, and manageable debt.",
        "opportunity": "Goal-based savings and long-term investment products.",
        "icon": "📊",
    },
    "Growing Saver": {
        "description": "Savings rate is improving month-on-month. Income is steady.",
        "opportunity": "Savings boosters, SIPs, and goal-based products.",
        "icon": "📈",
    },
    "High Discretionary Spender": {
        "description": "Earns adequately but spends heavily on discretionary categories.",
        "opportunity": "Budgeting guidance, spending alerts, and micro-savings nudges.",
        "icon": "🛍️",
    },
    "Cash Flow Constrained": {
        "description": "Limited income with high essential expense burden leaves little room for savings.",
        "opportunity": "Emergency micro-savings, income supplement guidance.",
        "icon": "⚠️",
    },
    "EMI Stressed": {
        "description": "EMI obligations are high relative to income, leaving limited flexibility.",
        "opportunity": "Debt restructuring guidance, stress support, no new loan recommendations.",
        "icon": "🚨",
    },
    "Irregular Income": {
        "description": "Income fluctuates significantly — seasonal or gig-based work pattern.",
        "opportunity": "Buffer savings, income smoothing guidance.",
        "icon": "🔄",
    },
    "New to Digital": {
        "description": "Recently adopted digital banking. Building transaction and savings history.",
        "opportunity": "Financial literacy, simple savings products, UPI usage guidance.",
        "icon": "🌱",
    },
}


def assign_segment(features: Dict) -> Tuple[str, str, str]:
    """
    Assign the most relevant behavioral segment using rule-based logic.

    Returns:
        (segment_name, description, opportunity)
    """
    emi_ratio = features.get("emi_ratio", 0.0)
    savings_rate = features.get("savings_rate", 0.0)
    savings_trend = features.get("savings_trend", 0.0)
    income_stability = features.get("income_stability", 0.5)
    expense_ratio = features.get("expense_ratio", 0.7)
    expense_surge = features.get("expense_surge", 0.0)
    months = features.get("months_of_data", 0)
    overdue = features.get("overdue_loan_count", 0)

    # Determine segment by priority rules
    if emi_ratio > 0.40 or overdue > 0:
        seg = "EMI Stressed"
    elif income_stability < 0.50:
        seg = "Irregular Income"
    elif months <= 2:
        seg = "New to Digital"
    elif expense_ratio > 0.85 and savings_rate < 0.05:
        seg = "Cash Flow Constrained"
    elif savings_rate > 0.20 and savings_trend > 0:
        seg = "Growing Saver"
    elif expense_surge > 0.15 and savings_rate < 0.15:
        seg = "High Discretionary Spender"
    elif income_stability >= 0.75 and savings_rate >= 0.15 and emi_ratio <= 0.30:
        seg = "Stable Planner"
    elif savings_trend > 0.05:
        seg = "Growing Saver"
    elif expense_ratio > 0.75:
        seg = "Cash Flow Constrained"
    else:
        seg = "Stable Planner"

    info = SEGMENTS.get(seg, {"description": "", "opportunity": "", "icon": "📋"})
    return seg, info["description"], info["opportunity"]


def compute_all_segments(all_features: List[Dict]) -> List[Dict]:
    """Compute segments for all customers."""
    results = []
    for features in all_features:
        segment, description, opportunity = assign_segment(features)
        results.append({
            "customer_id": features["customer_id"],
            "segment": segment,
            "segment_description": description,
            "segment_opportunity": opportunity,
            "segment_icon": SEGMENTS.get(segment, {}).get("icon", "📋"),
        })
    return results


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_all_data
    from features import compute_all_features

    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")
    data = load_all_data(seed_dir)
    all_features = compute_all_features(data["customers"], data["monthly_aggregates"], data["loans"])
    segments = compute_all_segments(all_features)

    segment_dist = {}
    for s in segments:
        seg = s["segment"]
        segment_dist[seg] = segment_dist.get(seg, 0) + 1
        print(f"  {s['customer_id']}: {s['segment_icon']} {seg}")

    print("\nSegment distribution:")
    for seg, count in sorted(segment_dist.items()):
        print(f"  {seg}: {count}")
