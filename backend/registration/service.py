"""Service layer for registration business logic."""

from dataclasses import dataclass
from typing import List, Optional

from .models import User, Event
from .repositories import UserRepository, EventRepository
from .exceptions import (
    DuplicateUserError,
    EntityNotFoundError,
    EventFullError,
    AlreadyRegisteredError,
    NotRegisteredError
)


@dataclass
class RegistrationResult:
    """Result of a registration attempt.
    
    Attributes:
        status: Status of the registration ("registered", "waitlisted", or "denied")
        message: Human-readable message describing the result
    """
    status: str
    message: str


class RegistrationService:
    """Service for managing user registrations and events."""
    
    def __init__(self, user_repo: UserRepository, event_repo: EventRepository):
        """Initialize the service with repositories.
        
        Args:
            user_repo: Repository for user data access
            event_repo: Repository for event data access
        """
        self.user_repo = user_repo
        self.event_repo = event_repo
    
    def create_user(self, user_id: str, name: str) -> User:
        """Create a new user.
        
        Args:
            user_id: Unique identifier for the user
            name: User's name
            
        Returns:
            The created User object
            
        Raises:
            DuplicateUserError: If a user with the given ID already exists
            ValidationError: If user_id or name are invalid
        """
        # Check for duplicate
        if self.user_repo.exists(user_id):
            raise DuplicateUserError(f"User with ID {user_id} already exists")
        
        # Create user (validation happens in User.__post_init__)
        user = User(user_id=user_id, name=name)
        return self.user_repo.create(user)
    
    def create_event(self, event_id: str, name: str, capacity: int, waitlist_enabled: bool) -> Event:
        """Create a new event.
        
        Args:
            event_id: Unique identifier for the event
            name: Event name
            capacity: Maximum number of registered users
            waitlist_enabled: Whether the event supports a waitlist
            
        Returns:
            The created Event object
            
        Raises:
            ValidationError: If capacity is invalid
        """
        # Create event (validation happens in Event.__post_init__)
        event = Event(
            event_id=event_id,
            name=name,
            capacity=capacity,
            waitlist_enabled=waitlist_enabled
        )
        return self.event_repo.create(event)
    
    def register_user(self, user_id: str, event_id: str) -> RegistrationResult:
        """Register a user for an event.
        
        Args:
            user_id: ID of the user to register
            event_id: ID of the event to register for
            
        Returns:
            RegistrationResult indicating the outcome
            
        Raises:
            EntityNotFoundError: If user or event doesn't exist
            AlreadyRegisteredError: If user is already registered or waitlisted
        """
        # Verify user exists
        if not self.user_repo.exists(user_id):
            raise EntityNotFoundError(f"User {user_id} not found")
        
        # Get event
        event = self.event_repo.get(event_id)
        if event is None:
            raise EntityNotFoundError(f"Event {event_id} not found")
        
        # Check if already registered
        if user_id in event.registered_users:
            raise AlreadyRegisteredError(f"User {user_id} is already registered for event {event_id}")
        
        # Check if already on waitlist
        if user_id in event.waitlist:
            raise AlreadyRegisteredError(f"User {user_id} is already on the waitlist for event {event_id}")
        
        # Check capacity
        if event.has_available_capacity():
            # Add to registered users
            event.registered_users.append(user_id)
            self.event_repo._add_registration(event_id, user_id)
            self.event_repo.update(event)
            return RegistrationResult(
                status="registered",
                message=f"User {user_id} successfully registered for event {event_id}"
            )
        elif event.waitlist_enabled:
            # Add to waitlist
            event.waitlist.append(user_id)
            self.event_repo._add_to_waitlist(event_id, user_id, len(event.waitlist) - 1)
            self.event_repo.update(event)
            return RegistrationResult(
                status="waitlisted",
                message=f"Event is full. User {user_id} added to waitlist for event {event_id}"
            )
        else:
            # Event is full and no waitlist
            raise EventFullError(f"Event {event_id} is full and does not have a waitlist")
    
    def unregister_user(self, user_id: str, event_id: str) -> None:
        """Unregister a user from an event.
        
        Args:
            user_id: ID of the user to unregister
            event_id: ID of the event to unregister from
            
        Raises:
            EntityNotFoundError: If event doesn't exist
            NotRegisteredError: If user is not registered or waitlisted
        """
        # Get event
        event = self.event_repo.get(event_id)
        if event is None:
            raise EntityNotFoundError(f"Event {event_id} not found")
        
        # Check if user is registered
        if user_id in event.registered_users:
            event.registered_users.remove(user_id)
            self.event_repo._remove_registration(event_id, user_id)
            
            # Promote from waitlist if available
            if event.waitlist:
                promoted_user_id = event.waitlist.pop(0)
                event.registered_users.append(promoted_user_id)
                
                # Remove from waitlist and add to registered
                self.event_repo._remove_from_waitlist(event_id, promoted_user_id)
                self.event_repo._add_registration(event_id, promoted_user_id)
                
                # Reindex remaining waitlist
                for i, remaining_user_id in enumerate(event.waitlist):
                    self.event_repo._remove_from_waitlist(event_id, remaining_user_id)
                    self.event_repo._add_to_waitlist(event_id, remaining_user_id, i)
            
            self.event_repo.update(event)
            return
        
        # Check if user is on waitlist
        if user_id in event.waitlist:
            event.waitlist.remove(user_id)
            self.event_repo._remove_from_waitlist(event_id, user_id)
            
            # Reindex remaining waitlist
            for i, remaining_user_id in enumerate(event.waitlist):
                self.event_repo._remove_from_waitlist(event_id, remaining_user_id)
                self.event_repo._add_to_waitlist(event_id, remaining_user_id, i)
            
            self.event_repo.update(event)
            return
        
        # User is not registered or waitlisted
        raise NotRegisteredError(f"User {user_id} is not registered or waitlisted for event {event_id}")
    
    def get_user_registrations(self, user_id: str) -> List[Event]:
        """Get all events a user is registered for.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of Event objects the user is registered for
        """
        return self.event_repo.get_events_by_registered_user(user_id)
    
    def get_user_waitlists(self, user_id: str) -> List[Event]:
        """Get all events a user is waitlisted for.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of Event objects the user is waitlisted for
        """
        return self.event_repo.get_events_by_waitlisted_user(user_id)
    
    def get_event_registrations(self, event_id: str) -> List[str]:
        """Get all registered user IDs for an event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            List of user IDs registered for the event
            
        Raises:
            EntityNotFoundError: If event doesn't exist
        """
        event = self.event_repo.get(event_id)
        if event is None:
            raise EntityNotFoundError(f"Event {event_id} not found")
        
        return event.registered_users
