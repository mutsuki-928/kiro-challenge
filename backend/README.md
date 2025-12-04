# Event Management API

A FastAPI-based REST API for managing events, deployed on AWS using serverless architecture (Lambda + API Gateway + DynamoDB).

## Features

- **CRUD Operations**: Create, Read, Update, and Delete events
- **Event Filtering**: Filter events by status
- **Input Validation**: Comprehensive validation using Pydantic models
- **Error Handling**: Proper HTTP status codes and error messages
- **CORS Support**: Configured for web access
- **Serverless**: Deployed on AWS Lambda with API Gateway

## Event Schema

Each event has the following properties:

- `eventId` (string): Unique identifier for the event
- `title` (string): Event title (1-200 characters)
- `description` (string): Event description (1-2000 characters)
- `date` (string): Event date in ISO format (e.g., "2024-12-25T10:00:00Z" or "2024-12-25")
- `location` (string): Event location (1-200 characters)
- `capacity` (integer): Maximum number of attendees (1-100000)
- `organizer` (string): Event organizer name (1-200 characters)
- `status` (string): Event status - one of: `draft`, `published`, `cancelled`, `completed`, `active`

## API Endpoints

### List Events
```
GET /events
GET /events?status=active
```
Returns a list of all events, optionally filtered by status.

**Response**: `200 OK`

### Create Event
```
POST /events
Content-Type: application/json
```

**Request Body**:
```json
{
  "eventId": "optional-custom-id",
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-25T10:00:00Z",
  "location": "Tokyo Convention Center",
  "capacity": 500,
  "organizer": "Tech Events Inc",
  "status": "published"
}
```

**Response**: `201 Created`

Note: `eventId` is optional. If not provided, a UUID will be generated automatically.

### Get Event by ID
```
GET /events/{eventId}
```

**Response**: `200 OK` or `404 Not Found`

### Update Event
```
PUT /events/{eventId}
Content-Type: application/json
```

**Request Body** (all fields optional):
```json
{
  "title": "Updated Title",
  "capacity": 600
}
```

**Response**: `200 OK` or `404 Not Found`

### Delete Event
```
DELETE /events/{eventId}
```

**Response**: `204 No Content` or `404 Not Found`

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable for DynamoDB table:
```bash
export EVENTS_TABLE_NAME=your-table-name
```

3. Run locally with uvicorn:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running locally, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Deployment

This API is designed to be deployed on AWS using CDK. See the `infrastructure/` directory for deployment configuration.

### AWS Resources

- **Lambda Function**: Runs the FastAPI application
- **API Gateway**: Provides HTTP endpoints
- **DynamoDB Table**: Stores event data

## Dependencies

- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `boto3==1.34.0` - AWS SDK
- `mangum==0.17.0` - AWS Lambda adapter for ASGI applications

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## License

MIT
