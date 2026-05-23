from fastapi import APIRouter
from src.core.models import SystemHealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=SystemHealthResponse)
def get_health() -> SystemHealthResponse:
    """Retrieves the current application runtime health status.

    Returns:
        SystemHealthResponse: Fully modelled health status response.
    """
    return SystemHealthResponse(status="ok")
