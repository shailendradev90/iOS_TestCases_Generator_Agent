"""Custom exceptions for the iOS Test Generator Agent."""

from __future__ import annotations


class AgentError(Exception):
    """Base exception for all agent errors."""

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional additional details about the error
        """
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation."""
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class ConfigurationError(AgentError):
    """Raised when there's a configuration error."""

    pass


class ProjectNotFoundError(AgentError):
    """Raised when the specified project path doesn't exist."""

    pass


class InvalidProjectError(AgentError):
    """Raised when the project structure is invalid."""

    pass


class ParsingError(AgentError):
    """Raised when Swift code parsing fails."""

    pass


class LLMError(AgentError):
    """Raised when LLM API calls fail."""

    pass


class APIKeyError(AgentError):
    """Raised when API key is missing or invalid."""

    def __init__(self, provider: str) -> None:
        """Initialize API key error.

        Args:
            provider: The LLM provider name (openai, anthropic, groq)
        """
        message = (
            f"API key for {provider} is not configured. "
            f"Please set the {provider.upper()}_API_KEY environment variable."
        )
        super().__init__(message)
        self.provider = provider


class RateLimitError(LLMError):
    """Raised when API rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: int | None = None) -> None:
        """Initialize rate limit error.

        Args:
            provider: The LLM provider name
            retry_after: Optional seconds to wait before retrying
        """
        message = f"Rate limit exceeded for {provider}"
        if retry_after:
            message += f". Retry after {retry_after} seconds."
        super().__init__(message)
        self.provider = provider
        self.retry_after = retry_after


class TestGenerationError(AgentError):
    """Raised when test generation fails."""

    pass


class FileWriteError(AgentError):
    """Raised when writing test files fails."""

    pass


class ValidationError(AgentError):
    """Raised when input validation fails."""

    pass

# Made with Bob
