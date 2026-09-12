"""Simulator endpoints — EMI and goal projection."""

from fastapi import APIRouter

from app.schemas.simulator import (
    EMISimulatorInput,
    EMISimulatorOutput,
    GoalSimulatorInput,
    GoalSimulatorOutput,
)
from app.services.simulator import calculate_emi, project_goal

router = APIRouter(prefix="/api/v1/simulator", tags=["Simulator"])


@router.post("/emi", response_model=EMISimulatorOutput)
async def simulate_emi(input: EMISimulatorInput):
    """
    Calculate EMI, total interest, and assess affordability.

    Uses the standard reducing-balance EMI formula.
    Returns monthly EMI, total repayment, total interest,
    EMI-to-income ratio, new savings rate, and health impact.

    All input values are validated: loan amount > 0, rate 0-50%, tenure 1-360 months.
    """
    return calculate_emi(input)


@router.post("/goal", response_model=GoalSimulatorOutput)
async def simulate_goal(input: GoalSimulatorInput):
    """
    Project savings goal timeline with compound interest.

    Returns months to goal, total contributions, interest earned,
    and whether the goal is achievable within a reasonable timeframe.
    """
    return project_goal(input)
