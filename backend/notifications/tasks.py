from celery import shared_task
from django.contrib.auth.models import User
from events.models import Booking, Event

from notifications.services import (
    NotificationService,
    send_fake_notification,
    send_grpc_notification,
)


@shared_task(name='notifications.tasks.process_pending_notifications')
def process_pending_notifications() -> str:
    """Sends all pending notifications."""
    pending_notifications = NotificationService.get_pending_notifications()

    success_count = 0
    failure_count = 0

    for notification in pending_notifications:
        if send_fake_notification(notification):
            success_count += 1
        else:
            failure_count += 1

    return (
        'Processed notifications: '
        + '{success} successful, {failure} failed'.format(
            success=success_count, failure=failure_count
        )
    )


@shared_task(name='notifications.tasks.send_booking_confirmation')
def send_booking_confirmation(booking_id: int) -> bool:
    try:
        booking = Booking.objects.select_related('user', 'event').get(
            id=booking_id
        )
    except Booking.DoesNotExist:
        return False
    else:
        notif = NotificationService.create_booking_confirmation(
            user=booking.user,
            event=booking.event,
            seats=booking.seats,
        )
        send_grpc_notification(notif)
        return True


@shared_task(name='notifications.tasks.send_event_cancelled')
def send_event_cancelled(user_id: int, event_id: int) -> bool:
    user = User.objects.get(pk=user_id)
    event = Event.objects.get(pk=event_id)
    try:
        notif = NotificationService.create_event_cancelled_notification(
            user=user, event=event
        )
    except Exception:
        return False
    else:
        send_fake_notification(notif)
        return True


@shared_task(name='notifications.tasks.event_reminder')
def event_reminder(event_id: int) -> bool:
    event = Event.objects.get(pk=event_id)
    bookings = Booking.objects.filter(event=event).select_related('user')
    try:
        for booking in bookings:
            notif = NotificationService.create_event_reminder(
                user=booking.user, event=event
            )
            send_fake_notification(notif)
    except Exception:
        return False
    else:
        return True
