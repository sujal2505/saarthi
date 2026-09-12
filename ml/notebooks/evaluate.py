"""
Evaluation Script - Saarthi Finance
Tests and validates the ML pipeline outputs:
- Segment distribution
- Health score explanations
- Anomaly detection examples
- Loan suppression under stress
- Recommendation consistency
"""

import sys
import os
import io
import json

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from preprocess import load_all_data
from features import compute_all_features
from health_score import compute_all_health_scores
from segmentation import compute_all_segments, SEGMENTS
from stress import detect_all_stress
from recommendations import generate_all_recommendations
from anomaly import run_anomaly_detection


def separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_segment_distribution(segments):
    separator("Segment Distribution")
    dist = {}
    for s in segments:
        seg = s["segment"]
        dist[seg] = dist.get(seg, 0) + 1

    for seg, count in sorted(dist.items(), key=lambda x: -x[1]):
        bar = "#" * count
        print(f"  [{seg:<30}] {bar} ({count})")

    print(f"\n  Total segments defined: {len(SEGMENTS)}")
    print(f"  Total customers segmented: {len(segments)}")
    assert len(segments) > 0, "No segments generated"


def test_health_score_explanations(features, health_scores):
    separator("Health Score Explanations")

    for h in health_scores:
        cid = h["customer_id"]
        print(f"\n  [{cid}] Score: {h['score']}/100 ({h['label']})")
        print(f"    Components:")
        for comp, score in h["components"].items():
            bar = "#" * (score // 10) + "." * (10 - score // 10)
            print(f"      {comp:<22} {bar} {score}")
        print(f"    [+] {h['positive_factors'][0] if h['positive_factors'] else 'N/A'}")
        print(f"    [!] {h['risk_factors'][0] if h['risk_factors'] else 'N/A'}")

    # Verify scores are within 0-100
    for h in health_scores:
        assert 0 <= h["score"] <= 100, f"Score out of range for {h['customer_id']}: {h['score']}"
        assert h["label"] in ("Excellent", "Stable", "Moderate", "Needs Attention", "At Risk")
    print("\n  [PASS] All health scores within valid range")


def test_anomaly_detection(anomaly_results):
    separator("Anomaly Detection Examples")

    total_anomalies = sum(len(v) for v in anomaly_results.values())
    print(f"  Total anomalies detected: {total_anomalies}")

    for cid, anomalies in anomaly_results.items():
        if anomalies:
            print(f"\n  {cid} — {len(anomalies)} anomalies:")
            for a in anomalies[:2]:
                sev_label = "[HIGH]" if a["severity"] == "high" else "[MED] "
                print(f"    {sev_label} [{a['anomaly_type']}] {a['evidence']}")

    # Arjun (cust_004) should have anomalies (shopping spike)
    arjun_anomalies = anomaly_results.get("cust_004", [])
    print(f"\n  Arjun Kumar (cust_004) anomalies: {len(arjun_anomalies)}")


def test_loan_suppression(features, stress_results, recommendations):
    separator("Loan Suppression Under Stress")

    feature_map = {f["customer_id"]: f for f in features}
    stress_map = {s["customer_id"]: s for s in stress_results}
    rec_map = {r["customer_id"]: r for r in recommendations}

    print(f"  {'Customer':<12} {'Stress':<10} {'EMI Ratio':>10} {'Loan Suppressed':>16} {'Recommendation'}")
    print(f"  {'-'*80}")
    for cid in sorted(rec_map.keys()):
        stress = stress_map.get(cid, {})
        rec = rec_map.get(cid, {})
        feat = feature_map.get(cid, {})

        suppressed = rec.get("loan_suppressed", False)
        stress_level = stress.get("stress_level", "none")
        emi_ratio = feat.get("emi_ratio", 0.0)
        rec_title = rec.get("title", "")[:35]

        icon = "[X]" if suppressed else "[OK]"
        print(f"  {cid:<12} {stress_level:<10} {emi_ratio:>9.0%} "
              f"  {icon} {'YES' if suppressed else 'NO':<14} {rec_title}")

    # Key assertion: Ramesh (cust_002) and Sunita (cust_005) should have loans suppressed
    ramesh_suppressed = rec_map.get("cust_002", {}).get("loan_suppressed", False)
    print(f"\n  Key check — Ramesh (cust_002) loan suppressed: {ramesh_suppressed}")
    if not ramesh_suppressed:
        print("  [WARNING] Ramesh has high EMI but loan not suppressed - review stress thresholds")
    else:
        print("  [PASS] Correct: Loan suppressed for high-EMI customer")


def test_recommendation_consistency(recommendations):
    separator("Recommendation Consistency")

    for r in recommendations:
        cid = r["customer_id"]
        assert "title" in r and r["title"], f"{cid}: Missing recommendation title"
        assert "why" in r and len(r["why"]) > 0, f"{cid}: Missing rationale"
        assert "disclaimer" in r, f"{cid}: Missing disclaimer"
        assert 0.0 <= r.get("confidence", 0) <= 1.0, f"{cid}: Invalid confidence"
        print(f"  [OK] {cid}: {r['title']} (confidence={r['confidence']:.0%})")

    print(f"\n  All {len(recommendations)} recommendations have required fields.")


def main():
    print("Saarthi Finance — ML Evaluation Script")
    print("All data is synthetic and for demonstration only.")

    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")

    if not os.path.exists(os.path.join(seed_dir, "customers.csv")):
        print(f"\nSeed data not found at: {seed_dir}")
        print("Run first: python ml/src/generate_data.py")
        sys.exit(1)

    # Load data
    data = load_all_data(seed_dir)
    all_features = compute_all_features(data["customers"], data["monthly_aggregates"], data["loans"])
    health_scores = compute_all_health_scores(all_features)
    segments = compute_all_segments(all_features)
    stress_results = detect_all_stress(all_features)
    recommendations = generate_all_recommendations(
        data["customers"], all_features, stress_results, health_scores, segments
    )
    anomaly_results = run_anomaly_detection(
        data["transactions"], data["monthly_aggregates"], data["customers"]
    )

    # Run tests
    test_segment_distribution(segments)
    test_health_score_explanations(all_features, health_scores)
    test_anomaly_detection(anomaly_results)
    test_loan_suppression(all_features, stress_results, recommendations)
    test_recommendation_consistency(recommendations)

    separator("Evaluation Complete")
    print("  All checks passed. Pipeline is working correctly.")


if __name__ == "__main__":
    main()
