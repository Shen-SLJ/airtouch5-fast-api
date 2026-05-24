from enum import StrEnum
from pydantic import BaseModel


class HealthStatus(StrEnum):
    """Possible health states of the application."""
    OK = "ok"
    DEGRADED = "degraded"


class SystemHealthResponse(BaseModel):
    """Health check response containing application runtime status."""
    status: HealthStatus
