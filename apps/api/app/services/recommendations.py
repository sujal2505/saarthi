"""
Saarthi Finance — Recommendation Engine.

Responsible lending rules:
1. If financial_health.score < 45 → suppress loan recs, suggest counselling
2. If emi_to_income_ratio > 0.40 → suppress new loans, suggest restructuring
3. If savings_rate < 10% → prioritize savings recommendations
4. Every borrowing rec includes affordability explanation
5. Never recommend based on revenue — only customer benefit
6. human_review_required = True for stressed customers

This is decision support only. The platform never claims to approve or reject a loan.
"""

from __future__ import annotations

from typing import List

from app.schemas.recommendation import RecommendationResponse
from app.schemas.financial_health import FinancialHealthResponse
from app.schemas.cash_flow import CashFlowResponse


def generate_recommendations(
    health: FinancialHealthResponse,
    cash_flow: CashFlowResponse,
    existing_goals: int = 0,
) -> RecommendationResponse:
    """
    Generate the primary recommendation for a customer.

    Core principle: This is responsible financial guidance.
    Recommendations are decision support only — never automatic approval.
    """
    score = health.score
    savings_rate = cash_flow.savings_rate
    emi_ratio = (cash_flow.monthly_emi / cash_flow.monthly_income * 100) if cash_flow.monthly_income > 0 else 100

    # ------------------------------------------------------------------
    # RULE 1: High financial stress → suppress loans, suggest counselling
    # ------------------------------------------------------------------
    if score < 45:
        return RecommendationResponse(
            type="restructure",
            title="Focus on stabilizing before borrowing",
            product="Financial Counselling Support",
            recommended_amount=0,
            confidence=0.95,
            why=[
                "New debt would increase stress significantly",
                "Income instability makes repayments unpredictable",
                "Current EMI burden is already at risk level",
            ],
            warning="A loan recommendation is not suitable at this time. "
                    "Saarthi recommends speaking with a financial counsellor.",
            human_review_required=True,
            suppressed=True,
            suppression_reason="High financial stress detected. Loan offers suppressed to protect customer.",
        )

    # ------------------------------------------------------------------
    # RULE 2: EMI burden too high → recommend restructuring
    # ------------------------------------------------------------------
    if emi_ratio > 40:
        return RecommendationResponse(
            type="restructure",
            title="Consider restructuring existing EMIs",
            product="EMI Restructuring Review",
            recommended_amount=0,
            confidence=0.88,
            why=[
                f"Current EMI-to-income ratio is {emi_ratio:.1f}% (safe: below 40%)",
                "Adding more debt would strain finances significantly",
                "Restructuring existing loans may reduce monthly burden",
            ],
            warning="This is guidance only. Please consult your bank for restructuring options.",
            human_review_required=True,
            suppressed=True,
            suppression_reason="EMI burden exceeds safe threshold. New loan offers suppressed.",
        )

    # ------------------------------------------------------------------
    # RULE 3: Low savings rate → prioritize savings
    # ------------------------------------------------------------------
    if savings_rate < 10:
        suggested = max(1000, round(cash_flow.monthly_income * 0.05, -2))
        return RecommendationResponse(
            type="savings",
            title="Boost your savings rate first",
            product="Automated Savings Plan",
            recommended_amount=suggested,
            confidence=0.87,
            why=[
                f"Your savings rate of {savings_rate:.1f}% is below the recommended 20%",
                "Building savings creates a financial cushion",
                "Automated transfers help maintain discipline",
            ],
            warning="This is financial guidance, not a product guarantee. "
                    "Please review with your financial advisor.",
            human_review_required=False,
            suppressed=False,
        )

    # ------------------------------------------------------------------
    # Healthy customer: recommend based on context
    # ------------------------------------------------------------------
    emergency_months = 0
    if cash_flow.monthly_expenses > 0:
        # We don't have emergency_fund here directly, estimate from savings
        # For a stable customer, primary recommendation: build emergency buffer
        pass

    # If savings rate is healthy, recommend building emergency fund
    if savings_rate >= 20:
        suggested = max(3000, round(cash_flow.monthly_savings * 0.3, -2))
        return RecommendationResponse(
            type="savings",
            title="Build a stronger emergency buffer",
            product="Emergency Savings Plan",
            recommended_amount=suggested,
            confidence=0.91,
            why=[
                "Your income is stable and predictable",
                f"Your savings rate is currently healthy at {savings_rate:.1f}%",
                "Household expenses have been rising — a buffer protects you",
                "A strong emergency fund is the foundation of financial health",
            ],
            warning="This is financial guidance, not a loan approval or financial product guarantee. "
                    "Please consult a certified financial advisor before making major decisions.",
            human_review_required=False,
            suppressed=False,
        )

    # Moderate savings → insurance recommendation
    if savings_rate >= 15:
        return RecommendationResponse(
            type="insurance",
            title="Consider term life insurance",
            product="Term Insurance Plan",
            recommended_amount=round(cash_flow.monthly_income * 12 * 10, -3),  # 10x annual income
            estimated_emi=round(cash_flow.monthly_income * 0.02),
            confidence=0.78,
            why=[
                "Your finances are stable enough to afford protection",
                "Term insurance provides family security at low cost",
                f"Recommended coverage: ~{round(cash_flow.monthly_income * 120, -5):,.0f}",
            ],
            warning="This is guidance only. Insurance needs vary — consult an insurance advisor.",
            human_review_required=False,
            suppressed=False,
        )

    # Default: savings focus
    suggested = max(2000, round(cash_flow.monthly_income * 0.10, -2))
    return RecommendationResponse(
        type="savings",
        title="Start a systematic savings plan",
        product="Recurring Deposit",
        recommended_amount=suggested,
        confidence=0.82,
        why=[
            f"Your current savings rate is {savings_rate:.1f}%",
            "Regular savings builds a strong financial foundation",
            "A recurring deposit provides guaranteed returns",
        ],
        warning="This is financial guidance, not a product guarantee.",
        human_review_required=False,
        suppressed=False,
    )
