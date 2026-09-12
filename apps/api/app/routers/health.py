"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Application health check.

    Returns service status and version information.
    """
    return {
        "status": "healthy",
        "service": "saarthi-api",
        "version": "0.1.0",
        "disclaimer": (
            "Saarthi Finance is a decision-support platform. "
            "It does not approve or reject loans. "
            "All recommendations are guidance only."
        ),
    }
