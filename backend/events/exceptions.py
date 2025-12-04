"""Custom exception classes for the event management system."""


class EventError(Exception):
    """Base exception for event-related errors."""
    pass


class DuplicateEventError(EventError):
    """Raised when attempting to create an event with duplicate ID."""
    pass


class EventNotFoundError(EventError):
    """Raised when an event is not found."""
    pass


class InvalidEventDataError(EventError):
    """Raised when event data is invalid."""
    pass
