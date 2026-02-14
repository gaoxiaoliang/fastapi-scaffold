"""Custom exception hierarchy for API errors."""

from typing import Any


class AppError(Exception):
    """Base application exception with standard metadata."""

    def __init__(
        self,
        message: str,
        *,
        code: str,
        status_code: int,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ClientError(AppError):
    """Exception for 4xx client-originated errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "CLIENT_ERROR",
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, status_code=status_code, details=details)


class ServerError(AppError):
    """Exception for 5xx server-side errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        *,
        code: str = "SERVER_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code, status_code=status_code, details=details)
