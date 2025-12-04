# Implementation Plan

- [x] 1. Create events module structure
  - Create `backend/events/` directory with all necessary files
  - Set up `__init__.py`, `models.py`, `exceptions.py`, `repositories.py`, `service.py`, `api.py`
  - Establish basic imports and module structure
  - _Requirements: 3.4, 3.5_

- [x] 2. Implement domain models and exceptions
- [x] 2.1 Create Event domain model with validation
  - Define Event dataclass in `events/models.py`
  - Implement `__post_init__` validation for all fields (title, description, date, location, capacity, organizer, status)
  - Ensure validation matches existing Pydantic validation logic
  - _Requirements: 6.1, 6.5_

- [ ]* 2.2 Write property test for domain object validation
  - **Property 4: Domain Object Validation**
  - **Validates: Requirements 6.1**

- [ ]* 2.3 Write property test for invalid data rejection
  - **Property 5: Invalid Data Rejection**
  - **Validates: Requirements 6.2**

- [ ]* 2.4 Write property test for domain object invariant
  - **Property 6: Domain Object Invariant**
  - **Validates: Requirements 6.5**

- [x] 2.5 Create exception classes
  - Define EventError base exception
  - Implement DuplicateEventError, EventNotFoundError, InvalidEventDataError
  - _Requirements: 7.1_

- [ ]* 2.6 Write unit tests for domain models
  - Test Event creation with valid data
  - Test validation for each field constraint
  - Test exception raising for invalid data
  - _Requirements: 6.1, 6.2_

- [ ] 3. Implement repository layer
- [x] 3.1 Create EventRepository class
  - Implement `__init__` with DynamoDB table setup
  - Implement `create` method to persist events
  - Implement `get` method to retrieve events by ID
  - Implement `list` method with optional status filtering
  - Implement `update` method for event updates
  - Implement `delete` method to remove events
  - Implement `exists` method to check event existence
  - _Requirements: 2.1, 2.3_

- [ ]* 3.2 Write unit tests for repository operations
  - Test create operation with mock DynamoDB
  - Test get operation for existing and non-existing events
  - Test list operation with and without filters
  - Test update operation
  - Test delete operation
  - _Requirements: 2.1_

- [ ] 4. Implement service layer
- [x] 4.1 Create EventService class
  - Implement `__init__` with EventRepository dependency
  - Implement `create_event` with business logic and validation
  - Implement `get_event` with error handling
  - Implement `list_events` with optional filtering
  - Implement `update_event` with validation and existence check
  - Implement `delete_event` with existence check
  - _Requirements: 1.1, 1.4_

- [ ]* 4.2 Write property test for exception type specificity
  - **Property 7: Exception Type Specificity**
  - **Validates: Requirements 7.1**

- [ ]* 4.3 Write unit tests for service layer
  - Test create_event with valid and invalid data
  - Test get_event for existing and non-existing events
  - Test list_events with various filters
  - Test update_event scenarios
  - Test delete_event scenarios
  - Test exception raising for business rule violations
  - _Requirements: 1.1, 7.1_

- [ ] 5. Implement API layer
- [x] 5.1 Create Pydantic request/response models
  - Define EventCreate model for POST requests
  - Define EventUpdate model for PUT requests
  - Define EventResponse model for responses
  - Ensure models match existing API contracts
  - _Requirements: 5.2_

- [x] 5.2 Create API router with all endpoints
  - Create FastAPI router with `/events` prefix
  - Implement POST `/events` endpoint for creating events
  - Implement GET `/events` endpoint for listing events
  - Implement GET `/events/{event_id}` endpoint for getting specific event
  - Implement PUT `/events/{event_id}` endpoint for updating events
  - Implement DELETE `/events/{event_id}` endpoint for deleting events
  - _Requirements: 1.1, 5.2_

- [x] 5.3 Implement exception to HTTP status code mapping
  - Map EventNotFoundError to 404
  - Map DuplicateEventError to 409
  - Map InvalidEventDataError to 400
  - Map generic exceptions to 500
  - Ensure error response format matches existing format
  - _Requirements: 7.2, 5.4_

- [ ]* 5.4 Write property test for exception to HTTP mapping
  - **Property 8: Exception to HTTP Mapping**
  - **Validates: Requirements 7.2**

- [ ]* 5.5 Write property test for API response consistency
  - **Property 1: API Response Consistency**
  - **Validates: Requirements 5.1**

- [ ]* 5.6 Write property test for error status code preservation
  - **Property 2: Error Status Code Preservation**
  - **Validates: Requirements 5.3**

- [ ]* 5.7 Write property test for validation error consistency
  - **Property 3: Validation Error Consistency**
  - **Validates: Requirements 5.4**

- [ ]* 5.8 Write unit tests for API endpoints
  - Test each endpoint with valid requests
  - Test error scenarios (not found, validation failures)
  - Test status code mapping
  - Test response format
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 6. Update main application
- [x] 6.1 Refactor main.py to use events router
  - Import events router
  - Register events router with app
  - Remove all event-related Pydantic models from main.py
  - Remove all event endpoint definitions from main.py
  - Remove DynamoDB setup for events table from main.py
  - Keep only app initialization, CORS middleware, router registration, and health endpoints
  - _Requirements: 8.1, 8.3, 8.5_

- [x] 6.2 Verify all endpoints are accessible
  - Test that `/events` endpoints work through the router
  - Test that `/users` and registration endpoints still work
  - Test health check endpoints
  - _Requirements: 5.1, 5.2_

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 8. Integration testing
- [ ]* 8.1 Write integration tests for complete workflows
  - Test create → get → update → delete workflow
  - Test list with filtering
  - Test error scenarios end-to-end
  - Test with actual DynamoDB local or test environment
  - _Requirements: 5.1_

- [ ]* 8.2 Write cross-module integration tests
  - Test that events and registration modules work together
  - Test shared DynamoDB access patterns
  - Test application startup and router registration
  - _Requirements: 4.1, 4.2_

- [ ] 9. Final validation and cleanup
- [ ] 9.1 Manual testing of all endpoints
  - Test all event endpoints manually
  - Verify response formats match original
  - Test error scenarios
  - Verify registration endpoints still work
  - _Requirements: 5.1, 5.2_

- [x] 9.2 Code review and cleanup
  - Review code for consistency with registration module
  - Remove any unused imports or code
  - Ensure all docstrings are present
  - Verify type hints are complete
  - _Requirements: 4.1, 4.2_

- [ ] 10. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
