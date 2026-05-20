#==========================#
# EXCEPTIONS SCRIPT
#==========================#


class AppError(Exception):
    """Base exception for application-level errors."""


class AppValidationError(AppError, ValueError):
    """Raised when application input fails domain validation."""


class ConfigurationError(AppValidationError):
    """Raised when application configuration is missing or invalid."""


class UnsupportedMessageTypeError(AppValidationError):
    """Raised when an inbound webhook message type is unsupported."""


class EmptyMessageError(AppValidationError):
    """Raised when an inbound webhook message has no usable content."""
