"""API layer for event management endpoints."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
from datetime import datetime

from .exceptions import DuplicateEventError, EventNotFoundError, InvalidEventDataError
from .repositories import EventRepository
from .service import EventService

router = APIRouter(prefix="/events", tags=["events"])

# Initialize service with repository
_event_repo = EventRepository()
_event_service = EventService(_event_repo)


class EventCreate(BaseModel):
    """Request model for creating an event."""
    eventId: Optional[str] = Field(None, description="Unique identifier for the event")
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str = Field(..., min_length=1, max_length=2000, description="Event description")
    date: str = Field(..., description="Event date (ISO format or YYYY-MM-DD)")
    location: str = Field(..., min_length=1, max_length=200, description="Event location")
    capacity: int = Field(..., gt=0, le=100000, description="Maximum number of attendees")
    organizer: str = Field(..., min_length=1, max_length=200, description="Event organizer")
    status: str = Field(..., pattern="^(draft|published|cancelled|completed|active)$", description="Event status")
    
    @validator('date')
    def validate_date(cls, v):
        """Validate date format."""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Invalid date format. Use ISO format (e.g., 2024-12-25T10:00:00Z or 2024-12-25)')
        return v


class EventUpdate(BaseModel):
    """Request model for updating an event."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Event title")
    description: Optional[str] = Field(None, min_length=1, max_length=2000, description="Event description")
    date: Optional[str] = Field(None, description="Event date (ISO format or YYYY-MM-DD)")
    location: Optional[str] = Field(None, min_length=1, max_length=200, description="Event location")
    capacity: Optional[int] = Field(None, gt=0, le=100000, description="Maximum number of attendees")
    organizer: Optional[str] = Field(None, min_length=1, max_length=200, description="Event organizer")
    status: Optional[str] = Field(None, pattern="^(draft|published|cancelled|completed|active)$", description="Event status")
    
    @validator('date')
    def validate_date(cls, v):
        """Validate date format."""
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                try:
                    datetime.strptime(v, '%Y-%m-%d')
                except ValueError:
                    raise ValueError('Invalid date format. Use ISO format (e.g., 2024-12-25T10:00:00Z or 2024-12-25)')
        return v


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


def _map_exception_to_http(e: Exception) -> HTTPException:
    """Map domain exceptions to HTTP exceptions.
    
    Args:
        e: Domain exception
        
    Returns:
        HTTPException with appropriate status code
    """
    if isinstance(e, EventNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    elif isinstance(e, DuplicateEventError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    elif isinstance(e, InvalidEventDataError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process request: {str(e)}"
        )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    """Create a new event.
    
    Args:
        event: Event creation data
        
    Returns:
        The created event
        
    Raises:
        HTTPException: 400 for invalid data, 409 for duplicate event
    """
    try:
        created_event = _event_service.create_event(event.dict())
        return EventResponse(
            eventId=created_event.event_id,
            title=created_event.title,
            description=created_event.description,
            date=created_event.date,
            location=created_event.location,
            capacity=created_event.capacity,
            organizer=created_event.organizer,
            status=created_event.status
        )
    except (InvalidEventDataError, DuplicateEventError) as e:
        raise _map_exception_to_http(e)
    except Exception as e:
        raise _map_exception_to_http(e)


@router.get("", response_model=List[EventResponse])
async def list_events(status_filter: Optional[str] = None):
    """List all events.
    
    Args:
        status_filter: Optional status filter
        
    Returns:
        List of events
    """
    try:
        events = _event_service.list_events(status=status_filter)
        return [
            EventResponse(
                eventId=event.event_id,
                title=event.title,
                description=event.description,
                date=event.date,
                location=event.location,
                capacity=event.capacity,
                organizer=event.organizer,
                status=event.status
            )
            for event in events
        ]
    except Exception as e:
        raise _map_exception_to_http(e)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """Get a specific event.
    
    Args:
        event_id: Unique identifier for the event
        
    Returns:
        The event
        
    Raises:
        HTTPException: 404 if event not found
    """
    try:
        event = _event_service.get_event(event_id)
        return EventResponse(
            eventId=event.event_id,
            title=event.title,
            description=event.description,
            date=event.date,
            location=event.location,
            capacity=event.capacity,
            organizer=event.organizer,
            status=event.status
        )
    except EventNotFoundError as e:
        raise _map_exception_to_http(e)
    except Exception as e:
        raise _map_exception_to_http(e)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event_update: EventUpdate):
    """Update an event.
    
    Args:
        event_id: Unique identifier for the event
        event_update: Event update data
        
    Returns:
        The updated event
        
    Raises:
        HTTPException: 400 for invalid data, 404 if event not found
    """
    try:
        updates = event_update.dict(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updated_event = _event_service.update_event(event_id, updates)
        return EventResponse(
            eventId=updated_event.event_id,
            title=updated_event.title,
            description=updated_event.description,
            date=updated_event.date,
            location=updated_event.location,
            capacity=updated_event.capacity,
            organizer=updated_event.organizer,
            status=updated_event.status
        )
    except (EventNotFoundError, InvalidEventDataError) as e:
        raise _map_exception_to_http(e)
    except HTTPException:
        raise
    except Exception as e:
        raise _map_exception_to_http(e)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """Delete an event.
    
    Args:
        event_id: Unique identifier for the event
        
    Raises:
        HTTPException: 404 if event not found
    """
    try:
        _event_service.delete_event(event_id)
        return None
    except EventNotFoundError as e:
        raise _map_exception_to_http(e)
    except Exception as e:
        raise _map_exception_to_http(e)
