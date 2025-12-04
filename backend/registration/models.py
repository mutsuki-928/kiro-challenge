"""Domain models for the registration system."""

from dataclasses import dataclass, field
from typing import List

from .exceptions import ValidationError


@dataclass
class User:
    """Represents a user in the registration system.
    
    Attributes:
        user_id: Unique identifier for the user
        name: User's name
    """
    user_id: str
    name: str
    
    def __post_init__(self):
        """Validate user data after initialization."""
        if not self.user_id or not self.user_id.strip():
            raise ValidationError("userId cannot be empty")
        if not self.name or not self.name.strip():
            raise ValidationError("name cannot be empty")


@dataclass
class Event:
    """Represents an event in the registration system.
    
    Attributes:
        event_id: Unique identifier for the event
        name: Event name
        capacity: Maximum number of registered users
        waitlist_enabled: Whether the event supports a waitlist
        registered_users: List of user_ids who are registered
        waitlist: List of user_ids on the waitlist (in order)
    """
    event_id: str
    name: str
    capacity: int
    waitlist_enabled: bool
    registered_users: List[str] = field(default_factory=list)
    waitlist: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate event data after initialization."""
        if self.capacity <= 0:
            raise ValidationError("capacity must be greater than zero")
    
    def is_full(self) -> bool:
        """Check if the event is at full capacity.
        
        Returns:
            True if the event has reached its capacity, False otherwise
        """
        return len(self.registered_users) >= self.capacity
    
    def has_available_capacity(self) -> bool:
        """Check if the event has available capacity.
        
        Returns:
            True if the event has not reached its capacity, False otherwise
        """
        return len(self.registered_users) < self.capacity
