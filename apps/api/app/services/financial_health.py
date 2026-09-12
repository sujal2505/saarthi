"""
Saarthi Finance — Financial Health Calculator.

Computes a transparent 0-100 score from 7 components:
1. Income stability
2. Savings rate
3. Expense-to-income ratio
4. EMI-to-income ratio
5. Repayment behavior
6. Emergency savings adequacy
7. Cash-flow consistency

Each component is individually scored 0-100 and weighted.
The overall score drives labels and explanations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from app.schemas.financial_health import HealthComponents, FinancialHealthResponse


# ---------------------------------------------------------------------------
# Weights (must sum to 1.0)
# ---------------------------------------------------------------------------
WEIGHTS = {
    "income_stability": 0.18,
    "savings": 0.18,
    "expense_management": 0.15,
    "debt_burden": 0.18,
    "repayment_behavior": 0.15,
    "liquidity": 0.16,
}


@dataclass
class CustomerFinancials:
    """Input data for health calculation."""
    monthly_income: float
    monthly_expenses: float
    monthly_emi: float
    monthly_savings: float  # income - expenses - emi
    income_stability: str  # "stable" | "variable" | "declining"
    emergency_fund: float
    missed_emi_count: int = 0
    total_emi_count: int = 12
    income_variance_pct: float = 5.0  # month-to-month variance
    prev_month_expenses: float = 0.0
    prev_health_score: float = 0.0  # for change computation


def _score_income_stability(cf: CustomerFinancials) -> float:
    """Score income stability: stable income → high score."""
    base = {"stable": 85, "variable": 55, "declining": 30}.get(cf.income_stability, 50)
    # Adjust by variance: lower variance → higher score
    if cf.income_variance_pct < 5:
        base = min(100, base + 10)
    elif cf.income_variance_pct > 20:
        base = max(0, base - 15)
    return float(base)


def _score_savings(cf: CustomerFinancials) -> float:
    """Score savings rate: 25%+ is excellent, <5% is poor."""
    if cf.monthly_income <= 0:
        return 0.0
    rate = (cf.monthly_savings / cf.monthly_income) * 100
    if rate >= 30:
        return 95.0
    elif rate >= 25:
        return 85.0
    elif rate >= 20:
        return 75.0
    elif rate >= 15:
        return 65.0
    elif rate >= 10:
        return 50.0
    elif rate >= 5:
        return 35.0
    elif rate >= 0:
        return 20.0
    else:
        return max(0, 10 + rate)  # negative savings


def _score_expense_management(cf: CustomerFinancials) -> float:
    """Score expense-to-income ratio: lower is better."""
    if cf.monthly_income <= 0:
        return 0.0
    ratio = cf.monthly_expenses / cf.monthly_income
    if ratio <= 0.40:
        return 90.0
    elif ratio <= 0.50:
        return 80.0
    elif ratio <= 0.60:
        return 70.0
    elif ratio <= 0.70:
        return 55.0
    elif ratio <= 0.80:
        return 35.0
    else:
        return max(0, 20 - (ratio - 0.80) * 100)


def _score_debt_burden(cf: CustomerFinancials) -> float:
    """Score EMI-to-income ratio: <20% excellent, >50% critical."""
    if cf.monthly_income <= 0:
        return 0.0
    ratio = cf.monthly_emi / cf.monthly_income
    if ratio <= 0.10:
        return 95.0
    elif ratio <= 0.20:
        return 85.0
    elif ratio <= 0.30:
        return 75.0
    elif ratio <= 0.40:
        return 55.0
    elif ratio <= 0.50:
        return 35.0
    else:
        return max(0, 20 - (ratio - 0.50) * 100)


def _score_repayment_behavior(cf: CustomerFinancials) -> float:
    """Score repayment: no missed payments → high score."""
    if cf.total_emi_count <= 0:
        return 80.0  # no EMI history defaults to decent
    miss_rate = cf.missed_emi_count / cf.total_emi_count
    if miss_rate == 0:
        return 95.0
    elif miss_rate <= 0.05:
        return 80.0
    elif miss_rate <= 0.10:
        return 60.0
    elif miss_rate <= 0.20:
        return 40.0
    else:
        return max(0, 25 - miss_rate * 100)


def _score_liquidity(cf: CustomerFinancials) -> float:
    """Score emergency fund adequacy: 6+ months expenses = excellent."""
    if cf.monthly_expenses <= 0:
        return 50.0
    months_covered = cf.emergency_fund / cf.monthly_expenses
    if months_covered >= 6:
        return 95.0
    elif months_covered >= 3:
        return 75.0
    elif months_covered >= 1.5:
        return 55.0
    elif months_covered >= 0.5:
        return 35.0
    else:
        return 15.0


def _get_label(score: float) -> str:
    """Map score to human-readable label."""
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 50:
        return "Stable"
    elif score >= 35:
        return "Fair"
    else:
        return "Poor"


def _identify_factors(cf: CustomerFinancials, components: HealthComponents) -> Tuple[List[str], List[str]]:
    """Identify positive and risk factors from component scores."""
    positive: List[str] = []
    risk: List[str] = []

    # Income stability
    if components.income_stability >= 75:
        positive.append("Income has remained stable for the last six months")
    elif components.income_stability < 45:
        risk.append("Income has been variable or declining recently")

    # Savings
    savings_rate = (cf.monthly_savings / cf.monthly_income * 100) if cf.monthly_income > 0 else 0
    if savings_rate >= 20:
        positive.append(f"Savings rate is above the recommended minimum ({savings_rate:.1f}%)")
    elif savings_rate < 10:
        risk.append(f"Savings rate is below 10% ({savings_rate:.1f}%)")

    # Expense management
    if cf.prev_month_expenses > 0 and cf.monthly_expenses > cf.prev_month_expenses * 1.05:
        change_pct = ((cf.monthly_expenses - cf.prev_month_expenses) / cf.prev_month_expenses) * 100
        risk.append(f"Household expenses have increased by {change_pct:.0f}% recently")

    # Debt
    if cf.monthly_income > 0:
        emi_ratio = cf.monthly_emi / cf.monthly_income
        if emi_ratio < 0.20:
            positive.append("EMI burden is well within safe limits")
        elif emi_ratio > 0.40:
            risk.append("EMI-to-income ratio exceeds safe threshold (40%)")

    # Repayment
    if cf.missed_emi_count == 0 and cf.total_emi_count > 0:
        positive.append("EMI repayments are consistent with no missed payments")
    elif cf.missed_emi_count > 0:
        risk.append(f"Missed {cf.missed_emi_count} EMI payment(s) in recent history")

    # Liquidity
    if cf.monthly_expenses > 0:
        months_covered = cf.emergency_fund / cf.monthly_expenses
        if months_covered < 3:
            risk.append(f"Emergency fund covers only {months_covered:.1f} months of expenses")
        elif months_covered >= 6:
            positive.append("Emergency fund is strong (6+ months coverage)")

    return positive, risk


def _build_explanation(score: float, label: str, positive: List[str], risk: List[str], cf: CustomerFinancials) -> str:
    """Generate a plain-language explanation."""
    savings_rate = (cf.monthly_savings / cf.monthly_income * 100) if cf.monthly_income > 0 else 0

    parts: List[str] = []
    parts.append(f"Your financial health is {label.lower()}.")

    if positive:
        parts.append(f"You have {positive[0].lower()}.")

    if risk:
        parts.append(f"However, {risk[0][0].lower()}{risk[0][1:]}.")

    if savings_rate > 20:
        parts.append(f"Your savings rate of {savings_rate:.1f}% is healthy.")
    elif savings_rate > 0:
        parts.append(f"Your savings rate of {savings_rate:.1f}% could be improved.")

    return " ".join(parts)


def calculate_financial_health(cf: CustomerFinancials) -> FinancialHealthResponse:
    """
    Calculate the full financial health assessment.

    Returns a FinancialHealthResponse with score, label, components,
    positive/risk factors, and plain-language explanation.
    """
    components = HealthComponents(
        income_stability=round(_score_income_stability(cf), 1),
        savings=round(_score_savings(cf), 1),
        expense_management=round(_score_expense_management(cf), 1),
        debt_burden=round(_score_debt_burden(cf), 1),
        repayment_behavior=round(_score_repayment_behavior(cf), 1),
        liquidity=round(_score_liquidity(cf), 1),
    )

    # Weighted score
    score = (
        components.income_stability * WEIGHTS["income_stability"]
        + components.savings * WEIGHTS["savings"]
        + components.expense_management * WEIGHTS["expense_management"]
        + components.debt_burden * WEIGHTS["debt_burden"]
        + components.repayment_behavior * WEIGHTS["repayment_behavior"]
        + components.liquidity * WEIGHTS["liquidity"]
    )
    score = round(score, 1)

    label = _get_label(score)
    positive, risk = _identify_factors(cf, components)
    explanation = _build_explanation(score, label, positive, risk, cf)
    change = round(score - cf.prev_health_score, 1) if cf.prev_health_score else 0.0

    return FinancialHealthResponse(
        score=score,
        label=label,
        change=change,
        components=components,
        positive_factors=positive,
        risk_factors=risk,
        explanation=explanation,
    )
