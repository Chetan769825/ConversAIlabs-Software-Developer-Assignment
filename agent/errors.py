"""Agent-specific error types."""


class AgentError(RuntimeError):
    """Base class for expected agent failures."""


class SecurityError(AgentError):
    """Raised when a tool request violates a security boundary."""


class ProviderError(AgentError):
    """Raised for invalid or unavailable model responses."""


class ValidationFailure(AgentError):
    """Raised when repository validation does not pass."""
