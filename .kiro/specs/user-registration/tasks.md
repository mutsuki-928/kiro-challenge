# Implementation Plan

- [x] 1. Set up project structure and domain models
  - Create directory structure for models, services, repositories, and tests
  - Define custom exception classes for error handling
  - Implement User and Event domain models with validation
  - _Requirements: 1.1, 1.3, 1.4, 2.1, 2.2_

- [x] 1.1 Write property test for user creation round trip
  - **Property 1: User creation round trip**
  - **Validates: Requirements 1.1**

- [x] 1.2 Write property test for invalid user input rejection
  - **Property 2: Invalid user input rejection**
  - **Validates: Requirements 1.3, 1.4**

- [x] 1.3 Write property test for invalid capacity rejection
  - **Property 4: Invalid capacity rejection**
  - **Validates: Requirements 2.2**

- [x] 2. Implement repository layer with DynamoDB
  - Create UserRepository with create, get, and exists methods
  - Create EventRepository with create, get, update methods
  - Implement DynamoDB table access patterns for single-table design
  - Set up conditional writes for concurrency safety
  - _Requirements: 1.1, 1.2, 2.1, 2.3, 2.4_

- [x] 2.1 Write unit tests for repository operations
  - Test user CRUD operations
  - Test event CRUD operations
  - Test conditional write behavior
  - Use moto for DynamoDB mocking
  - _Requirements: 1.1, 1.2, 2.1_

- [-] 3. Implement user and event creation in service layer
  - Create RegistrationService class with repository dependencies
  - Implement create_user method with duplicate checking
  - Implement create_event method with validation
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4_

- [ ] 3.1 Write unit tests for user creation
  - Test successful user creation
  - Test duplicate userId rejection
  - Test validation error handling
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 3.2 Write unit tests for event creation
  - Test successful event creation with and without waitlist
  - Test capacity validation
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 4. Implement registration logic
  - Implement register_user method with capacity checking
  - Handle registration to events with available capacity
  - Handle registration to full events without waitlist (denial)
  - Handle registration to full events with waitlist (add to waitlist)
  - Prevent duplicate registrations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 4.1 Write property test for capacity enforcement
  - **Property 3: Capacity enforcement**
  - **Validates: Requirements 2.1**

- [ ] 4.2 Write property test for waitlist behavior when enabled
  - **Property 5: Waitlist behavior when enabled**
  - **Validates: Requirements 2.3, 3.3**

- [ ] 4.3 Write property test for registration denial without waitlist
  - **Property 6: Registration denial without waitlist**
  - **Validates: Requirements 2.4, 3.2**

- [ ] 4.4 Write property test for successful registration adds user
  - **Property 7: Successful registration adds user**
  - **Validates: Requirements 3.1**

- [ ] 4.5 Write property test for duplicate registration prevention
  - **Property 8: Duplicate registration prevention**
  - **Validates: Requirements 3.4**

- [ ] 4.6 Write unit tests for registration scenarios
  - Test registration with available capacity
  - Test registration to full event without waitlist
  - Test registration to full event with waitlist
  - Test duplicate registration attempt
  - Test registration to non-existent event
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement unregistration logic
  - Implement unregister_user method
  - Handle unregistration from registered users list
  - Handle unregistration from waitlist
  - Implement waitlist promotion when registered user unregisters
  - Validate user is actually registered or waitlisted before unregistering
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6.1 Write property test for unregistration removes user
  - **Property 9: Unregistration removes user**
  - **Validates: Requirements 4.1**

- [ ] 6.2 Write property test for waitlist promotion on unregistration
  - **Property 10: Waitlist promotion on unregistration**
  - **Validates: Requirements 4.2**

- [ ] 6.3 Write property test for waitlist unregistration removes user
  - **Property 11: Waitlist unregistration removes user**
  - **Validates: Requirements 4.3**

- [ ] 6.4 Write unit tests for unregistration scenarios
  - Test unregistration from registered list
  - Test unregistration from waitlist
  - Test waitlist promotion after unregistration
  - Test unregistration when not registered or waitlisted
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 7. Implement query operations
  - Implement get_user_registrations method using GSI
  - Implement get_user_waitlists method using GSI
  - Add repository methods for querying events by user
  - Ensure registered events exclude waitlisted events
  - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.2_

- [ ] 7.1 Write property test for user registrations query accuracy
  - **Property 12: User registrations query accuracy**
  - **Validates: Requirements 5.1, 5.3**

- [ ] 7.2 Write property test for user waitlists query accuracy
  - **Property 13: User waitlists query accuracy**
  - **Validates: Requirements 6.1**

- [ ] 7.3 Write unit tests for query operations
  - Test get_user_registrations with multiple events
  - Test get_user_registrations with no registrations
  - Test get_user_waitlists with multiple events
  - Test get_user_waitlists with no waitlists
  - Test that registered events exclude waitlisted events
  - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.2_

- [-] 8. Implement API endpoints
  - Create FastAPI router for registration endpoints
  - Implement POST /users endpoint with request/response models
  - Implement GET /users/{user_id} endpoint
  - Implement POST /events endpoint with request/response models (use waitlistEnabled field)
  - Implement GET /events/{event_id} endpoint
  - Implement POST /events/{event_id}/registrations endpoint
  - Implement GET /events/{event_id}/registrations endpoint
  - Implement DELETE /events/{event_id}/registrations/{user_id} endpoint
  - Implement GET /users/{user_id}/registrations endpoint
  - Implement GET /users/{user_id}/waitlists endpoint
  - Add proper error handling and HTTP status code mapping
  - _Requirements: All requirements_

- [ ] 8.1 Write unit tests for API endpoints
  - Test all endpoints with valid inputs
  - Test error responses with appropriate status codes
  - Test request validation
  - _Requirements: All requirements_

- [x] 9. Update CDK infrastructure
  - Add DynamoDB table definition to CDK stack
  - Configure table with partition key, sort key, and GSI
  - Set up appropriate IAM permissions for Lambda
  - Add table name to Lambda environment variables
  - Configure removal policy and encryption settings
  - _Requirements: All requirements_

- [x] 10. Integration and documentation
  - Wire up registration service in main FastAPI application
  - Update API documentation with new endpoints
  - Add example requests and responses to docs
  - Update README with registration feature information
  - _Requirements: All requirements_

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
