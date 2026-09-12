"""
Anomaly Detection Module — Saarthi Finance
Uses statistical methods: rolling median, IQR, z-score.
All anomalies are explainable. No black-box models used for customer-facing alerts.
"""

import statistics
import math
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def _iqr_bounds(values: List[float]) -> Tuple[float, float]:
    """Compute IQR-based bounds for outlier detection."""
    if len(values) < 4:
        return (0.0, float("inf"))
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    q1 = sorted_vals[n // 4]
    q3 = sorted_vals[(3 * n) // 4]
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return lower, upper


def _z_score(value: float, values: List[float]) -> float:
    """Compute z-score of a value relative to a list."""
    if len(values) < 2:
        return 0.0
    mean = statistics.mean(values)
    std = statistics.stdev(values)
    if std == 0:
        return 0.0
    return (value - mean) / std


def detect_unusual_transactions(
    transactions: List[Dict], customer_id: str
) -> List[Dict]:
    """
    Detect individual transactions with unusually high amounts per category.
    Uses IQR bounds per category.
    """
    cust_txns = [
        t for t in transactions
        if t["customer_id"] == customer_id and t["transaction_type"] == "debit"
    ]

    # Group amounts by category
    cat_amounts: Dict[str, List[float]] = defaultdict(list)
    for t in cust_txns:
        cat_amounts[t["category"]].append(t["amount"])

    anomalies = []
    for t in cust_txns:
        cat = t["category"]
        amounts = cat_amounts[cat]
        if len(amounts) < 3:
            continue

        lower, upper = _iqr_bounds(amounts)
        z = _z_score(t["amount"], amounts)
        median = statistics.median(amounts)

        if t["amount"] > upper and z > 2.0:
            anomalies.append({
                "transaction_id": t["transaction_id"],
                "customer_id": customer_id,
                "anomaly_type": "unusual_amount",
                "category": cat,
                "merchant": t.get("merchant", "Unknown"),
                "amount": t["amount"],
                "date": t["date"],
                "severity": "high" if z > 3.0 else "medium",
                "evidence": f"Amount ₹{t['amount']:,.0f} is {t['amount']/median:.1f}x the typical "
                            f"₹{median:,.0f} for {cat} (z-score: {z:.1f}).",
                "explanation": f"This {cat} transaction of ₹{t['amount']:,.0f} is significantly "
                               f"higher than your usual spending in this category.",
            })

    return anomalies


def detect_new_merchant(transactions: List[Dict], customer_id: str) -> List[Dict]:
    """Flag transactions at merchants never seen before in the last 3 months."""
    cust_txns = sorted(
        [t for t in transactions if t["customer_id"] == customer_id],
        key=lambda x: x["date"],
    )
    if len(cust_txns) < 10:
        return []

    # Split into "history" and "recent" periods
    cutoff_idx = max(1, int(len(cust_txns) * 0.7))
    history_merchants = {t["merchant"] for t in cust_txns[:cutoff_idx]}
    recent_txns = cust_txns[cutoff_idx:]

    anomalies = []
    for t in recent_txns:
        if t["merchant"] not in history_merchants and t["transaction_type"] == "debit":
            anomalies.append({
                "transaction_id": t["transaction_id"],
                "customer_id": customer_id,
                "anomaly_type": "new_merchant",
                "category": t.get("category", "Other"),
                "merchant": t["merchant"],
                "amount": t["amount"],
                "date": t["date"],
                "severity": "low",
                "evidence": f"New merchant '{t['merchant']}' not seen in prior transaction history.",
                "explanation": f"A transaction of ₹{t['amount']:,.0f} was made at "
                               f"'{t['merchant']}', which is a new merchant for you.",
            })

    return anomalies


def detect_category_surge(
    monthly_aggregates: List[Dict], customer_id: str
) -> List[Dict]:
    """
    Detect months where a spending category increased by >40% vs prior month.
    """
    monthly = sorted(monthly_aggregates, key=lambda x: x["month"])
    if len(monthly) < 3:
        return []

    anomalies = []
    for i in range(1, len(monthly)):
        prev = monthly[i - 1].get("category_breakdown", {})
        curr = monthly[i].get("category_breakdown", {})

        for cat, curr_amt in curr.items():
            prev_amt = prev.get(cat, 0)
            if prev_amt == 0 or cat in ("Salary", "Savings"):
                continue
            change_pct = (curr_amt - prev_amt) / prev_amt
            if change_pct > 0.40:
                anomalies.append({
                    "customer_id": customer_id,
                    "anomaly_type": "category_surge",
                    "category": cat,
                    "month": monthly[i]["month"],
                    "current_amount": round(curr_amt, 2),
                    "previous_amount": round(prev_amt, 2),
                    "change_pct": round(change_pct * 100, 1),
                    "severity": "high" if change_pct > 0.70 else "medium",
                    "evidence": f"{cat} spending rose from ₹{prev_amt:,.0f} to "
                                f"₹{curr_amt:,.0f} ({change_pct:.0%} increase).",
                    "explanation": f"Your {cat} spending increased by {change_pct:.0%} "
                                   f"in {monthly[i]['month']}. This may warrant review.",
                })

    return anomalies


def detect_income_drop(monthly_aggregates: List[Dict], customer_id: str) -> List[Dict]:
    """Flag months where income dropped by more than 25%."""
    monthly = sorted(monthly_aggregates, key=lambda x: x["month"])
    if len(monthly) < 3:
        return []

    incomes = [m["income"] for m in monthly if m["income"] > 0]
    if not incomes:
        return []

    baseline = statistics.median(incomes)
    anomalies = []
    for m in monthly:
        if m["income"] > 0 and m["income"] < baseline * 0.75:
            drop_pct = (baseline - m["income"]) / baseline
            anomalies.append({
                "customer_id": customer_id,
                "anomaly_type": "income_drop",
                "month": m["month"],
                "observed_income": round(m["income"], 2),
                "baseline_income": round(baseline, 2),
                "drop_pct": round(drop_pct * 100, 1),
                "severity": "high" if drop_pct > 0.40 else "medium",
                "evidence": f"Income of ₹{m['income']:,.0f} in {m['month']} is "
                            f"{drop_pct:.0%} below the typical ₹{baseline:,.0f}.",
                "explanation": f"Income was significantly lower in {m['month']}. "
                               f"This could indicate a missed payment or irregular work pattern.",
            })

    return anomalies


def run_anomaly_detection(
    transactions: List[Dict],
    monthly_aggregates: Dict[str, List[Dict]],
    customers: List[Dict],
) -> Dict[str, List[Dict]]:
    """
    Run all anomaly detectors for each customer.

    Returns:
        {customer_id: [list of anomaly dicts]}
    """
    results: Dict[str, List[Dict]] = {}

    for customer in customers:
        cid = customer["customer_id"]
        cust_monthly = monthly_aggregates.get(cid, [])

        anomalies: List[Dict] = []
        anomalies.extend(detect_unusual_transactions(transactions, cid))
        anomalies.extend(detect_new_merchant(transactions, cid))
        anomalies.extend(detect_category_surge(cust_monthly, cid))
        anomalies.extend(detect_income_drop(cust_monthly, cid))

        # De-duplicate by transaction_id where present, keep unique
        seen = set()
        unique = []
        for a in anomalies:
            key = a.get("transaction_id") or f"{a['anomaly_type']}_{a.get('month','')}"
            if key not in seen:
                seen.add(key)
                unique.append(a)

        results[cid] = unique

    return results


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocess import load_all_data

    seed_dir = os.path.join(os.path.dirname(__file__), "../../data/seed")
    data = load_all_data(seed_dir)
    anomalies = run_anomaly_detection(
        data["transactions"],
        data["monthly_aggregates"],
        data["customers"],
    )

    for cid, anom_list in anomalies.items():
        if anom_list:
            print(f"\n{cid} — {len(anom_list)} anomalies:")
            for a in anom_list[:3]:
                print(f"  [{a['severity'].upper()}] {a['anomaly_type']}: {a['evidence']}")
