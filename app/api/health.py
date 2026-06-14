"""Health-check endpoint used by the frontend online indicator."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Return a minimal liveness response."""
    return {"status": "ok"}
