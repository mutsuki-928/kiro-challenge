"""Property-based tests for User model.

Feature: user-registration
"""

from hypothesis import given, strategies as st, settings

from registration.models import User
from registration.exceptions import ValidationError


# Feature: user-registration, Property 1: User creation round trip
@settings(max_examples=100)
@given(
    user_id=st.text(min_size=1).filter(lambda s: s.strip()),
    name=st.text(min_size=1).filter(lambda s: s.strip())
)
def test_user_creation_round_trip(user_id, name):
    """
    Property 1: User creation round trip
    
    For any valid userId and name (non-empty, non-whitespace), 
    creating a user should preserve the userId and name values.
    
    Validates: Requirements 1.1
    """
    # Create user with valid inputs
    user = User(user_id=user_id, name=name)
    
    # Verify the user was created with the correct values
    assert user.user_id == user_id
    assert user.name == name


# Strategy for generating whitespace-only strings
@st.composite
def whitespace_strings(draw):
    """Generate strings that are either empty or contain only whitespace."""
    whitespace_chars = [' ', '\t', '\n', '\r']
    length = draw(st.integers(min_value=0, max_value=20))
    if length == 0:
        return ""
    return ''.join(draw(st.lists(st.sampled_from(whitespace_chars), min_size=length, max_size=length)))


# Feature: user-registration, Property 2: Invalid user input rejection
@settings(max_examples=100)
@given(
    invalid_string=whitespace_strings()
)
def test_invalid_user_input_rejection_userid(invalid_string):
    """
    Property 2: Invalid user input rejection (userId)
    
    For any string composed entirely of whitespace or empty string,
    attempting to create a user with that string as userId should be rejected.
    
    Validates: Requirements 1.3, 1.4
    """
    try:
        User(user_id=invalid_string, name="Valid Name")
        assert False, "Expected ValidationError to be raised"
    except ValidationError as e:
        assert "userId cannot be empty" in str(e)


@settings(max_examples=100)
@given(
    invalid_string=whitespace_strings()
)
def test_invalid_user_input_rejection_name(invalid_string):
    """
    Property 2: Invalid user input rejection (name)
    
    For any string composed entirely of whitespace or empty string,
    attempting to create a user with that string as name should be rejected.
    
    Validates: Requirements 1.3, 1.4
    """
    try:
        User(user_id="valid_id", name=invalid_string)
        assert False, "Expected ValidationError to be raised"
    except ValidationError as e:
        assert "name cannot be empty" in str(e)
