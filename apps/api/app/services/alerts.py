"""
Saarthi Finance — Alert Generation Service.

Implements 5 alert types:
1. Unusual spending alert
2. Negative cash-flow trend alert
3. Reduced savings alert
4. Missed EMI risk alert
5. Potential fraud review alert

Each alert contains severity, explanation, evidence,
recommended action, and customer-friendly wording.
"""

from __future__ import annotations

from typing import List
import uuid

from app.schemas.alert import AlertResponse
from app.schemas.cash_flow import CashFlowResponse
from app.schemas.financial_health import FinancialHealthResponse
from app.schemas.transaction import SpendingCategoryResponse


def generate_alerts(
    health: FinancialHealthResponse,
    cash_flow: CashFlowResponse,
    spending_categories: List[SpendingCategoryResponse],
    prev_month_expenses: float = 0,
    has_large_unusual_txn: bool = False,
) -> List[AlertResponse]:
    """Generate all applicable alerts for a customer."""
    alerts: List[AlertResponse] = []

    # ------------------------------------------------------------------
    # 1. Unusual spending alert
    # ------------------------------------------------------------------
    for cat in spending_categories:
        if cat.trend == "up" and cat.change_pct and cat.change_pct > 15:
            alerts.append(
                AlertResponse(
                    id=f"alert_{uuid.uuid4().hex[:8]}",
                    type="unusual_spending",
                    severity="low" if cat.change_pct < 30 else "medium",
                    title=f"{cat.category} spend {cat.change_pct:.0f}% higher than usual",
                    description=(
                        f"You spent ₹{cat.amount:,.0f} on {cat.category.lower()} this month, "
                        f"which is {cat.change_pct:.0f}% more than your usual spending in this category."
                    ),
                    evidence=f"{cat.category}: ₹{cat.amount:,.0f} vs usual pattern",
                    action=(
                        "If these are one-time purchases, no action needed. "
                        "Otherwise, consider reviewing your spending habits in this category."
                    ),
                    action_label="View Transactions",
                )
            )

    # ------------------------------------------------------------------
    # 2. Negative cash-flow trend alert
    # ------------------------------------------------------------------
    if cash_flow.monthly_savings < 0:
        alerts.append(
            AlertResponse(
                id=f"alert_{uuid.uuid4().hex[:8]}",
                type="cash_flow",
                severity="high",
                title="Negative cash flow detected",
                description=(
                    f"Your expenses (₹{cash_flow.monthly_expenses:,.0f}) and EMI "
                    f"(₹{cash_flow.monthly_emi:,.0f}) exceed your income "
                    f"(₹{cash_flow.monthly_income:,.0f}) by ₹{abs(cash_flow.monthly_savings):,.0f}."
                ),
                evidence=(
                    f"Monthly shortfall: ₹{abs(cash_flow.monthly_savings):,.0f} | "
                    f"Income: ₹{cash_flow.monthly_income:,.0f}"
                ),
                action="Review your recurring expenses and consider speaking with a financial counsellor.",
                action_label="Review Expenses",
            )
        )
    elif prev_month_expenses > 0 and cash_flow.monthly_expenses > prev_month_expenses * 1.08:
        change_pct = ((cash_flow.monthly_expenses - prev_month_expenses) / prev_month_expenses) * 100
        alerts.append(
            AlertResponse(
                id=f"alert_{uuid.uuid4().hex[:8]}",
                type="cash_flow",
                severity="medium",
                title="Monthly expenses rising steadily",
                description=(
                    f"Your household spending increased by ₹{cash_flow.monthly_expenses - prev_month_expenses:,.0f} "
                    f"({change_pct:.0f}%) recently. If this trend continues, your savings rate may drop."
                ),
                evidence=f"Previous: ₹{prev_month_expenses:,.0f} → Current: ₹{cash_flow.monthly_expenses:,.0f}",
                action="Review your recurring expenses and identify where you can cut back.",
                action_label="Review Expenses",
            )
        )

    # ------------------------------------------------------------------
    # 3. Reduced savings alert
    # ------------------------------------------------------------------
    if 0 < cash_flow.savings_rate < 15:
        alerts.append(
            AlertResponse(
                id=f"alert_{uuid.uuid4().hex[:8]}",
                type="savings_decline",
                severity="medium" if cash_flow.savings_rate > 5 else "high",
                title="Savings rate is below recommended level",
                description=(
                    f"Your current savings rate is {cash_flow.savings_rate:.1f}%, "
                    f"which is below the recommended 20%. "
                    f"You are saving ₹{cash_flow.monthly_savings:,.0f} per month."
                ),
                evidence=f"Savings rate: {cash_flow.savings_rate:.1f}% (recommended: 20%+)",
                action="Consider reducing discretionary spending to boost your savings.",
                action_label="View Savings Tips",
            )
        )

    # ------------------------------------------------------------------
    # 4. Missed EMI risk alert
    # ------------------------------------------------------------------
    if cash_flow.monthly_income > 0:
        emi_ratio = cash_flow.monthly_emi / cash_flow.monthly_income
        if emi_ratio > 0.45:
            alerts.append(
                AlertResponse(
                    id=f"alert_{uuid.uuid4().hex[:8]}",
                    type="missed_emi_risk",
                    severity="high" if emi_ratio > 0.55 else "medium",
                    title="High EMI burden — missed payment risk",
                    description=(
                        f"Your EMI-to-income ratio is {emi_ratio * 100:.1f}%, "
                        f"which is above the safe threshold of 40%. "
                        f"This increases the risk of missed payments."
                    ),
                    evidence=f"EMI: ₹{cash_flow.monthly_emi:,.0f} | Income: ₹{cash_flow.monthly_income:,.0f}",
                    action="Consider restructuring existing loans or increasing income sources.",
                    action_label="Explore Options",
                )
            )

    # ------------------------------------------------------------------
    # 5. Potential fraud review alert
    # ------------------------------------------------------------------
    if has_large_unusual_txn:
        alerts.append(
            AlertResponse(
                id=f"alert_{uuid.uuid4().hex[:8]}",
                type="fraud_review",
                severity="high",
                title="Unusual large transaction detected",
                description=(
                    "A transaction significantly larger than your typical spending "
                    "pattern has been detected. Please verify this is authorized."
                ),
                evidence="Transaction amount exceeds 3x your average transaction size",
                action="If you don't recognize this transaction, contact your bank immediately.",
                action_label="Review Transaction",
            )
        )

    # ------------------------------------------------------------------
    # Financial stress meta-alert
    # ------------------------------------------------------------------
    if health.score < 40:
        alerts.append(
            AlertResponse(
                id=f"alert_{uuid.uuid4().hex[:8]}",
                type="stress",
                severity="high",
                title="Financial stress detected",
                description=(
                    "Your financial health score indicates significant stress. "
                    "Income may have dropped or obligations are high relative to earnings."
                ),
                evidence=f"Health score: {health.score}/100 | Savings rate: {cash_flow.savings_rate:.1f}%",
                action="Consider speaking with a financial counsellor to explore options.",
                action_label="Talk to Support",
            )
        )

    # Sort by severity priority
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda a: severity_order.get(a.severity, 4))

    return alerts
