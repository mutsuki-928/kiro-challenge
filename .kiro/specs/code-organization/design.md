# Design Document

## Overview

This design document outlines the refactoring approach to reorganize the event management backend into a clean, layered architecture. The refactoring will extract event management logic from `main.py` into a dedicated `events` module that mirrors the structure of the existing `registration` module. This will establish a consistent three-layer architecture (API → Service → Repository) across all features, improving maintainability, testability, and code clarity.

The refactoring is purely structural and will not change any API contracts or functionality. All existing endpoints will continue to work exactly as before.

## Architecture

### Current Architecture

```
backend/
├── main.py                    # Contains everything: API handlers, models, DB logic
├── registration/              # Well-structured module
│   ├── api.py                # API handlers
│   ├── service.py            # Business logic
│   ├── repositories.py       # Data access
│   ├── models.py             # Domain models
│   └── exceptions.py         # Custom exceptions
└── tests/
```

### Target Architecture

```
backend/
├── main.py                    # Application setup and routing only
├── events/                    # New events module
│   ├── __init__.py
│   ├── api.py                # Event API handlers
│   ├── service.py            # Event business logic
│   ├── repositories.py       # Event data access
│   ├── models.py             # Event domain models
│   └── exceptions.py         # Event-specific exceptions
├── registration/              # Existing registration module (unchanged)
│   ├── api.py
│   ├── service.py
│   ├── repositories.py
│   ├── models.py
│   └── exceptions.py
└── tests/
    ├── unit/
    │   ├── test_event_repositories.py
    │   └── test_repositories.py
    └── property/
        ├── test_event_properties.py
        └── test_user_properties.py
```

### Layered Architecture Pattern

Each feature module follows a three-layer architecture:

1. **API Layer** (`api.py`): Handles HTTP concerns
   - Request/response models (Pydantic)
   - Endpoint definitions
   - HTTP status codes
   - Exception to HTTP error mapping

2. **Service Layer** (`service.py`): Contains business logic
   - Orchestrates operations
   - Enforces business rules
   - Coordinates between repositories
   - Raises domain exceptions

3. **Repository Layer** (`repositories.py`): Manages data access
   - DynamoDB operations
   - Query construction
   - Data mapping to/from domain models
   - No business logic

## Components and Interfaces

### Events Module

#### models.py

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    """Domain model for an event."""
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
        """Validate event data."""
        # Validation logic here
```

#### exceptions.py

```python
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
```

#### repositories.py

```python
class EventRepository:
    """Repository for Event data access operations."""
    
    def __init__(self, table_name: Optional[str] = None):
        """Initialize with DynamoDB table."""
        pass
    
    def create(self, event: Event) -> Event:
        """Create a new event."""
        pass
    
    def get(self, event_id: str) -> Optional[Event]:
        """Get an event by ID."""
        pass
    
    def list(self, status: Optional[str] = None) -> List[Event]:
        """List all events, optionally filtered by status."""
        pass
    
    def update(self, event_id: str, updates: Dict[str, Any]) -> Event:
        """Update an event."""
        pass
    
    def delete(self, event_id: str) -> None:
        """Delete an event."""
        pass
    
    def exists(self, event_id: str) -> bool:
        """Check if an event exists."""
        pass
```

#### service.py

```python
class EventService:
    """Service for managing events."""
    
    def __init__(self, event_repo: EventRepository):
        """Initialize with repository."""
        self.event_repo = event_repo
    
    def create_event(self, event_data: Dict[str, Any]) -> Event:
        """Create a new event with validation."""
        pass
    
    def get_event(self, event_id: str) -> Event:
        """Get an event by ID."""
        pass
    
    def list_events(self, status: Optional[str] = None) -> List[Event]:
        """List events with optional filtering."""
        pass
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Event:
        """Update an event with validation."""
        pass
    
    def delete_event(self, event_id: str) -> None:
        """Delete an event."""
        pass
```

#### api.py

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/events", tags=["events"])

class EventCreate(BaseModel):
    """Request model for creating an event."""
    pass

class EventUpdate(BaseModel):
    """Request model for updating an event."""
    pass

class EventResponse(BaseModel):
    """Response model for event data."""
    pass

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    """Create a new event."""
    pass

@router.get("", response_model=List[EventResponse])
async def list_events(status: Optional[str] = None):
    """List all events."""
    pass

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """Get a specific event."""
    pass

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(event_id: str, event_update: EventUpdate):
    """Update an event."""
    pass

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """Delete an event."""
    pass
```

### Main Application

The refactored `main.py` will be simplified to:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from registration.api import router as registration_router
from events.api import router as events_router

app = FastAPI(title="Event Management API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(events_router)
app.include_router(registration_router)

@app.get("/")
async def root():
    return {"message": "Event Management API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

handler = Mangum(app)
```

## Data Models

### Event Domain Model

The Event model represents the core event entity with validation:

```python
@dataclass
class Event:
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
```

### API Models

Pydantic models for API request/response:

- `EventCreate`: For creating events (all fields required except eventId)
- `EventUpdate`: For updating events (all fields optional)
- `EventResponse`: For returning event data (all fields included)

## Correct
ness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Based on the requirements analysis, this refactoring is primarily structural rather than functional. Most acceptance criteria focus on code organization and architecture patterns, which are verified through code review rather than automated testing. However, there are critical functional properties that must be preserved during refactoring:

**Property 1: API Response Consistency**
*For any* valid event data input to an API endpoint, the refactored system should return the same response structure and data as the original system.
**Validates: Requirements 5.1**

**Property 2: Error Status Code Preservation**
*For any* error condition (invalid input, not found, etc.), the refactored system should return the same HTTP status code as the original system.
**Validates: Requirements 5.3**

**Property 3: Validation Error Consistency**
*For any* invalid request data, the refactored system should return validation errors in the same format as the original system.
**Validates: Requirements 5.4**

**Property 4: Domain Object Validation**
*For any* valid domain object data, creating the domain object should succeed without raising exceptions.
**Validates: Requirements 6.1**

**Property 5: Invalid Data Rejection**
*For any* invalid domain object data (empty strings, out-of-range values, invalid formats), creating the domain object should raise a validation exception.
**Validates: Requirements 6.2**

**Property 6: Domain Object Invariant**
*For any* domain object that exists in the system, all its fields should satisfy their validation constraints.
**Validates: Requirements 6.5**

**Property 7: Exception Type Specificity**
*For any* error scenario (duplicate, not found, validation failure), the system should raise a specific exception type that accurately describes the error category.
**Validates: Requirements 7.1**

**Property 8: Exception to HTTP Mapping**
*For any* domain exception raised by the service layer, the API layer should map it to the appropriate HTTP status code (404 for not found, 409 for conflict, 400 for validation, etc.).
**Validates: Requirements 7.2**

## Error Handling

### Exception Hierarchy

```python
# Base exceptions
class EventError(Exception):
    """Base exception for event-related errors."""
    pass

# Specific exceptions
class DuplicateEventError(EventError):
    """Raised when attempting to create an event with duplicate ID."""
    pass

class EventNotFoundError(EventError):
    """Raised when an event is not found."""
    pass

class InvalidEventDataError(EventError):
    """Raised when event data fails validation."""
    pass
```

### Exception to HTTP Status Code Mapping

The API layer will map exceptions to HTTP status codes:

- `EventNotFoundError` → 404 Not Found
- `DuplicateEventError` → 409 Conflict
- `InvalidEventDataError` → 400 Bad Request
- Generic `EventError` → 500 Internal Server Error
- Generic `Exception` → 500 Internal Server Error

### Error Response Format

All error responses will follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

This matches FastAPI's default HTTPException format, ensuring consistency with existing endpoints.

## Testing Strategy

### Unit Testing

Unit tests will verify specific behaviors and integration points:

1. **Repository Tests**
   - Test CRUD operations with specific data
   - Test query methods with filters
   - Test error handling for database failures
   - Test data mapping between DynamoDB and domain models

2. **Service Tests**
   - Test business logic with specific scenarios
   - Test validation enforcement
   - Test exception raising for error conditions
   - Test coordination between repositories

3. **API Tests**
   - Test endpoint routing and HTTP methods
   - Test request/response serialization
   - Test exception to HTTP status code mapping
   - Test specific error scenarios

### Property-Based Testing

Property-based tests will verify universal properties across many inputs using the Hypothesis library for Python:

**Configuration**: Each property-based test should run a minimum of 100 iterations to ensure thorough coverage of the input space.

**Test Tagging**: Each property-based test must include a comment explicitly referencing the correctness property from this design document using this format:
```python
# Feature: code-organization, Property 1: API Response Consistency
```

**Property Tests to Implement**:

1. **Property 1: API Response Consistency**
   - Generate random valid event data
   - Call create/update/get endpoints
   - Verify response structure matches expected format
   - Verify all required fields are present

2. **Property 2: Error Status Code Preservation**
   - Generate various error conditions (not found, invalid data)
   - Verify correct HTTP status codes are returned
   - Test across all endpoints

3. **Property 3: Validation Error Consistency**
   - Generate invalid request data (empty strings, out-of-range values)
   - Verify validation errors are returned
   - Verify error format is consistent

4. **Property 4: Domain Object Validation**
   - Generate random valid event data
   - Create Event domain objects
   - Verify no exceptions are raised

5. **Property 5: Invalid Data Rejection**
   - Generate invalid event data (various constraint violations)
   - Attempt to create Event domain objects
   - Verify InvalidEventDataError is raised

6. **Property 6: Domain Object Invariant**
   - Generate and create random valid Event objects
   - Verify all fields satisfy constraints
   - Test that no invalid Event objects can exist

7. **Property 7: Exception Type Specificity**
   - Trigger various error scenarios
   - Verify specific exception types are raised
   - Test duplicate creation, not found, validation failures

8. **Property 8: Exception to HTTP Mapping**
   - Raise various domain exceptions
   - Verify correct HTTP status codes are returned
   - Test all exception types

### Integration Testing

Integration tests will verify end-to-end functionality:

1. **API Integration Tests**
   - Test complete request/response cycles
   - Test with real DynamoDB (local or test environment)
   - Verify data persistence and retrieval
   - Test error scenarios with actual database

2. **Cross-Module Integration**
   - Test interaction between events and registration modules
   - Verify shared resources (DynamoDB tables) work correctly
   - Test application startup and router registration

### Refactoring Validation

To ensure the refactoring preserves functionality:

1. **Baseline Tests**: Run all existing tests before refactoring to establish baseline
2. **Incremental Testing**: Run tests after each refactoring step
3. **Comparison Testing**: Compare API responses before and after refactoring
4. **Manual Testing**: Test all endpoints manually to verify behavior

### Test Organization

```
backend/tests/
├── unit/
│   ├── test_event_models.py          # Domain model tests
│   ├── test_event_repositories.py    # Repository tests
│   ├── test_event_service.py         # Service tests
│   └── test_event_api.py             # API handler tests
├── property/
│   └── test_event_properties.py      # Property-based tests
└── integration/
    └── test_event_integration.py     # Integration tests
```

## Migration Strategy

### Phase 1: Create Events Module Structure
1. Create `backend/events/` directory
2. Create empty module files (`__init__.py`, `models.py`, `exceptions.py`, `repositories.py`, `service.py`, `api.py`)
3. Set up basic imports and structure

### Phase 2: Extract Domain Models
1. Move Event-related Pydantic models from `main.py` to `events/models.py`
2. Create domain model with validation
3. Create exception classes
4. Write unit tests for models

### Phase 3: Create Repository Layer
1. Extract DynamoDB operations from `main.py` to `events/repositories.py`
2. Implement EventRepository class
3. Write unit tests for repository

### Phase 4: Create Service Layer
1. Extract business logic to `events/service.py`
2. Implement EventService class
3. Write unit tests for service

### Phase 5: Create API Layer
1. Move endpoint definitions to `events/api.py`
2. Create router with all endpoints
3. Implement exception to HTTP mapping
4. Write API tests

### Phase 6: Update Main Application
1. Simplify `main.py` to only include router registration
2. Remove all event-related code from `main.py`
3. Verify all endpoints still work

### Phase 7: Testing and Validation
1. Run all unit tests
2. Run property-based tests
3. Run integration tests
4. Manual testing of all endpoints
5. Verify API contracts are preserved

## Dependencies

### Existing Dependencies
- FastAPI: Web framework
- Pydantic: Data validation
- boto3: AWS SDK for DynamoDB
- mangum: AWS Lambda adapter

### Testing Dependencies
- pytest: Test framework
- hypothesis: Property-based testing library
- pytest-asyncio: Async test support
- moto: AWS service mocking (for unit tests)

No new runtime dependencies are required for this refactoring.

## Performance Considerations

This refactoring should not impact performance:

1. **No Additional Layers**: The layered architecture doesn't add significant overhead
2. **Same Database Operations**: Repository methods perform the same DynamoDB operations
3. **No Extra Network Calls**: All operations remain local
4. **Minimal Object Creation**: Domain models are lightweight dataclasses

The main benefit is improved code organization and maintainability, not performance optimization.

## Security Considerations

Security remains unchanged:

1. **Input Validation**: Validation moves to domain models but remains equally strict
2. **Database Access**: Repository layer maintains same access patterns
3. **Error Messages**: Error messages don't expose sensitive information
4. **Authentication/Authorization**: Not affected by this refactoring (handled at API Gateway level)

## Rollback Plan

If issues arise during refactoring:

1. **Git History**: All changes are tracked in version control
2. **Incremental Commits**: Each phase is committed separately
3. **Feature Flags**: Not needed (refactoring is internal)
4. **Testing**: Comprehensive tests catch issues before deployment

The refactoring can be rolled back by reverting commits if necessary.
