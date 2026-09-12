"""
Saarthi Finance — AI Assistant Service.

Deterministic bilingual (EN/HI) response templates grounded in customer ML data.
If an LLM API key is configured, it can be extended to use an LLM.

Rules:
- Explain insights simply
- Ground in the active customer's actual ML health score and cash flow
- Never pretend to be a bank employee
- Never claim guaranteed approval
- Avoid investment/lending certainty
- Support English and Hindi accurately
- Include disclaimer when discussing loans
"""

from __future__ import annotations

from typing import Optional

from app.schemas.assistant import ChatRequest, ChatResponse
from app.schemas.cash_flow import CashFlowResponse
from app.schemas.financial_health import FinancialHealthResponse
from app.config import settings


DISCLAIMER_EN = "\n\n*Disclaimer: This is AI-generated financial guidance, not professional advice or a loan approval.*"
DISCLAIMER_HI = "\n\n*Disclaimer: Yeh AI-dwara generated financial guidance hai, professional advice ya loan approval nahi.*"


def generate_response(
    request: ChatRequest,
    health: Optional[FinancialHealthResponse] = None,
    cash_flow: Optional[CashFlowResponse] = None,
    customer_name: str = "Customer",
    full_name: str = "",
    is_suppressed: bool = False,
    suppression_reason: Optional[str] = None,
) -> ChatResponse:
    """Generate an assistant response grounded in customer financial data."""
    if settings.llm_api_key:
        pass

    msg = request.message.lower().strip()
    lang = request.language

    # Language determination: if user explicitly selected hi, or typed devanagari / hindi words
    is_hindi = (
        lang == "hi" or
        any(w in msg for w in ["kya", "kaise", "mera", "meri", "bachat", "kharcha", "karj", "paisa", "chahiye", "batao"])
    )

    # Extract data for templates
    score = health.score if health else 70
    label = health.label if health else "Stable"
    income = cash_flow.monthly_income if cash_flow else 0
    expenses = cash_flow.monthly_expenses if cash_flow else 0
    emi = cash_flow.monthly_emi if cash_flow else 0
    savings = cash_flow.monthly_savings if cash_flow else 0
    savings_rate = cash_flow.savings_rate if cash_flow else 0
    emi_ratio = (emi / income * 100) if income > 0 else 0

    reply = _match_template(
        msg=msg,
        is_hindi=is_hindi,
        name=customer_name,
        score=score,
        label=label,
        income=income,
        expenses=expenses,
        emi=emi,
        savings=savings,
        savings_rate=savings_rate,
        emi_ratio=emi_ratio,
        is_suppressed=is_suppressed,
        suppression_reason=suppression_reason,
    )

    return ChatResponse(
        reply=reply,
        language="hi" if is_hindi else "en",
    )


def _match_template(
    msg: str,
    is_hindi: bool,
    name: str,
    score: float,
    label: str,
    income: float,
    expenses: float,
    emi: float,
    savings: float,
    savings_rate: float,
    emi_ratio: float,
    is_suppressed: bool = False,
    suppression_reason: Optional[str] = None,
) -> str:
    """Match user message to the best template response."""
    disclaimer = DISCLAIMER_HI if is_hindi else DISCLAIMER_EN

    # ---- Loan / Borrowing ----
    if any(w in msg for w in ["loan", "lena", "borrow", "udhar", "karj", "credit"]):
        if is_suppressed or score < 45 or emi_ratio > 40:
            if is_hindi:
                reason = suppression_reason or "Aapka EMI burden zyada hai aur overdue obligations par dhyan dena zaroori hai."
                return (
                    f"{name} ji, aapka financial health score abhi {score:.0f}/100 ({label}) hai. "
                    f"Aapke aarthik hit ke liye, naye loan ke sujhav abhi suppress kiye gaye hain. "
                    f"Karan: {reason} "
                    f"Is samay naya karz lene se bachein aur debt restructuring ya emergency buffer par dhyan dein."
                    f"{disclaimer}"
                )
            reason = suppression_reason or f"Your EMI burden is {emi_ratio:.1f}% of your income."
            return (
                f"{name}, your financial health score is {score:.0f}/100 ({label}). "
                f"Under our responsible lending safeguards, new loan recommendations are suppressed to protect your finances. "
                f"Reason: {reason} "
                f"We recommend speaking with a certified financial counsellor to restructure debt rather than taking new credit."
                f"{disclaimer}"
            )
        else:
            if is_hindi:
                return (
                    f"{name} ji, aapka financial health score abhi {score:.0f}/100 ({label}) hai, jo ki stable hai. "
                    f"Aapka EMI burden abhi {emi_ratio:.1f}% hai (safe limit: 40% se kam). "
                    f"Aap ek safe borrowing range explore kar sakte hain, lekin simulator mein check zaroor karein ki naye EMI se aapka savings rate prabhavit na ho."
                    f"{disclaimer}"
                )
            return (
                f"{name}, your financial health score is {score:.0f}/100 ({label}). "
                f"Your current EMI burden is {emi_ratio:.1f}% of your income (safe threshold: below 40%). "
                f"You are eligible for safe borrowing guidance. We recommend using our Borrowing Simulator to test whether the new EMI fits comfortably within your monthly budget."
                f"{disclaimer}"
            )

    # ---- Savings ----
    if any(w in msg for w in ["savings", "bachat", "save", "jama"]):
        if is_hindi:
            return (
                f"{name} ji, aapki monthly savings lagbhag ₹{savings:,.0f} hai, jo ki {savings_rate:.1f}% savings rate hai. "
                f"{'Yeh recommended level se upar hai — shandar discipline!' if savings_rate >= 20 else 'Isse badhakar kam se kam 20% tak le jaane ka prayas karein.'} "
                f"Aap hamare Goals section mein jaakar naya savings target set kar sakte hain."
            )
        return (
            f"{name}, you are currently saving approximately ₹{savings:,.0f}/month, representing a {savings_rate:.1f}% savings rate. "
            f"{'This is healthy and above the recommended 20% threshold!' if savings_rate >= 20 else 'We recommend aiming for at least 20% to build your financial resilience.'} "
            f"You can set up and track automatic savings milestones in the Goal Planning tab."
        )

    # ---- EMI / Repayment ----
    if any(w in msg for w in ["emi", "repay", "kist"]):
        if is_hindi:
            return (
                f"{name} ji, aapka current EMI ₹{emi:,.0f}/month hai, jo monthly income (₹{income:,.0f}) ka {emi_ratio:.1f}% hai. "
                f"{'Yeh safe zone mein hai (40% se kam).' if emi_ratio < 40 else 'Yeh safe limit (40%) se zyada hai, naye debt se bachein.'}"
            )
        return (
            f"{name}, your existing monthly EMI obligation is ₹{emi:,.0f}/month, which is {emi_ratio:.1f}% of your monthly income (₹{income:,.0f}). "
            f"{'This is well within safe limits (below 40%).' if emi_ratio < 40 else 'This exceeds the safe 40% threshold — avoid taking additional debt.'}"
        )

    # ---- Expenses / Spending ----
    if any(w in msg for w in ["kharcha", "expense", "spend", "kharch"]):
        exp_pct = (expenses / income * 100) if income > 0 else 0
        if is_hindi:
            return (
                f"{name} ji, aapka ausat monthly kharcha ₹{expenses:,.0f} hai, jo income ka {exp_pct:.0f}% hai. "
                f"Spending Analysis page par jakar aap category-wise breakdown dekh sakte hain."
            )
        return (
            f"{name}, your average monthly expenditure is ₹{expenses:,.0f}, which is {exp_pct:.0f}% of your income. "
            f"Visit the Spending Analysis tab to see a detailed category breakdown."
        )

    # ---- General greeting / fallback ----
    if is_hindi:
        return (
            f"Namaste {name} ji! Main Saarthi hoon — aapka personal financial guide. "
            f"Aapka financial health score abhi {score:.0f}/100 ({label}) hai. "
            f"Aap mujhse apne kharche, savings, EMI burden, ya safe borrowing ke baare mein pooch sakte hain."
            f"{disclaimer}"
        )
    return (
        f"Hello {name}! I am Saarthi, your personal financial guide. "
        f"Your current financial health score is {score:.0f}/100 ({label}). "
        f"Feel free to ask about your spending patterns, savings goals, EMI burden, or safe borrowing guidance."
        f"{disclaimer}"
    )
