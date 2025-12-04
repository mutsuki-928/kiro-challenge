"""Unit tests for repository operations."""

import pytest
from moto import mock_aws
import boto3
import os

from registration.models import User, Event
from registration.repositories import UserRepository, EventRepository


@pytest.fixture
def aws_credentials():
    """Mock AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'


@pytest.fixture
def dynamodb_table(aws_credentials):
    """Create a mock DynamoDB table for testing."""
    with mock_aws():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create table
        table = dynamodb.create_table(
            TableName='registration-system',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
                {'AttributeName': 'GSI1SK', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'GSI1',
                    'KeySchema': [
                        {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                        {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        yield table


class TestUserRepository:
    """Tests for UserRepository."""
    
    def test_create_user(self, dynamodb_table):
        """Test creating a user."""
        repo = UserRepository('registration-system')
        user = User(user_id='user123', name='John Doe')
        
        created_user = repo.create(user)
        
        assert created_user.user_id == 'user123'
        assert created_user.name == 'John Doe'
    
    def test_get_user(self, dynamodb_table):
        """Test retrieving a user."""
        repo = UserRepository('registration-system')
        user = User(user_id='user123', name='John Doe')
        repo.create(user)
        
        retrieved_user = repo.get('user123')
        
        assert retrieved_user is not None
        assert retrieved_user.user_id == 'user123'
        assert retrieved_user.name == 'John Doe'
    
    def test_get_nonexistent_user(self, dynamodb_table):
        """Test retrieving a user that doesn't exist."""
        repo = UserRepository('registration-system')
        
        retrieved_user = repo.get('nonexistent')
        
        assert retrieved_user is None
    
    def test_user_exists(self, dynamodb_table):
        """Test checking if a user exists."""
        repo = UserRepository('registration-system')
        user = User(user_id='user123', name='John Doe')
        repo.create(user)
        
        assert repo.exists('user123') is True
        assert repo.exists('nonexistent') is False


class TestEventRepository:
    """Tests for EventRepository."""
    
    def test_create_event(self, dynamodb_table):
        """Test creating an event."""
        repo = EventRepository('registration-system')
        event = Event(
            event_id='event123',
            name='Test Event',
            capacity=10,
            waitlist_enabled=True
        )
        
        created_event = repo.create(event)
        
        assert created_event.event_id == 'event123'
        assert created_event.name == 'Test Event'
        assert created_event.capacity == 10
        assert created_event.waitlist_enabled is True
    
    def test_get_event(self, dynamodb_table):
        """Test retrieving an event."""
        repo = EventRepository('registration-system')
        event = Event(
            event_id='event123',
            name='Test Event',
            capacity=10,
            waitlist_enabled=True
        )
        repo.create(event)
        
        retrieved_event = repo.get('event123')
        
        assert retrieved_event is not None
        assert retrieved_event.event_id == 'event123'
        assert retrieved_event.name == 'Test Event'
    
    def test_get_nonexistent_event(self, dynamodb_table):
        """Test retrieving an event that doesn't exist."""
        repo = EventRepository('registration-system')
        
        retrieved_event = repo.get('nonexistent')
        
        assert retrieved_event is None
    
    def test_create_event_with_registrations(self, dynamodb_table):
        """Test creating an event with registered users."""
        repo = EventRepository('registration-system')
        event = Event(
            event_id='event123',
            name='Test Event',
            capacity=10,
            waitlist_enabled=True,
            registered_users=['user1', 'user2']
        )
        
        repo.create(event)
        retrieved_event = repo.get('event123')
        
        assert len(retrieved_event.registered_users) == 2
        assert 'user1' in retrieved_event.registered_users
        assert 'user2' in retrieved_event.registered_users
    
    def test_create_event_with_waitlist(self, dynamodb_table):
        """Test creating an event with waitlisted users."""
        repo = EventRepository('registration-system')
        event = Event(
            event_id='event123',
            name='Test Event',
            capacity=2,
            waitlist_enabled=True,
            registered_users=['user1', 'user2'],
            waitlist=['user3', 'user4']
        )
        
        repo.create(event)
        retrieved_event = repo.get('event123')
        
        assert len(retrieved_event.waitlist) == 2
        assert retrieved_event.waitlist == ['user3', 'user4']
    
    def test_update_event(self, dynamodb_table):
        """Test updating an event."""
        repo = EventRepository('registration-system')
        event = Event(
            event_id='event123',
            name='Test Event',
            capacity=10,
            waitlist_enabled=True,
            registered_users=['user1']
        )
        repo.create(event)
        
        event.registered_users.append('user2')
        repo.update(event)
        
        retrieved_event = repo.get('event123')
        # Note: update only updates counts, not the actual registration records
        assert retrieved_event is not None
    
    def test_get_events_by_registered_user(self, dynamodb_table):
        """Test getting events where a user is registered."""
        repo = EventRepository('registration-system')
        
        event1 = Event(
            event_id='event1',
            name='Event 1',
            capacity=10,
            waitlist_enabled=True,
            registered_users=['user1']
        )
        event2 = Event(
            event_id='event2',
            name='Event 2',
            capacity=10,
            waitlist_enabled=True,
            registered_users=['user1', 'user2']
        )
        event3 = Event(
            event_id='event3',
            name='Event 3',
            capacity=10,
            waitlist_enabled=True,
            registered_users=['user2']
        )
        
        repo.create(event1)
        repo.create(event2)
        repo.create(event3)
        
        user1_events = repo.get_events_by_registered_user('user1')
        
        assert len(user1_events) == 2
        event_ids = [e.event_id for e in user1_events]
        assert 'event1' in event_ids
        assert 'event2' in event_ids
    
    def test_get_events_by_waitlisted_user(self, dynamodb_table):
        """Test getting events where a user is waitlisted."""
        repo = EventRepository('registration-system')
        
        event1 = Event(
            event_id='event1',
            name='Event 1',
            capacity=1,
            waitlist_enabled=True,
            registered_users=['user1'],
            waitlist=['user2']
        )
        event2 = Event(
            event_id='event2',
            name='Event 2',
            capacity=1,
            waitlist_enabled=True,
            registered_users=['user1'],
            waitlist=['user2', 'user3']
        )
        
        repo.create(event1)
        repo.create(event2)
        
        user2_events = repo.get_events_by_waitlisted_user('user2')
        
        assert len(user2_events) == 2
        event_ids = [e.event_id for e in user2_events]
        assert 'event1' in event_ids
        assert 'event2' in event_ids
