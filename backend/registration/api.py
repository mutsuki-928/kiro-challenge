"""API endpoints for the registration system."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator

from .service import RegistrationService
from .repositories import UserRepository, EventRepository
from .exceptions import (
    ValidationError,
    DuplicateUserError,
    EntityNotFoundError,
    EventFullError,
    AlreadyRegisteredError,
    NotRegisteredError
)


# Pydantic models for API
class UserCreate(BaseModel):
    """Request model for creating a user."""
    userId: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's name")


class UserResponse(BaseModel):
    """Response model for user data."""
    userId: str
    name: str


class EventCreate(BaseModel):
    """Request model for creating an event."""
    eventId: str = Field(..., description="Unique event identifier")
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Event description")
    date: str = Field(..., description="Event date")
    location: str = Field(..., description="Event location")
    capacity: int = Field(..., gt=0, description="Maximum capacity")
    organizer: str = Field(..., description="Event organizer")
    status: str = Field(..., description="Event status")
    waitlistEnabled: bool = Field(..., description="Whether waitlist is enabled")


class EventResponse(BaseModel):
    """Response model for event data."""
    eventId: str
    title: str
    description: str
    date: str
    location: str
    capacity: int
    organizer: str
    status: str
    waitlistEnabled: bool
    registeredCount: int
    waitlistCount: int


class RegistrationRequest(BaseModel):
    """Request model for registering a user."""
    userId: str = Field(..., description="User ID to register")


class RegistrationResponse(BaseModel):
    """Response model for registration result."""
    status: str
    message: str


class RegistrationListResponse(BaseModel):
    """Response model for list of registrations."""
    registrations: List[str]


# Create router
router = APIRouter(prefix="", tags=["registration"])


# Initialize service (will be overridden in main.py with actual table name)
def get_registration_service():
    """Get registration service instance."""
    user_repo = UserRepository()
    event_repo = EventRepository()
    return RegistrationService(user_repo, event_repo)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user.
    
    Args:
        user_data: User creation data
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    service = get_registration_service()
    
    try:
        user = service.create_user(user_data.userId, user_data.name)
        return UserResponse(userId=user.user_id, name=user.name)
    except DuplicateUserError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a user by ID.
    
    Args:
        user_id: User's ID
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    service = get_registration_service()
    user_repo = service.user_repo
    
    user = user_repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    
    return UserResponse(userId=user.user_id, name=user.name)


@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event_data: EventCreate):
    """Create a new event.
    
    Args:
        event_data: Event creation data
        
    Returns:
        Created event data
        
    Raises:
        HTTPException: If validation fails
    """
    service = get_registration_service()
    
    try:
        event = service.create_event(
            event_id=event_data.eventId,
            name=event_data.title,
            capacity=event_data.capacity,
            waitlist_enabled=event_data.waitlistEnabled
        )
        
        return EventResponse(
            eventId=event.event_id,
            title=event_data.title,
            description=event_data.description,
            date=event_data.date,
            location=event_data.location,
            capacity=event.capacity,
            organizer=event_data.organizer,
            status=event_data.status,
            waitlistEnabled=event.waitlist_enabled,
            registeredCount=len(event.registered_users),
            waitlistCount=len(event.waitlist)
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """Get an event by ID.
    
    Args:
        event_id: Event's ID
        
    Returns:
        Event data
        
    Raises:
        HTTPException: If event not found
    """
    service = get_registration_service()
    event_repo = service.event_repo
    
    event = event_repo.get(event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event {event_id} not found")
    
    return EventResponse(
        eventId=event.event_id,
        title=event.name,
        description="",
        date="",
        location="",
        capacity=event.capacity,
        organizer="",
        status="active",
        waitlistEnabled=event.waitlist_enabled,
        registeredCount=len(event.registered_users),
        waitlistCount=len(event.waitlist)
    )


@router.post("/events/{event_id}/registrations", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_for_event(event_id: str, registration: RegistrationRequest):
    """Register a user for an event.
    
    Args:
        event_id: Event's ID
        registration: Registration request data
        
    Returns:
        Registration result
        
    Raises:
        HTTPException: If registration fails
    """
    service = get_registration_service()
    
    try:
        result = service.register_user(registration.userId, event_id)
        return RegistrationResponse(status=result.status, message=result.message)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AlreadyRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except EventFullError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/events/{event_id}/registrations", response_model=RegistrationListResponse)
async def get_event_registrations(event_id: str):
    """Get all registered users for an event.
    
    Args:
        event_id: Event's ID
        
    Returns:
        List of registered user IDs
        
    Raises:
        HTTPException: If event not found
    """
    service = get_registration_service()
    
    try:
        registrations = service.get_event_registrations(event_id)
        return RegistrationListResponse(registrations=registrations)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_from_event(event_id: str, user_id: str):
    """Unregister a user from an event.
    
    Args:
        event_id: Event's ID
        user_id: User's ID
        
    Raises:
        HTTPException: If unregistration fails
    """
    service = get_registration_service()
    
    try:
        service.unregister_user(user_id, event_id)
        return None
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotRegisteredError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/users/{user_id}/registrations", response_model=List[EventResponse])
async def get_user_registrations(user_id: str):
    """Get all events a user is registered for.
    
    Args:
        user_id: User's ID
        
    Returns:
        List of events
    """
    service = get_registration_service()
    
    events = service.get_user_registrations(user_id)
    return [
        EventResponse(
            eventId=event.event_id,
            title=event.name,
            description="",
            date="",
            location="",
            capacity=event.capacity,
            organizer="",
            status="active",
            waitlistEnabled=event.waitlist_enabled,
            registeredCount=len(event.registered_users),
            waitlistCount=len(event.waitlist)
        )
        for event in events
    ]


@router.get("/users/{user_id}/waitlists", response_model=List[EventResponse])
async def get_user_waitlists(user_id: str):
    """Get all events a user is waitlisted for.
    
    Args:
        user_id: User's ID
        
    Returns:
        List of events
    """
    service = get_registration_service()
    
    events = service.get_user_waitlists(user_id)
    return [
        EventResponse(
            eventId=event.event_id,
            title=event.name,
            description="",
            date="",
            location="",
            capacity=event.capacity,
            organizer="",
            status="active",
            waitlistEnabled=event.waitlist_enabled,
            registeredCount=len(event.registered_users),
            waitlistCount=len(event.waitlist)
        )
        for event in events
    ]
