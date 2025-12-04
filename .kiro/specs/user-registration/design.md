# Design Document: User Registration System

## Overview

The user registration system provides a comprehensive solution for managing user profiles, events with capacity constraints, and registration workflows including waitlist management. The system is designed as a service layer that can be integrated into the existing FastAPI backend, with data persistence in DynamoDB.

The core design follows a domain-driven approach with clear separation between:
- Domain models (User, Event, Registration)
- Business logic (registration rules, capacity enforcement, waitlist management)
- Data access layer (repositories for persistence)
- API layer (FastAPI endpoints)

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   API Layer     │  FastAPI endpoints
│  (REST API)     │
└────────┬────────┘
         │
┌────────▼────────┐
│  Service Layer  │  Business logic & validation
│                 │
└────────┬────────┘
         │
┌────────▼────────┐
│ Repository      │  Data access abstraction
│    Layer        │
└────────┬────────┘
         │
┌────────▼────────┐
│   DynamoDB      │  Data persistence
└─────────────────┘
```

### Component Responsibilities

**API Layer**: Handles HTTP requests, input validation, and response formatting. Delegates business logic to the service layer.

**Service Layer**: Implements core business rules including:
- User and event creation with validation
- Registration logic with capacity checking
- Waitlist management and promotion
- Query operations for user registrations

**Repository Layer**: Provides data access abstraction with methods for CRUD operations on users, events, and registrations. Isolates DynamoDB-specific implementation details.

**Domain Models**: Represent core business entities with validation logic and business rules.

## Components and Interfaces

### Domain Models

#### User
```python
@dataclass
class User:
    user_id: str
    name: str
    
    def __post_init__(self):
        # Validation logic
        if not self.user_id or not self.user_id.strip():
            raise ValueError("userId cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
```

#### Event
```python
@dataclass
class Event:
    event_id: str
    name: str
    capacity: int
    waitlist_enabled: bool
    registered_users: List[str]  # List of user_ids
    waitlist: List[str]  # List of user_ids in order
    
    def __post_init__(self):
        if self.capacity <= 0:
            raise ValueError("capacity must be greater than zero")
    
    def is_full(self) -> bool:
        return len(self.registered_users) >= self.capacity
    
    def has_available_capacity(self) -> bool:
        return len(self.registered_users) < self.capacity
```

### Service Layer

#### RegistrationService
```python
class RegistrationService:
    def __init__(self, user_repo: UserRepository, event_repo: EventRepository):
        self.user_repo = user_repo
        self.event_repo = event_repo
    
    def create_user(self, user_id: str, name: str) -> User
    def create_event(self, event_id: str, name: str, capacity: int, waitlist_enabled: bool) -> Event
    def register_user(self, user_id: str, event_id: str) -> RegistrationResult
    def unregister_user(self, user_id: str, event_id: str) -> None
    def get_user_registrations(self, user_id: str) -> List[Event]
    def get_user_waitlists(self, user_id: str) -> List[Event]
    def get_event_registrations(self, event_id: str) -> List[str]
```

#### RegistrationResult
```python
@dataclass
class RegistrationResult:
    status: str  # "registered", "waitlisted", "denied"
    message: str
```

### Repository Layer

#### UserRepository
```python
class UserRepository:
    def create(self, user: User) -> User
    def get(self, user_id: str) -> Optional[User]
    def exists(self, user_id: str) -> bool
```

#### EventRepository
```python
class EventRepository:
    def create(self, event: Event) -> Event
    def get(self, event_id: str) -> Optional[Event]
    def update(self, event: Event) -> Event
    def get_events_by_registered_user(self, user_id: str) -> List[Event]
    def get_events_by_waitlisted_user(self, user_id: str) -> List[Event]
```

### API Layer

#### Endpoints

```
POST   /users                                      - Create a new user
GET    /users/{user_id}                            - Get user details
POST   /events                                     - Create a new event
GET    /events/{event_id}                          - Get event details
POST   /events/{event_id}/registrations            - Register user for event
GET    /events/{event_id}/registrations            - Get event's registered users
DELETE /events/{event_id}/registrations/{user_id} - Unregister user from event
GET    /users/{user_id}/registrations              - Get user's registered events
GET    /users/{user_id}/waitlists                  - Get user's waitlisted events
```

#### Request/Response Models

**User Creation (POST /users)**
```json
Request: {
  "userId": "string",
  "name": "string"
}
Response: {
  "userId": "string",
  "name": "string"
}
```

**Event Creation (POST /events)**
```json
Request: {
  "eventId": "string",
  "title": "string",
  "description": "string",
  "date": "string",
  "location": "string",
  "capacity": number,
  "organizer": "string",
  "status": "string",
  "waitlistEnabled": boolean
}
Response: {
  "eventId": "string",
  "title": "string",
  "description": "string",
  "date": "string",
  "location": "string",
  "capacity": number,
  "organizer": "string",
  "status": "string",
  "waitlistEnabled": boolean,
  "registeredCount": number,
  "waitlistCount": number
}
```

**Registration (POST /events/{event_id}/registrations)**
```json
Request: {
  "userId": "string"
}
Response: {
  "status": "registered" | "waitlisted" | "denied",
  "message": "string"
}
```

## Data Models

### DynamoDB Table Design

We'll use a single-table design with the following structure:

**Table Name**: `registration-system`

**Primary Key**:
- Partition Key (PK): Entity type and ID
- Sort Key (SK): Related entity or metadata

**GSI-1** (for querying user registrations):
- GSI1PK: user_id
- GSI1SK: registration status (registered/waitlisted)

#### Access Patterns

| Pattern | PK | SK | GSI |
|---------|----|----|-----|
| Get User | USER#{user_id} | METADATA | - |
| Get Event | EVENT#{event_id} | METADATA | - |
| Get Event Registrations | EVENT#{event_id} | REG#{user_id} | - |
| Get Event Waitlist | EVENT#{event_id} | WAIT#{position}#{user_id} | - |
| Get User Registrations | - | - | GSI1PK=USER#{user_id}, GSI1SK=REGISTERED |
| Get User Waitlists | - | - | GSI1PK=USER#{user_id}, GSI1SK=WAITLISTED |

#### Item Examples

**User Item**:
```json
{
  "PK": "USER#user123",
  "SK": "METADATA",
  "entity_type": "user",
  "user_id": "user123",
  "name": "John Doe"
}
```

**Event Item**:
```json
{
  "PK": "EVENT#event456",
  "SK": "METADATA",
  "entity_type": "event",
  "event_id": "event456",
  "name": "Tech Conference",
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-20",
  "location": "Convention Center",
  "organizer": "Tech Corp",
  "status": "active",
  "capacity": 100,
  "waitlist_enabled": true,
  "registered_count": 100,
  "waitlist_count": 5
}
```

**Registration Item**:
```json
{
  "PK": "EVENT#event456",
  "SK": "REG#user123",
  "GSI1PK": "USER#user123",
  "GSI1SK": "REGISTERED",
  "entity_type": "registration",
  "user_id": "user123",
  "event_id": "event456",
  "status": "registered"
}
```

**Waitlist Item**:
```json
{
  "PK": "EVENT#event456",
  "SK": "WAIT#00005#user789",
  "GSI1PK": "USER#user789",
  "GSI1SK": "WAITLISTED",
  "entity_type": "waitlist",
  "user_id": "user789",
  "event_id": "event456",
  "position": 5,
  "status": "waitlisted"
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User creation round trip
*For any* valid userId and name (non-empty, non-whitespace), creating a user and then retrieving it should return a user with the same userId and name.
**Validates: Requirements 1.1**

### Property 2: Invalid user input rejection
*For any* string composed entirely of whitespace or empty string, attempting to create a user with that string as either userId or name should be rejected with an error.
**Validates: Requirements 1.3, 1.4**

### Property 3: Capacity enforcement
*For any* event with capacity N, after N users have successfully registered, the count of registered users should equal N and no additional users should be able to register without using the waitlist.
**Validates: Requirements 2.1**

### Property 4: Invalid capacity rejection
*For any* integer value less than or equal to zero, attempting to create an event with that capacity should be rejected with an error.
**Validates: Requirements 2.2**

### Property 5: Waitlist behavior when enabled
*For any* event with waitlist enabled and at full capacity, attempting to register an additional user should result in that user being added to the waitlist rather than being denied.
**Validates: Requirements 2.3, 3.3**

### Property 6: Registration denial without waitlist
*For any* event without waitlist that is at full capacity, attempting to register an additional user should be denied with an error.
**Validates: Requirements 2.4, 3.2**

### Property 7: Successful registration adds user
*For any* user and any event with available capacity, registering the user should result in the user appearing in the event's registered users list.
**Validates: Requirements 3.1**

### Property 8: Duplicate registration prevention
*For any* user already registered for an event, attempting to register that user for the same event again should be rejected with an error.
**Validates: Requirements 3.4**

### Property 9: Unregistration removes user
*For any* user registered for an event, unregistering that user should result in the user no longer appearing in the event's registered users list.
**Validates: Requirements 4.1**

### Property 10: Waitlist promotion on unregistration
*For any* event with a non-empty waitlist, when a registered user unregisters, the first user from the waitlist should be moved to the registered users list and removed from the waitlist.
**Validates: Requirements 4.2**

### Property 11: Waitlist unregistration removes user
*For any* user on an event's waitlist, unregistering that user should result in the user no longer appearing in the event's waitlist.
**Validates: Requirements 4.3**

### Property 12: User registrations query accuracy
*For any* user, querying their registered events should return exactly the set of events where the user appears in the registered users list, excluding any events where the user is only on the waitlist.
**Validates: Requirements 5.1, 5.3**

### Property 13: User waitlists query accuracy
*For any* user, querying their waitlisted events should return exactly the set of events where the user appears on the waitlist.
**Validates: Requirements 6.1**

## Error Handling

### Error Types

The system will define specific exception types for different error conditions:

```python
class RegistrationError(Exception):
    """Base exception for registration system errors"""
    pass

class ValidationError(RegistrationError):
    """Raised when input validation fails"""
    pass

class DuplicateUserError(RegistrationError):
    """Raised when attempting to create a user with duplicate userId"""
    pass

class EventFullError(RegistrationError):
    """Raised when attempting to register for a full event without waitlist"""
    pass

class AlreadyRegisteredError(RegistrationError):
    """Raised when user attempts to register for event they're already registered for"""
    pass

class NotRegisteredError(RegistrationError):
    """Raised when user attempts to unregister from event they're not part of"""
    pass

class EntityNotFoundError(RegistrationError):
    """Raised when referenced user or event doesn't exist"""
    pass
```

### Error Handling Strategy

1. **Input Validation**: Validate all inputs at the domain model level using `__post_init__` methods
2. **Business Rule Violations**: Check business rules in the service layer and raise appropriate exceptions
3. **Data Access Errors**: Handle DynamoDB errors in the repository layer and translate to domain exceptions
4. **API Layer**: Catch exceptions and return appropriate HTTP status codes with error messages

### HTTP Status Code Mapping

- `400 Bad Request`: ValidationError, AlreadyRegisteredError
- `404 Not Found`: EntityNotFoundError
- `409 Conflict`: DuplicateUserError, EventFullError
- `422 Unprocessable Entity`: NotRegisteredError
- `500 Internal Server Error`: Unexpected errors

## Testing Strategy

The testing strategy employs both unit testing and property-based testing to ensure comprehensive coverage and correctness.

### Property-Based Testing

We will use **Hypothesis** as the property-based testing library for Python. Hypothesis will generate random test cases to verify that our correctness properties hold across a wide range of inputs.

**Configuration**:
- Each property-based test will run a minimum of 100 iterations
- Each test will be tagged with a comment referencing the specific correctness property from this design document
- Tag format: `# Feature: user-registration, Property {number}: {property_text}`

**Property Test Coverage**:
- Each of the 13 correctness properties defined above will be implemented as a single property-based test
- Tests will use Hypothesis strategies to generate:
  - Random valid and invalid userIds and names
  - Random event configurations (capacity, waitlist settings)
  - Random sequences of registration and unregistration operations
  - Random user and event combinations

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

# Feature: user-registration, Property 1: User creation round trip
@given(
    user_id=st.text(min_size=1).filter(lambda s: s.strip()),
    name=st.text(min_size=1).filter(lambda s: s.strip())
)
def test_user_creation_round_trip(user_id, name):
    service = RegistrationService(user_repo, event_repo)
    created_user = service.create_user(user_id, name)
    retrieved_user = user_repo.get(user_id)
    assert retrieved_user.user_id == user_id
    assert retrieved_user.name == name
```

### Unit Testing

Unit tests will complement property-based tests by covering:

1. **Specific Examples**: Concrete scenarios that demonstrate correct behavior
2. **Edge Cases**: Boundary conditions like empty lists, zero capacity, first/last waitlist positions
3. **Integration Points**: Interactions between service layer and repositories
4. **Error Conditions**: Specific error scenarios with expected error messages

**Unit Test Coverage**:
- User creation with valid and invalid inputs
- Event creation with various capacity and waitlist configurations
- Registration workflows (success, waitlist, denial)
- Unregistration workflows (with and without waitlist promotion)
- Query operations (registrations, waitlists, empty results)
- Repository operations (CRUD, queries)

### Test Organization

```
tests/
├── unit/
│   ├── test_models.py          # Domain model validation
│   ├── test_service.py         # Service layer logic
│   ├── test_repositories.py    # Repository operations
│   └── test_api.py             # API endpoint behavior
└── property/
    ├── test_user_properties.py       # Properties 1-2
    ├── test_event_properties.py      # Properties 3-6
    ├── test_registration_properties.py  # Properties 7-8
    ├── test_unregistration_properties.py  # Properties 9-11
    └── test_query_properties.py      # Properties 12-13
```

### Testing Dependencies

- **pytest**: Test framework
- **hypothesis**: Property-based testing library
- **moto**: AWS service mocking for DynamoDB
- **pytest-cov**: Coverage reporting

## Implementation Notes

### Concurrency Considerations

DynamoDB operations for registration and unregistration should use conditional writes to prevent race conditions:

- Use `ConditionExpression` to ensure event capacity hasn't been exceeded
- Use atomic counters for `registered_count` and `waitlist_count`
- Implement optimistic locking for waitlist promotion

### Waitlist Ordering

Waitlist positions are maintained using zero-padded numbers in the sort key (e.g., `WAIT#00001#user123`). This ensures:
- Lexicographic sorting maintains insertion order
- First waitlisted user can be efficiently queried
- Position updates are minimized

### Performance Optimization

- Use batch operations for querying multiple events
- Implement caching for frequently accessed events
- Use DynamoDB streams for async notifications (future enhancement)
- Consider read replicas for high-traffic scenarios

### Future Enhancements

- Email notifications for waitlist promotions
- Event capacity updates with automatic waitlist processing
- User preferences for automatic waitlist registration
- Analytics and reporting on registration patterns
- Bulk registration operations
