---
inclusion: fileMatch
fileMatchPattern: '(main\.py|.*api.*|.*endpoint.*|.*route.*)'
---

# API Standards and Best Practices

This document defines the REST API standards and conventions for this project. Follow these guidelines when working with API-related code.

## HTTP Methods

Use HTTP methods according to their semantic meaning:

- **GET**: Retrieve resources (read-only, idempotent, cacheable)
- **POST**: Create new resources (non-idempotent)
- **PUT**: Update existing resources (idempotent, full replacement)
- **PATCH**: Partially update resources (idempotent, partial update)
- **DELETE**: Remove resources (idempotent)

## HTTP Status Codes

Use appropriate status codes for different scenarios:

### Success Codes (2xx)
- **200 OK**: Successful GET, PUT, PATCH requests
- **201 Created**: Successful POST request that creates a resource
- **204 No Content**: Successful DELETE request or update with no response body

### Client Error Codes (4xx)
- **400 Bad Request**: Invalid request data, validation errors
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Resource conflict (e.g., duplicate)
- **422 Unprocessable Entity**: Validation error with detailed feedback

### Server Error Codes (5xx)
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: Service temporarily unavailable

## JSON Response Format

### Success Response
All successful responses should return JSON with consistent structure:

```json
{
  "data": { ... },
  "message": "Optional success message"
}
```

For list endpoints:
```json
{
  "data": [ ... ],
  "count": 10,
  "page": 1,
  "total": 100
}
```

### Error Response
All error responses must follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "OPTIONAL_ERROR_CODE",
  "field_errors": {
    "field_name": ["Error message for this field"]
  }
}
```

## API Endpoint Conventions

### URL Structure
- Use plural nouns for resources: `/events`, `/users`
- Use kebab-case for multi-word resources: `/event-categories`
- Use path parameters for resource IDs: `/events/{eventId}`
- Use query parameters for filtering, sorting, pagination: `/events?status=active&page=1`

### Naming Conventions
- Endpoints should be lowercase
- Use hyphens (-) to separate words in URLs
- Avoid verbs in endpoint names (use HTTP methods instead)
- Keep URLs short and intuitive

### Examples
✅ Good:
- `GET /events` - List events
- `POST /events` - Create event
- `GET /events/{id}` - Get specific event
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event
- `GET /events?status=active` - Filter events

❌ Bad:
- `GET /getEvents`
- `POST /createEvent`
- `GET /event` (should be plural)
- `DELETE /events/delete/{id}` (redundant verb)

## Request/Response Headers

### Required Headers
- `Content-Type: application/json` for requests with body
- `Accept: application/json` for API requests

### CORS Headers
Ensure proper CORS configuration:
- `Access-Control-Allow-Origin`
- `Access-Control-Allow-Methods`
- `Access-Control-Allow-Headers`

## Input Validation

- Validate all input data using Pydantic models or similar
- Return 400 Bad Request for validation errors
- Provide clear, actionable error messages
- Validate data types, formats, ranges, and constraints
- Sanitize input to prevent injection attacks

## Error Handling

- Always catch and handle exceptions appropriately
- Never expose internal error details or stack traces to clients
- Log detailed errors server-side for debugging
- Return user-friendly error messages
- Use appropriate HTTP status codes

## API Versioning

- Consider API versioning for breaking changes
- Use URL versioning: `/v1/events`, `/v2/events`
- Or header versioning: `Accept: application/vnd.api.v1+json`

## Documentation

- Document all endpoints with clear descriptions
- Include request/response examples
- Document all query parameters and path parameters
- Specify required vs optional fields
- Keep documentation up-to-date with code changes

## Security Best Practices

- Implement authentication and authorization
- Use HTTPS in production
- Validate and sanitize all inputs
- Implement rate limiting
- Use secure headers (CORS, CSP, etc.)
- Never expose sensitive data in responses
- Log security-relevant events

## Performance

- Implement pagination for list endpoints
- Use appropriate caching strategies
- Optimize database queries
- Consider compression for large responses
- Monitor and log API performance metrics
