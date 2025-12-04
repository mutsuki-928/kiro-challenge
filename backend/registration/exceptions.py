"""Custom exception classes for the registration system."""


class RegistrationError(Exception):
    """Base exception for registration system errors."""
    pass


class ValidationError(RegistrationError):
    """Raised when input validation fails."""
    pass


class DuplicateUserError(RegistrationError):
    """Raised when attempting to create a user with duplicate userId."""
    pass


class EventFullError(RegistrationError):
    """Raised when attempting to register for a full event without waitlist."""
    pass


class AlreadyRegisteredError(RegistrationError):
    """Raised when user attempts to register for event they're already registered for."""
    pass


class NotRegisteredError(RegistrationError):
    """Raised when user attempts to unregister from event they're not part of."""
    pass


class EntityNotFoundError(RegistrationError):
    """Raised when referenced user or event doesn't exist."""
    pass
