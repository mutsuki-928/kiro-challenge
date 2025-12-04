"""Repository layer for event data access operations."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Attr

from .exceptions import EventNotFoundError
from .models import Event


class EventRepository:
    """Repository for Event data access operations."""
    
    def __init__(self, table_name: Optional[str] = None):
        """Initialize with DynamoDB table.
        
        Args:
            table_name: Name of the DynamoDB table. If not provided, uses EVENTS_TABLE_NAME env var.
        """
        self.table_name = table_name or os.environ.get("EVENTS_TABLE_NAME", "EventsTable")
        dynamodb = boto3.resource("dynamodb")
        self.table = dynamodb.Table(self.table_name)
    
    def create(self, event: Event) -> Event:
        """Create a new event.
        
        Args:
            event: Event domain model to persist
            
        Returns:
            The created Event
        """
        item = {
            'eventId': event.event_id,
            'title': event.title,
            'description': event.description,
            'date': event.date,
            'location': event.location,
            'capacity': event.capacity,
            'organizer': event.organizer,
            'status': event.status,
            'createdAt': event.created_at or datetime.utcnow().isoformat(),
            'updatedAt': event.updated_at or datetime.utcnow().isoformat()
        }
        
        self.table.put_item(Item=item)
        
        # Update event with timestamps if they weren't set
        if not event.created_at:
            event.created_at = item['createdAt']
        if not event.updated_at:
            event.updated_at = item['updatedAt']
        
        return event
    
    def get(self, event_id: str) -> Optional[Event]:
        """Get an event by ID.
        
        Args:
            event_id: Unique identifier for the event
            
        Returns:
            Event if found, None otherwise
        """
        response = self.table.get_item(Key={'eventId': event_id})
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        return Event(
            event_id=item['eventId'],
            title=item['title'],
            description=item['description'],
            date=item['date'],
            location=item['location'],
            capacity=item['capacity'],
            organizer=item['organizer'],
            status=item['status'],
            created_at=item.get('createdAt'),
            updated_at=item.get('updatedAt')
        )
    
    def list(self, status: Optional[str] = None) -> List[Event]:
        """List all events, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of Event objects
        """
        if status:
            # Filter by status using scan with filter expression
            response = self.table.scan(
                FilterExpression=Attr('status').eq(status)
            )
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    FilterExpression=Attr('status').eq(status),
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))
        else:
            # Get all events
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Handle pagination
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
        
        return [
            Event(
                event_id=item['eventId'],
                title=item['title'],
                description=item['description'],
                date=item['date'],
                location=item['location'],
                capacity=item['capacity'],
                organizer=item['organizer'],
                status=item['status'],
                created_at=item.get('createdAt'),
                updated_at=item.get('updatedAt')
            )
            for item in items
        ]
    
    def update(self, event_id: str, updates: Dict[str, Any]) -> Event:
        """Update an event.
        
        Args:
            event_id: Unique identifier for the event
            updates: Dictionary of fields to update
            
        Returns:
            The updated Event
            
        Raises:
            EventNotFoundError: If the event doesn't exist
        """
        # Check if event exists
        if not self.exists(event_id):
            raise EventNotFoundError(f"Event with ID {event_id} not found")
        
        # Add updated timestamp
        updates['updatedAt'] = datetime.utcnow().isoformat()
        
        # Build update expression
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
        expression_attribute_names = {f"#{k}": k for k in updates.keys()}
        expression_attribute_values = {f":{k}": v for k, v in updates.items()}
        
        response = self.table.update_item(
            Key={'eventId': event_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues='ALL_NEW'
        )
        
        item = response['Attributes']
        return Event(
            event_id=item['eventId'],
            title=item['title'],
            description=item['description'],
            date=item['date'],
            location=item['location'],
            capacity=item['capacity'],
            organizer=item['organizer'],
            status=item['status'],
            created_at=item.get('createdAt'),
            updated_at=item.get('updatedAt')
        )
    
    def delete(self, event_id: str) -> None:
        """Delete an event.
        
        Args:
            event_id: Unique identifier for the event
            
        Raises:
            EventNotFoundError: If the event doesn't exist
        """
        # Check if event exists
        if not self.exists(event_id):
            raise EventNotFoundError(f"Event with ID {event_id} not found")
        
        self.table.delete_item(Key={'eventId': event_id})
    
    def exists(self, event_id: str) -> bool:
        """Check if an event exists.
        
        Args:
            event_id: Unique identifier for the event
            
        Returns:
            True if the event exists, False otherwise
        """
        return self.get(event_id) is not None
