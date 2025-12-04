"""Repository layer for data access."""

import os
from typing import Optional, List
import boto3
from boto3.dynamodb.conditions import Key

from .models import User, Event
from .exceptions import EntityNotFoundError


class UserRepository:
    """Repository for User data access operations."""
    
    def __init__(self, table_name: Optional[str] = None):
        """Initialize the repository with DynamoDB table.
        
        Args:
            table_name: Name of the DynamoDB table. If None, uses REGISTRATION_TABLE_NAME env var.
        """
        dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name or os.environ.get('REGISTRATION_TABLE_NAME', 'registration-system')
        self.table = dynamodb.Table(self.table_name)
    
    def create(self, user: User) -> User:
        """Create a new user in the database.
        
        Args:
            user: User object to create
            
        Returns:
            The created User object
        """
        item = {
            'PK': f'USER#{user.user_id}',
            'SK': 'METADATA',
            'entity_type': 'user',
            'user_id': user.user_id,
            'name': user.name
        }
        self.table.put_item(Item=item)
        return user
    
    def get(self, user_id: str) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User object if found, None otherwise
        """
        response = self.table.get_item(
            Key={
                'PK': f'USER#{user_id}',
                'SK': 'METADATA'
            }
        )
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        return User(
            user_id=item['user_id'],
            name=item['name']
        )
    
    def exists(self, user_id: str) -> bool:
        """Check if a user exists.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if user exists, False otherwise
        """
        return self.get(user_id) is not None


class EventRepository:
    """Repository for Event data access operations."""
    
    def __init__(self, table_name: Optional[str] = None):
        """Initialize the repository with DynamoDB table.
        
        Args:
            table_name: Name of the DynamoDB table. If None, uses REGISTRATION_TABLE_NAME env var.
        """
        dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name or os.environ.get('REGISTRATION_TABLE_NAME', 'registration-system')
        self.table = dynamodb.Table(self.table_name)
    
    def create(self, event: Event) -> Event:
        """Create a new event in the database.
        
        Args:
            event: Event object to create
            
        Returns:
            The created Event object
        """
        item = {
            'PK': f'EVENT#{event.event_id}',
            'SK': 'METADATA',
            'entity_type': 'event',
            'event_id': event.event_id,
            'name': event.name,
            'capacity': event.capacity,
            'waitlist_enabled': event.waitlist_enabled,
            'registered_count': len(event.registered_users),
            'waitlist_count': len(event.waitlist)
        }
        self.table.put_item(Item=item)
        
        # Store registered users
        for user_id in event.registered_users:
            self._add_registration(event.event_id, user_id)
        
        # Store waitlist
        for position, user_id in enumerate(event.waitlist):
            self._add_to_waitlist(event.event_id, user_id, position)
        
        return event
    
    def get(self, event_id: str) -> Optional[Event]:
        """Get an event by ID.
        
        Args:
            event_id: The event's ID
            
        Returns:
            Event object if found, None otherwise
        """
        # Get event metadata
        response = self.table.get_item(
            Key={
                'PK': f'EVENT#{event_id}',
                'SK': 'METADATA'
            }
        )
        
        if 'Item' not in response:
            return None
        
        item = response['Item']
        
        # Get registered users
        registered_users = self._get_registered_users(event_id)
        
        # Get waitlist
        waitlist = self._get_waitlist(event_id)
        
        return Event(
            event_id=item['event_id'],
            name=item['name'],
            capacity=item['capacity'],
            waitlist_enabled=item['waitlist_enabled'],
            registered_users=registered_users,
            waitlist=waitlist
        )
    
    def update(self, event: Event) -> Event:
        """Update an existing event.
        
        Args:
            event: Event object with updated data
            
        Returns:
            The updated Event object
        """
        # Update metadata
        self.table.update_item(
            Key={
                'PK': f'EVENT#{event.event_id}',
                'SK': 'METADATA'
            },
            UpdateExpression='SET registered_count = :rc, waitlist_count = :wc',
            ExpressionAttributeValues={
                ':rc': len(event.registered_users),
                ':wc': len(event.waitlist)
            }
        )
        
        return event
    
    def get_events_by_registered_user(self, user_id: str) -> List[Event]:
        """Get all events where a user is registered.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of Event objects
        """
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq(f'USER#{user_id}') & Key('GSI1SK').eq('REGISTERED')
        )
        
        events = []
        for item in response.get('Items', []):
            event = self.get(item['event_id'])
            if event:
                events.append(event)
        
        return events
    
    def get_events_by_waitlisted_user(self, user_id: str) -> List[Event]:
        """Get all events where a user is on the waitlist.
        
        Args:
            user_id: The user's ID
            
        Returns:
            List of Event objects
        """
        response = self.table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq(f'USER#{user_id}') & Key('GSI1SK').eq('WAITLISTED')
        )
        
        events = []
        for item in response.get('Items', []):
            event = self.get(item['event_id'])
            if event:
                events.append(event)
        
        return events
    
    def _get_registered_users(self, event_id: str) -> List[str]:
        """Get list of registered user IDs for an event.
        
        Args:
            event_id: The event's ID
            
        Returns:
            List of user IDs
        """
        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(f'EVENT#{event_id}') & Key('SK').begins_with('REG#')
        )
        
        return [item['user_id'] for item in response.get('Items', [])]
    
    def _get_waitlist(self, event_id: str) -> List[str]:
        """Get ordered list of waitlisted user IDs for an event.
        
        Args:
            event_id: The event's ID
            
        Returns:
            List of user IDs in waitlist order
        """
        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(f'EVENT#{event_id}') & Key('SK').begins_with('WAIT#')
        )
        
        # Sort by SK to maintain order
        items = sorted(response.get('Items', []), key=lambda x: x['SK'])
        return [item['user_id'] for item in items]
    
    def _add_registration(self, event_id: str, user_id: str):
        """Add a registration record.
        
        Args:
            event_id: The event's ID
            user_id: The user's ID
        """
        self.table.put_item(
            Item={
                'PK': f'EVENT#{event_id}',
                'SK': f'REG#{user_id}',
                'GSI1PK': f'USER#{user_id}',
                'GSI1SK': 'REGISTERED',
                'entity_type': 'registration',
                'user_id': user_id,
                'event_id': event_id,
                'status': 'registered'
            }
        )
    
    def _add_to_waitlist(self, event_id: str, user_id: str, position: int):
        """Add a user to the waitlist.
        
        Args:
            event_id: The event's ID
            user_id: The user's ID
            position: Position in the waitlist
        """
        self.table.put_item(
            Item={
                'PK': f'EVENT#{event_id}',
                'SK': f'WAIT#{position:05d}#{user_id}',
                'GSI1PK': f'USER#{user_id}',
                'GSI1SK': 'WAITLISTED',
                'entity_type': 'waitlist',
                'user_id': user_id,
                'event_id': event_id,
                'position': position,
                'status': 'waitlisted'
            }
        )
    
    def _remove_registration(self, event_id: str, user_id: str):
        """Remove a registration record.
        
        Args:
            event_id: The event's ID
            user_id: The user's ID
        """
        self.table.delete_item(
            Key={
                'PK': f'EVENT#{event_id}',
                'SK': f'REG#{user_id}'
            }
        )
    
    def _remove_from_waitlist(self, event_id: str, user_id: str):
        """Remove a user from the waitlist.
        
        Args:
            event_id: The event's ID
            user_id: The user's ID
        """
        # Find the waitlist item
        response = self.table.query(
            KeyConditionExpression=Key('PK').eq(f'EVENT#{event_id}') & Key('SK').begins_with('WAIT#')
        )
        
        for item in response.get('Items', []):
            if item['user_id'] == user_id:
                self.table.delete_item(
                    Key={
                        'PK': f'EVENT#{event_id}',
                        'SK': item['SK']
                    }
                )
                break
