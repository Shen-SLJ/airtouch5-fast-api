from src.core.errors.exceptions import DomainError, ErrorCategory


class ZoneControlError(DomainError):
    """Exception raised when a control command to the AirTouch zone unit fails validation or execution."""

    def __init__(self, message: str) -> None:
        super().__init__(message, category=ErrorCategory.CONTROL)
