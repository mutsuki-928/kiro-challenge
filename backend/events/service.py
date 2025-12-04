"""Service layer for event management business logic."""

import uuid
from typing import Any, Dict, List, Optional

from .exceptions import EventNotFoundError, InvalidEventDataError
from .models import Event
from .repositories import EventRepository


class EventService:
    """Service for managing events."""
    
    def __init__(self, event_repo: EventRepository):
        """Initialize with repository.
        
        Args:
            event_repo: EventRepository instance for data access
        """
        self.event_repo = event_repo
    
    def create_event(self, event_data: Dict[str, Any]) -> Event:
        """Create a new event with validation.
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            The created Event
            
        Raises:
            InvalidEventDataError: If event data is invalid
        """
        # Generate event_id if not provided
        event_id = event_data.get('event_id') or event_data.get('eventId') or str(uuid.uuid4())
        
        try:
            # Create Event domain model (validation happens in __post_init__)
            event = Event(
                event_id=event_id,
                title=event_data['title'],
                description=event_data['description'],
                date=event_data['date'],
                location=event_data['location'],
                capacity=event_data['capacity'],
                organizer=event_data['organizer'],
                status=event_data['status']
            )
        except KeyError as e:
            raise InvalidEventDataError(f"Missing required field: {e}")
        except InvalidEventDataError:
            # Re-raise validation errors from Event model
            raise
        
        # Persist to database
        return self.event_repo.create(event)
    
    def get_event(self, event_id: str) -> Event:
        """Get an event by ID.
        
        Args:
            event_id: Unique identifier for the event
            
        Returns:
            The Event
            
        Raises:
            EventNotFoundError: If the event doesn't exist
        """
        event = self.event_repo.get(event_id)
        if event is None:
            raise EventNotFoundError(f"Event with ID {event_id} not found")
        return event
    
    def list_events(self, status: Optional[str] = None) -> List[Event]:
        """List events with optional filtering.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of Event objects
        """
        return self.event_repo.list(status=status)
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Event:
        """Update an event with validation.
        
        Args:
            event_id: Unique identifier for the event
            updates: Dictionary of fields to update
            
        Returns:
            The updated Event
            
        Raises:
            EventNotFoundError: If the event doesn't exist
            InvalidEventDataError: If update data is invalid
        """
        # Check if event exists
        existing_event = self.event_repo.get(event_id)
        if existing_event is None:
            raise EventNotFoundError(f"Event with ID {event_id} not found")
        
        # Validate updates by creating a new Event with merged data
        # This ensures all validation rules are applied
        merged_data = {
            'event_id': existing_event.event_id,
            'title': updates.get('title', existing_event.title),
            'description': updates.get('description', existing_event.description),
            'date': updates.get('date', existing_event.date),
            'location': updates.get('location', existing_event.location),
            'capacity': updates.get('capacity', existing_event.capacity),
            'organizer': updates.get('organizer', existing_event.organizer),
            'status': updates.get('status', existing_event.status),
            'created_at': existing_event.created_at,
            'updated_at': existing_event.updated_at
        }
        
        try:
            # Validate by creating Event instance
            Event(**merged_data)
        except InvalidEventDataError:
            # Re-raise validation errors
            raise
        
        # Perform update
        return self.event_repo.update(event_id, updates)
    
    def delete_event(self, event_id: str) -> None:
        """Delete an event.
        
        Args:
            event_id: Unique identifier for the event
            
        Raises:
            EventNotFoundError: If the event doesn't exist
        """
        self.event_repo.delete(event_id)
