"""
Fixture Exporter — Saarthi Finance
Runs the complete ML pipeline and exports JSON fixtures for the backend and frontend.
Output files are consumed directly by the FastAPI backend and frontend mock data layer.
"""

import json
import os
import sys

# Ensure local imports work
sys.path.insert(0, os.path.dirname(__file__))

from preprocess import load_all_data
from features import compute_all_features
from health_score import compute_all_health_scores
from segmentation import compute_all_segments
from stress import detect_all_stress
from recommendations import generate_all_recommendations
from anomaly import run_anomaly_detection
from alerts import generate_all_alerts


SEED_DIR = os.path.join(os.path.dirname(__file__), "../../data/seed")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "../../data/processed")


def write_json(data, filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    size = os.path.getsize(filepath)
    print(f"  Written: {filepath}  ({size:,} bytes)")


def build_dashboard_fixture(
    customer: dict,
    features: dict,
    health: dict,
    recommendation: dict,
    alerts: list,
    monthly_data: list,
    transactions: list,
    goals: list,
    segment: dict,
    stress: dict,
) -> dict:
    """Build the shared dashboard response shape for one customer."""
    cid = customer["customer_id"]

    # Last 10 transactions for this customer
    cust_txns = sorted(
        [t for t in transactions if t["customer_id"] == cid],
        key=lambda x: x["date"],
        reverse=True,
    )[:10]

    # Monthly cash flow summary (last month)
    last_month = monthly_data[-1] if monthly_data else {}

    return {
        "customer": {
            "id": cid,
            "name": customer["name"],
            "city": customer["city"],
            "state": customer["state"],
            "age": customer["age"],
            "occupation": customer["occupation"],
            "preferred_language": customer["preferred_language"],
            "dependents": customer["dependents"],
            "financial_goal": customer["financial_goal"],
            "customer_segment": segment.get("segment", customer["customer_segment"]),
            "segment_description": segment.get("segment_description", ""),
            "segment_icon": segment.get("segment_icon", "📋"),
        },
        "financial_health": {
            "score": health["score"],
            "label": health["label"],
            "change": health["change"],
            "components": health["components"],
            "component_explanations": health.get("component_explanations", {}),
            "positive_factors": health["positive_factors"],
            "risk_factors": health["risk_factors"],
            "plain_explanation": health.get("plain_explanation", ""),
        },
        "cash_flow": {
            "monthly_income": customer["monthly_income"],
            "avg_monthly_income": features.get("avg_monthly_income", customer["monthly_income"]),
            "avg_monthly_expenses": features.get("avg_monthly_expenses", 0),
            "avg_monthly_emi": features.get("avg_monthly_emi", 0),
            "avg_monthly_savings": features.get("avg_monthly_savings", 0),
            "savings_rate": round(features.get("savings_rate", 0) * 100, 1),
            "emi_ratio": round(features.get("emi_ratio", 0) * 100, 1),
            "last_month": last_month,
        },
        "recommendation": {
            "type": recommendation.get("recommendation_type", "savings"),
            "title": recommendation.get("title", ""),
            "product": recommendation.get("product", ""),
            "category": recommendation.get("category", ""),
            "recommended_amount": recommendation.get("recommended_amount"),
            "estimated_emi": recommendation.get("estimated_emi"),
            "confidence": recommendation.get("confidence", 0.0),
            "why": recommendation.get("why", []),
            "not_recommended": recommendation.get("not_recommended", []),
            "not_recommended_reason": recommendation.get("not_recommended_reason", ""),
            "loan_suppressed": recommendation.get("loan_suppressed", False),
            "requires_human_review": recommendation.get("requires_human_review", False),
            "warning": recommendation.get("disclaimer", ""),
        },
        "stress": {
            "level": stress.get("stress_level", "none"),
            "score": stress.get("stress_score", 0),
            "evidence": stress.get("evidence", []),
            "confidence": stress.get("confidence", 0.0),
            "intervention": stress.get("customer_intervention", ""),
        },
        "alerts": alerts[:5],  # Top 5 alerts for dashboard
        "recent_transactions": [
            {
                "id": t["transaction_id"],
                "date": t["date"],
                "amount": t["amount"],
                "type": t["transaction_type"],
                "category": t["category"],
                "merchant": t["merchant"],
                "description": t["description"],
                "recurring": t.get("recurring", False),
            }
            for t in cust_txns
        ],
        "goals": [
            {
                "id": g["goal_id"],
                "type": g["goal_type"],
                "target_amount": g["target_amount"],
                "current_amount": g["current_amount"],
                "target_date": g["target_date"],
                "monthly_contribution": g["monthly_contribution"],
                "progress_pct": round(
                    g["current_amount"] / g["target_amount"] * 100, 1
                ) if g["target_amount"] > 0 else 0,
            }
            for g in goals
        ],
        "monthly_trends": monthly_data,
        "assistant_context": {
            "summary": (
                f"{customer['name']} has {'stable' if features.get('income_stability', 0) > 0.7 else 'variable'} income, "
                f"{'healthy' if features.get('savings_rate', 0) >= 0.15 else 'moderate'} savings, "
                f"and {'manageable' if features.get('emi_ratio', 0) <= 0.30 else 'high'} EMI obligations. "
                f"Financial health score: {health['score']}/100 ({health['label']}). "
                f"Primary goal: {customer.get('financial_goal', 'N/A')}."
            ),
            "stress_level": stress.get("stress_level", "none"),
            "loan_suppressed": stress.get("loan_recommendation_suppressed", False),
        },
    }


def run_pipeline():
    """Run the complete ML pipeline and export all fixtures."""
    print("=" * 60)
    print("Saarthi Finance — ML Pipeline")
    print("=" * 60)

    # Step 1: Load and preprocess data
    data = load_all_data(SEED_DIR)
    customers = data["customers"]
    transactions = data["transactions"]
    loans = data["loans"]
    goals = data["goals"]
    monthly_aggregates = data["monthly_aggregates"]

    # Step 2: Feature engineering
    print("\n[2/7] Computing features...")
    all_features = compute_all_features(customers, monthly_aggregates, loans)

    # Step 3: Health scores
    print("[3/7] Computing health scores...")
    health_scores = compute_all_health_scores(all_features)

    # Step 4: Segmentation
    print("[4/7] Segmenting customers...")
    segments = compute_all_segments(all_features)

    # Step 5: Stress detection
    print("[5/7] Detecting financial stress...")
    stress_results = detect_all_stress(all_features)

    # Step 6: Recommendations
    print("[6/7] Generating recommendations...")
    recommendations = generate_all_recommendations(
        customers, all_features, stress_results, health_scores, segments
    )

    # Step 7: Anomaly detection + alerts
    print("[7/7] Running anomaly detection and alerts...")
    anomaly_results = run_anomaly_detection(transactions, monthly_aggregates, customers)
    goals_by_customer = {}
    for g in goals:
        goals_by_customer.setdefault(g["customer_id"], []).append(g)

    alerts_by_customer = generate_all_alerts(
        customers, all_features, stress_results, anomaly_results, monthly_aggregates
    )

    # ── BUILD FIXTURES ────────────────────────────────────────
    print("\nExporting fixtures...")

    feature_map = {f["customer_id"]: f for f in all_features}
    health_map = {h["customer_id"]: h for h in health_scores}
    segment_map = {s["customer_id"]: s for s in segments}
    stress_map = {s["customer_id"]: s for s in stress_results}
    rec_map = {r["customer_id"]: r for r in recommendations}

    # 1. Customer features
    write_json(all_features, os.path.join(PROCESSED_DIR, "customer_features.json"))

    # 2. Health scores
    write_json(health_scores, os.path.join(PROCESSED_DIR, "health_scores.json"))

    # 3. Segments
    write_json(segments, os.path.join(PROCESSED_DIR, "segments.json"))

    # 4. Stress results
    write_json(stress_results, os.path.join(PROCESSED_DIR, "stress_signals.json"))

    # 5. Recommendations
    write_json(recommendations, os.path.join(PROCESSED_DIR, "recommendations.json"))

    # 6. Anomalies
    write_json(anomaly_results, os.path.join(PROCESSED_DIR, "anomalies.json"))

    # 7. Alerts per customer
    write_json(alerts_by_customer, os.path.join(PROCESSED_DIR, "alerts.json"))

    # 8. Dashboard fixtures (one per customer, plus combined)
    dashboards = {}
    for customer in customers:
        cid = customer["customer_id"]
        dashboard = build_dashboard_fixture(
            customer=customer,
            features=feature_map.get(cid, {}),
            health=health_map.get(cid, {}),
            recommendation=rec_map.get(cid, {}),
            alerts=alerts_by_customer.get(cid, []),
            monthly_data=monthly_aggregates.get(cid, []),
            transactions=transactions,
            goals=goals_by_customer.get(cid, []),
            segment=segment_map.get(cid, {}),
            stress=stress_map.get(cid, {}),
        )
        dashboards[cid] = dashboard

    write_json(dashboards, os.path.join(PROCESSED_DIR, "dashboards.json"))

    # 9. Single dashboard for primary demo customer (Ananya)
    write_json(
        dashboards.get("cust_001", {}),
        os.path.join(PROCESSED_DIR, "dashboard_cust_001.json"),
    )

    # 10. Transactions export
    write_json(transactions, os.path.join(PROCESSED_DIR, "transactions.json"))

    print("\n" + "=" * 60)
    print("Pipeline complete! Fixtures written to data/processed/")
    print("=" * 60)

    # Print summary
    print("\nCustomer Summary:")
    print(f"{'ID':<12} {'Name':<18} {'Score':>6} {'Segment':<25} {'Stress':<10} {'Rec'}")
    print("-" * 90)
    for customer in customers:
        cid = customer["customer_id"]
        h = health_map.get(cid, {})
        seg = segment_map.get(cid, {})
        st = stress_map.get(cid, {})
        rec = rec_map.get(cid, {})
        suppressed = " [SUPPRESSED]" if rec.get("loan_suppressed") else ""
        print(
            f"{cid:<12} {customer['name']:<18} {h.get('score', 0):>6} "
            f"{seg.get('segment', ''):<25} {st.get('stress_level', 'none'):<10} "
            f"{rec.get('title', '')[:30]}{suppressed}"
        )


if __name__ == "__main__":
    run_pipeline()
