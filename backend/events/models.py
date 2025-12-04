"""Domain models for the event management system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .exceptions import InvalidEventDataError


@dataclass
class Event:
    """Represents an event in the event management system.
    
    Attributes:
        event_id: Unique identifier for the event
        title: Event title
        description: Event description
        date: Event date (ISO format string or YYYY-MM-DD)
        location: Event location
        capacity: Maximum number of attendees
        organizer: Event organizer name
        status: Event status (draft, published, cancelled, completed, active)
        created_at: Timestamp when event was created
        updated_at: Timestamp when event was last updated
    """
    event_id: str
    title: str
    description: str
    date: str
    location: str
    capacity: int
    organizer: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate event data after initialization."""
        # Validate title
        if not self.title or len(self.title) > 200:
            raise InvalidEventDataError("Title must be 1-200 characters")
        
        # Validate description
        if not self.description or len(self.description) > 2000:
            raise InvalidEventDataError("Description must be 1-2000 characters")
        
        # Validate date format
        try:
            datetime.fromisoformat(self.date.replace('Z', '+00:00'))
        except ValueError:
            try:
                datetime.strptime(self.date, '%Y-%m-%d')
            except ValueError:
                raise InvalidEventDataError("Invalid date format")
        
        # Validate location
        if not self.location or len(self.location) > 200:
            raise InvalidEventDataError("Location must be 1-200 characters")
        
        # Validate capacity
        if self.capacity <= 0 or self.capacity > 100000:
            raise InvalidEventDataError("Capacity must be between 1 and 100000")
        
        # Validate organizer
        if not self.organizer or len(self.organizer) > 200:
            raise InvalidEventDataError("Organizer must be 1-200 characters")
        
        # Validate status
        valid_statuses = ["draft", "published", "cancelled", "completed", "active"]
        if self.status not in valid_statuses:
            raise InvalidEventDataError(f"Status must be one of: {', '.join(valid_statuses)}")
