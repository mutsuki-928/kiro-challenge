# Event Management System

A full-stack event management system built with FastAPI and deployed on AWS using serverless architecture.

## Project Structure

```
.
├── backend/              # FastAPI REST API
│   ├── main.py          # API endpoints and application logic
│   ├── requirements.txt # Python dependencies
│   ├── docs/            # API documentation
│   └── README.md        # Backend-specific documentation
├── infrastructure/       # AWS CDK deployment configuration
│   ├── app.py           # CDK app entry point
│   ├── stacks/          # CDK stack definitions
│   └── cdk.json         # CDK configuration
└── README.md            # This file
```

## Features

- **RESTful API**: Complete CRUD operations for event management
- **User Registration System**: Manage user registrations with capacity constraints and waitlists
- **Serverless Architecture**: Deployed on AWS Lambda with API Gateway
- **NoSQL Database**: DynamoDB for scalable data storage with single-table design
- **Input Validation**: Comprehensive validation using Pydantic
- **CORS Support**: Configured for web application access
- **Infrastructure as Code**: AWS CDK for reproducible deployments
- **Property-Based Testing**: Hypothesis for comprehensive correctness validation

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for AWS CDK)
- AWS CLI configured with appropriate credentials
- AWS CDK CLI (`npm install -g aws-cdk`)

### Backend Development

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
export EVENTS_TABLE_NAME=local-events-table
uvicorn main:app --reload
```

4. Access the API:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Deployment

1. Install infrastructure dependencies:
```bash
cd infrastructure
pip install -r requirements.txt
```

2. Bootstrap CDK (first time only):
```bash
cdk bootstrap
```

3. Deploy to AWS:
```bash
cdk deploy
```

The deployment will output the API Gateway URL for accessing your deployed API.

## API Documentation

### Live API

**Base URL:** `https://ivtbuugyh1.execute-api.us-west-2.amazonaws.com/prod/`

### Endpoints

#### Event Management
- `GET /events` - List all events (supports `?status=active` filter)
- `POST /events` - Create a new event
- `GET /events/{id}` - Get event by ID
- `PUT /events/{id}` - Update event
- `DELETE /events/{id}` - Delete event

#### User Registration
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user by ID
- `POST /events/{event_id}/registrations` - Register user for event
- `GET /events/{event_id}/registrations` - Get registered users for event
- `DELETE /events/{event_id}/registrations/{user_id}` - Unregister user from event
- `GET /users/{user_id}/registrations` - Get user's registered events
- `GET /users/{user_id}/waitlists` - Get user's waitlisted events

For detailed API documentation, see:
- [Backend README](backend/README.md)
- [API Documentation](backend/docs/index.html)

### Example Usage

#### Event Management

Create an event:
```bash
curl -X POST https://ivtbuugyh1.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "event-123",
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-12-25",
    "location": "Tokyo Convention Center",
    "capacity": 100,
    "organizer": "Tech Events Inc",
    "status": "active",
    "waitlistEnabled": true
  }'
```

List all events:
```bash
curl https://ivtbuugyh1.execute-api.us-west-2.amazonaws.com/prod/events
```

#### User Registration

Create a user:
```bash
curl -X POST https://ivtbuugyh1.execute-api.us-west-2.amazonaws.com/prod/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "name": "John Doe"
  }'
```

Register user for event:
```bash
curl -X POST https://ivtbuugyh1.execute-api.us-west-2.amazonaws.com/prod/events/event-123/registrations \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123"
  }'
```

Get user's registrations:
```bash
curl https://ivtbuugyh1.execute-api.us-west-2.amazonaws.com/prod/users/user-123/registrations
```

## AWS Architecture

### Services Used

- **AWS Lambda**: Runs the FastAPI application in a serverless environment
- **Amazon API Gateway**: Provides HTTP endpoints and handles routing
- **Amazon DynamoDB**: NoSQL database for storing event data
- **AWS CloudFormation**: Manages infrastructure deployment (via CDK)

### Architecture Diagram

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  API Gateway    │
│  (REST API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lambda         │
│  (FastAPI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  DynamoDB                       │
│  - Events Table                 │
│  - Registration Table (GSI)     │
└─────────────────────────────────┘
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type annotations
- **Boto3** - AWS SDK for Python
- **Mangum** - ASGI adapter for AWS Lambda
- **Hypothesis** - Property-based testing framework
- **Pytest** - Testing framework

### Infrastructure
- **AWS CDK** - Infrastructure as Code framework
- **Python** - CDK language binding

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Environment Variables

### Backend

- `EVENTS_TABLE_NAME` - DynamoDB table name for events (set automatically in Lambda)
- `REGISTRATION_TABLE_NAME` - DynamoDB table name for registration system (set automatically in Lambda)

### Infrastructure

- `AWS_DEFAULT_REGION` - AWS region for deployment (default: us-west-2)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
