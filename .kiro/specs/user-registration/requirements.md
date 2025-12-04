# Requirements Document

## Introduction

This document specifies the requirements for a user registration system that enables users to register for events with capacity constraints and waitlist management. The system allows users to create profiles, register for events, and manage their event registrations while respecting event capacity limits.

## Glossary

- **User**: An individual with a unique identifier who can register for events
- **Event**: A scheduled occurrence with a defined capacity limit and optional waitlist
- **Registration**: The act of a user signing up to attend an event
- **Capacity**: The maximum number of users that can be registered for an event
- **Waitlist**: An ordered list of users waiting for availability when an event reaches capacity
- **Registration System**: The software system that manages users, events, and registrations

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to create user profiles with basic information, so that users can be identified and tracked within the system.

#### Acceptance Criteria

1. WHEN a user is created with a userId and name, THEN the Registration System SHALL store the user information
2. WHEN a user is created with a duplicate userId, THEN the Registration System SHALL reject the creation and return an error
3. WHEN a user is created with an empty or whitespace-only name, THEN the Registration System SHALL reject the creation and return an error
4. WHEN a user is created with an empty or whitespace-only userId, THEN the Registration System SHALL reject the creation and return an error

### Requirement 2

**User Story:** As an event organizer, I want to configure events with capacity constraints and optional waitlists, so that I can control attendance and manage overflow demand.

#### Acceptance Criteria

1. WHEN an event is created with a capacity value, THEN the Registration System SHALL enforce that capacity as the maximum number of registered users
2. WHEN an event is created with a capacity less than or equal to zero, THEN the Registration System SHALL reject the creation and return an error
3. WHEN an event is configured with a waitlist enabled, THEN the Registration System SHALL maintain a waitlist for that event
4. WHEN an event is configured without a waitlist, THEN the Registration System SHALL not maintain a waitlist for that event

### Requirement 3

**User Story:** As a user, I want to register for events, so that I can attend events that interest me.

#### Acceptance Criteria

1. WHEN a user registers for an event that has available capacity, THEN the Registration System SHALL add the user to the event's registered users list
2. WHEN a user attempts to register for an event that is at full capacity and has no waitlist, THEN the Registration System SHALL deny the registration and return an error
3. WHEN a user attempts to register for an event that is at full capacity and has a waitlist enabled, THEN the Registration System SHALL add the user to the event's waitlist
4. WHEN a user attempts to register for an event they are already registered for, THEN the Registration System SHALL reject the registration and return an error
5. WHEN a user attempts to register for a non-existent event, THEN the Registration System SHALL reject the registration and return an error

### Requirement 4

**User Story:** As a user, I want to unregister from events, so that I can free up my spot if I can no longer attend.

#### Acceptance Criteria

1. WHEN a registered user unregisters from an event, THEN the Registration System SHALL remove the user from the event's registered users list
2. WHEN a user unregisters from an event with a waitlist that has waiting users, THEN the Registration System SHALL move the first user from the waitlist to the registered users list
3. WHEN a user on a waitlist unregisters from an event, THEN the Registration System SHALL remove the user from the waitlist
4. WHEN a user attempts to unregister from an event they are not registered for or waitlisted for, THEN the Registration System SHALL reject the unregistration and return an error

### Requirement 5

**User Story:** As a user, I want to view all events I am registered for, so that I can keep track of my commitments.

#### Acceptance Criteria

1. WHEN a user requests their registered events, THEN the Registration System SHALL return a list of all events where the user is in the registered users list
2. WHEN a user requests their registered events and they have no registrations, THEN the Registration System SHALL return an empty list
3. WHEN a user requests their registered events, THEN the Registration System SHALL not include events where the user is only on the waitlist

### Requirement 6

**User Story:** As a user, I want to view events I am waitlisted for, so that I know which events I might be able to attend if spots open up.

#### Acceptance Criteria

1. WHEN a user requests their waitlisted events, THEN the Registration System SHALL return a list of all events where the user is on the waitlist
2. WHEN a user requests their waitlisted events and they are not on any waitlists, THEN the Registration System SHALL return an empty list
