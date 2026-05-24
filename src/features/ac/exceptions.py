from src.core.errors.exceptions import DomainError, ErrorCategory


class AcControlError(DomainError):
    """Exception raised when a control command to the AirTouch AC unit fails validation or execution."""

    def __init__(self, message: str) -> None:
        super().__init__(message, category=ErrorCategory.CONTROL)
