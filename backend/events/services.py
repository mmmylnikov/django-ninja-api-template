from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import (  # noqa: WPS347
    Case,
    ExpressionWrapper,
    F,
    Func,
    IntegerField,
    QuerySet,
    Value,
    When,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja.errors import AuthorizationError, HttpError
from notifications.tasks import send_booking_confirmation, send_event_cancelled

from events.models import Booking, Event, EventStatus
from events.schemas import EventIn


class AbsEpoch(Func):
    function = 'ABS'
    template = 'ABS(EXTRACT(EPOCH FROM %(expressions)s)) / 60'


class EventService:  # noqa: WPS214
    @staticmethod
    def get_sorted_events() -> QuerySet[Event]:
        """
        Get custom-sorted events
        1. Current (UPCOMING), start_time
        2. Past (COMPLETED and CANCELLED), -start_time
        """
        return Event.objects.annotate(
            status_order=Case(
                When(status=EventStatus.UPCOMING, then=Value(0)),
                When(status=EventStatus.COMPLETED, then=Value(1)),
                When(status=EventStatus.CANCELLED, then=Value(1)),
                output_field=IntegerField(),
            ),
            start_time_order=AbsEpoch(
                ExpressionWrapper(
                    expression=F('start_time') - timezone.now(),  # type: ignore
                    output_field=IntegerField(),
                )
            ),
        ).order_by(
            'status_order',
            'start_time_order',
        )

    @staticmethod
    def get_event_by_id(event_id: int) -> Event:
        return get_object_or_404(Event, id=event_id)

    @staticmethod
    def create_event(event_data: EventIn, organizer: User) -> Event:
        """
        Creates a new event with the specified organizer.
        """
        if not organizer.is_staff:
            raise AuthorizationError(
                403, 'Only the organizers can create events.'
            )
        if event_data.start_time < timezone.now():
            raise HttpError(400, "You can't create an event in the past")

        event, created = Event.objects.get_or_create(
            title=event_data.title,
            description=event_data.description,
            start_time=event_data.start_time,
            city=event_data.city,
            seats_total=event_data.seats_total,
            status=EventStatus.UPCOMING,
            organizer=organizer,
        )
        if created:
            return event
        raise HttpError(409, 'Such an event already exists')

    @staticmethod
    def update_event_status(
        event_id: int, status: str, organizer: User
    ) -> Event:
        """
        Updates the status of the event.
        Only the organizer (who created the event) can change its status.
        """
        event = get_object_or_404(Event, id=event_id)
        if event.organizer_id != organizer.id:
            raise HttpError(
                403, 'Only the event organizer can change its status.'
            )
        if status not in EventStatus:
            raise HttpError(
                400,
                f'Invalid status. Available statuses: {EventStatus.values}',
            )
        event.status = status
        event.save(update_fields=['status', 'updated_at'])
        return event

    @staticmethod
    def delete_event(event_id: int, organizer: User) -> None:
        """
        Deletes the event if:
        1. The user is the organizer of the event
        2. No more than 1 hour has passed since the event was created.
        """
        event = get_object_or_404(Event, id=event_id)

        if event.organizer_id != organizer.id:
            raise HttpError(403, 'Only the organizer can delete the event.')

        time_since_creation = timezone.now() - event.created_at
        if time_since_creation > timedelta(hours=1):
            raise HttpError(
                403,
                'The event can only be deleted within 1 hour after creation.',
            )

        event.delete()

    @classmethod
    def get_booking_available_events(cls) -> QuerySet[Event]:
        """
        Retrieves the Queryset[Events] and filters it
        1. Events have the status of UPCOMING
        2. There are available seats, seats_available > 0
        """
        upcoming_events = cls.get_sorted_events().filter(status='upcoming')
        return upcoming_events.filter(_seats_available__gte=1)  # type: ignore

    @staticmethod
    def create_booking(visitor: User, event_id: int, seats: int = 1) -> Booking:  # noqa: WPS238
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist as error:
            raise HttpError(400, f'{error}') from error

        if event.status not in EventStatus.UPCOMING:
            raise HttpError(400, 'Event is not available for booking')
        if event.seats_available < seats:
            raise HttpError(
                400,
                'Not enough seats available ({seats}/{available})'.format(
                    seats=seats, available=event.seats_available
                ),
            )
        if Booking.objects.filter(user=visitor, event=event).exists():
            raise HttpError(400, 'You have already booked this event')

        booking = Booking.objects.create(user=visitor, event=event, seats=seats)
        send_booking_confirmation.delay(booking.id)
        return booking

    @staticmethod
    def cancel_booking(visitor: User, event_id: int) -> None:
        """Cancels the user's reservation for the specified event."""
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist as error:
            raise HttpError(400, f'{error}') from error
        if event.start_time < timezone.now():
            raise HttpError(400, 'Cannot cancel booking for past events')
        try:
            booking = Booking.objects.get(user=visitor, event=event)
        except Booking.DoesNotExist as error:
            raise HttpError(400, f'{error}') from error
        booking.delete()
        send_event_cancelled.delay(visitor.id, event.id)

    @classmethod
    def get_user_upcoming_events(cls, visitor: User) -> QuerySet[Event]:
        return cls.get_sorted_events().filter(
            bookings__user=visitor,
            start_time__gt=timezone.now(),
            status=EventStatus.UPCOMING,
        )
