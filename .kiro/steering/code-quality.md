# Code Quality and Best Practices

General coding standards and best practices for this project.

## Python Code Standards

### Style Guide
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Keep functions small and focused (single responsibility)
- Maximum line length: 100 characters
- Use type hints for function parameters and return values

### Code Organization
```python
# Import order:
# 1. Standard library imports
# 2. Third-party imports
# 3. Local application imports

import os
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .models import Event
```

### Documentation
- Add docstrings to all functions, classes, and modules
- Use clear, concise comments for complex logic
- Keep comments up-to-date with code changes
- Document API endpoints with descriptions

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Log errors appropriately
- Never expose sensitive information in errors
- Always clean up resources (use context managers)

### Testing
- Write tests for new features
- Maintain test coverage
- Use descriptive test names
- Test edge cases and error conditions
- Mock external dependencies

## FastAPI Specific

### Endpoint Design
- Use appropriate HTTP methods
- Define clear request/response models
- Add endpoint descriptions and tags
- Use dependency injection for shared logic
- Implement proper validation

### Models
- Use Pydantic models for validation
- Define clear field constraints
- Add field descriptions
- Use validators for complex validation
- Separate create/update/response models

### Example
```python
from pydantic import BaseModel, Field, validator

class EventCreate(BaseModel):
    """Model for creating a new event."""
    title: str = Field(..., min_length=1, max_length=200)
    capacity: int = Field(..., gt=0, le=100000)
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

## AWS CDK Standards

### Stack Organization
- Keep stacks focused and modular
- Use constructs for reusable components
- Define clear resource naming conventions
- Add tags to all resources
- Use environment variables for configuration

### Resource Naming
```python
# Use descriptive, consistent names
events_table = dynamodb.Table(
    self,
    "EventsTable",  # Construct ID
    table_name="events-prod",  # Resource name
)
```

### Best Practices
- Use removal policies appropriately
- Enable encryption where applicable
- Configure proper IAM permissions (least privilege)
- Add CloudFormation outputs for important values
- Document infrastructure decisions

## Security

### General
- Never commit secrets or credentials
- Use environment variables for sensitive data
- Validate and sanitize all inputs
- Implement proper authentication/authorization
- Keep dependencies up-to-date

### AWS Specific
- Use IAM roles instead of access keys when possible
- Enable encryption at rest and in transit
- Configure VPC and security groups properly
- Enable CloudTrail logging
- Use AWS Secrets Manager for secrets

## Performance

### Code Optimization
- Avoid premature optimization
- Profile before optimizing
- Use appropriate data structures
- Cache expensive operations
- Minimize database queries

### AWS Optimization
- Use appropriate Lambda memory settings
- Implement connection pooling
- Enable DynamoDB auto-scaling
- Use CloudFront for static content
- Monitor and optimize costs

## Git Practices

### Commits
- Write clear, descriptive commit messages
- Keep commits focused and atomic
- Reference issues in commit messages
- Don't commit generated files or dependencies

### Branches
- Use feature branches for new work
- Keep branches up-to-date with main
- Delete branches after merging
- Use meaningful branch names

### Commit Message Format
```
<type>: <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat: Add event filtering by status

Implement query parameter filtering for events endpoint.
Users can now filter events by status using ?status=active.

Closes #123
```

## Code Review Checklist

Before submitting code:
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No commented-out code
- [ ] No debug statements
- [ ] Error handling implemented
- [ ] Security considerations addressed
- [ ] Performance implications considered

## Continuous Improvement

- Refactor when you see opportunities
- Update documentation as code changes
- Learn from code reviews
- Stay current with best practices
- Share knowledge with the team
