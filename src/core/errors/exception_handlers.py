from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from src.core.errors.exceptions import DomainError, ErrorCategory, AirtouchConnectionError

logger = logging.getLogger("airtouch")

# Data-driven mapping from business error category to HTTP status code
HTTP_STATUS_MAP = {
    ErrorCategory.CONNECTION: 503,
    ErrorCategory.CONTROL: 400,
}


async def domain_error_handler(
    request: Request, exc: DomainError
) -> JSONResponse:
    """Unified handler that catches all subclasses of DomainError,

    routing them to HTTP status codes based on their category.
    """
    status_code = HTTP_STATUS_MAP.get(exc.category, 400)
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Converts a technical RequestValidationError into a clean, human-readable domain-level message."""
    errors = []
    for error in exc.errors():
        location = " -> ".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg", "invalid value")
        errors.append(f"{location}: {message}")

    return JSONResponse(
        status_code=400,
        content={"detail": f"Validation failed: {'; '.join(errors)}."},
    )


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Standardized fallback to handle unhandled runtime exceptions as a clean 500 error."""
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal system error occurred. Please verify your connection to the AirTouch console."
        },
    )
