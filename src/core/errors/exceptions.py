from enum import StrEnum


class ErrorCategory(StrEnum):
    """Business categories of domain errors."""
    CONNECTION = "CONNECTION"
    CONTROL = "CONTROL"


class DomainError(Exception):
    """Base class for all domain-level business errors."""
    def __init__(self, message: str, category: ErrorCategory) -> None:
        super().__init__(message)
        self.message = message
        self.category = category


class AirtouchConnectionError(DomainError):
    """Exception raised when connection to the AirTouch console fails."""
    def __init__(self, device_handle: str) -> None:
        super().__init__(
            message=f"Could not connect to Airtouch console at {device_handle}",
            category=ErrorCategory.CONNECTION,
        )
        self.device_handle = device_handle
