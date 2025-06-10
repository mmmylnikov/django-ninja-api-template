from typing import Literal, cast

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Query, Router

from events.models import Booking, Event
from events.schemas import (
    BookingOut,
    CreateBookingIn,
    EventFilterSchema,
    EventIn,
    EventOut,
    EventStatusUpdateIn,
)
from events.services import EventService


DEFAULT_QUERY = Query(...)

router = Router()


@router.get('/', response=list[EventOut])
def list_events(
    request: HttpRequest,
    filters: EventFilterSchema = DEFAULT_QUERY,
) -> QuerySet[Event]:
    """
    A list of all events sorted by:
    - Current (UPCOMING), start_time
    - Outdated (COMPLETED and CANCELLED), -start_time
    """
    return filters.filter(EventService.get_sorted_events())


@router.get('/upcoming/', response=list[EventOut])
def user_upcoming_events(request: HttpRequest) -> QuerySet[Event]:
    return EventService.get_user_upcoming_events(
        visitor=cast(User, request.user)
    )


@router.get('/{event_id}/', response=EventOut)
def get_event(request: HttpRequest, event_id: int) -> Event:
    """
    Get detailed information about the event by ID.
    """
    return EventService.get_event_by_id(event_id)


@router.post('/', response=EventOut)
def create_event(request: HttpRequest, event_data: EventIn) -> Event:
    """
    Creating a new event.

    Available only for users with organizer rights (is_staff=True).
    """
    return EventService.create_event(
        event_data=event_data,
        organizer=cast(User, request.user),
    )


@router.patch('/{event_id}/status/', response=EventOut)
def update_event_status(
    request: HttpRequest, event_id: int, status_data: EventStatusUpdateIn
) -> Event:
    """
    Event status update.

    Available only to the organizer of this event.
    """
    return EventService.update_event_status(
        event_id=event_id,
        status=status_data.status,
        organizer=cast(User, request.user),
    )


@router.delete('/{event_id}/', response={204: None})
def delete_event(
    request: HttpRequest, event_id: int
) -> tuple[Literal[204], None]:
    """
    Deleting an event.

    Available only to the organizer and only within 1 hour after creation.
    """
    EventService.delete_event(
        event_id=event_id,
        organizer=cast(User, request.user),
    )
    return 204, None


@router.post('/{event_id}/book/', response=BookingOut)
def book_event(
    request: HttpRequest,
    event_id: int,
    booking_data: CreateBookingIn,
) -> Booking:
    """
    Book an event.

    There is only one reservation available for one event.
    """
    return EventService.create_booking(
        visitor=cast(User, request.user),
        event_id=event_id,
        seats=booking_data.seats,
    )


@router.delete('/{event_id}/book/', response={204: None})
def cancel_booking(request: HttpRequest, event_id: int) -> tuple[int, None]:
    """
    Cancel reservation.
    """
    EventService.cancel_booking(
        visitor=cast(User, request.user),
        event_id=event_id,
    )
    return 204, None
