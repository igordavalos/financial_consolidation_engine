"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "service": "Financial Consolidation Engine",
        "version": "0.1.0",
    }
