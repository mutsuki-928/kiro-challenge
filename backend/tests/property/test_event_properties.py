"""Property-based tests for Event model.

Feature: user-registration
"""

from hypothesis import given, strategies as st, settings

from registration.models import Event
from registration.exceptions import ValidationError


# Feature: user-registration, Property 4: Invalid capacity rejection
@settings(max_examples=100)
@given(
    invalid_capacity=st.integers(max_value=0)
)
def test_invalid_capacity_rejection(invalid_capacity):
    """
    Property 4: Invalid capacity rejection
    
    For any integer value less than or equal to zero,
    attempting to create an event with that capacity should be rejected.
    
    Validates: Requirements 2.2
    """
    try:
        Event(
            event_id="event123",
            name="Test Event",
            capacity=invalid_capacity,
            waitlist_enabled=False
        )
        assert False, "Expected ValidationError to be raised"
    except ValidationError as e:
        assert "capacity must be greater than zero" in str(e)
