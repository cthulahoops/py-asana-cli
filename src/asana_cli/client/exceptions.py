"""Exceptions for Asana API client."""


class AsanaAPIError(Exception):
    """Base exception for Asana API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AsanaAPIError):
    """Raised when authentication fails."""

    pass


class NotFoundError(AsanaAPIError):
    """Raised when a resource is not found."""

    pass


class RateLimitError(AsanaAPIError):
    """Raised when rate limit is exceeded."""

    pass


class ValidationError(AsanaAPIError):
    """Raised when request validation fails."""

    pass


class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""

    pass
