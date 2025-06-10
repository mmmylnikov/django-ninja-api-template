import logging
from typing import Any

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.utils import timezone
from events.models import Booking, Event

from notifications.grpc.client import grpc_client
from notifications.models import (
    Notification,
    NotificationStatus,
    NotificationType,
)


logger = logging.getLogger(__name__)


class NotificationService:  # noqa: WPS214
    @staticmethod
    def create_notification(
        user: User,
        message: str,
        notification_type: NotificationType,
        title: str,
        related_event: Event | None = None,
    ) -> Notification:
        return Notification.objects.create(
            user=user,
            type=notification_type,
            status=NotificationStatus.PENDING,
            title=title,
            message=message,
            related_event=related_event,
        )

    @staticmethod
    def mark_as_sent(notification_id: int) -> Notification | None:
        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return None
        else:
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at', 'updated_at'])
            return notification

    @staticmethod
    def mark_as_read(notification_id: int) -> Notification | None:
        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return None
        else:
            notification.status = NotificationStatus.READ
            notification.save(update_fields=['status', 'updated_at'])
            return notification

    @staticmethod
    def mark_as_failed(
        notification_id: int,
        error_message: str | None = None,
    ) -> Notification | None:
        try:
            notification = Notification.objects.get(id=notification_id)

        except Notification.DoesNotExist:
            return None
        else:
            notification.status = NotificationStatus.FAILED
            if error_message:
                notification.message += f'\n\nError: {error_message}'  # noqa: WPS336
            notification.save(update_fields=['status', 'message', 'updated_at'])
            return notification

    @staticmethod
    def get_user_notifications(
        user_id: int, status: NotificationStatus | None = None
    ) -> QuerySet[Notification]:
        query = Notification.objects.filter(user_id=user_id)
        if status:
            query = query.filter(status=status)
        return query.order_by('-created_at')

    @staticmethod
    def get_pending_notifications() -> QuerySet[Notification]:
        return Notification.objects.filter(
            status=NotificationStatus.PENDING
        ).order_by('created_at')

    @staticmethod
    def create_event_reminder(
        user: User, event: Event, custom_message: str | None = None
    ) -> Notification:
        title = f'Reminder: {event.title}'
        message = (
            custom_message or f"The event will start in an hour '{event.title}'"
        )
        return NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.EVENT_REMINDER,
            related_event=event,
        )

    @staticmethod
    def create_booking_confirmation(
        user: User, event: Event, seats: int
    ) -> Notification:
        title = f'Booking confirmed: {event.title}'
        message = f"You have successfully booked {seats} for '{event.title}'"
        return NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.BOOKING_CONFIRMATION,
            related_event=event,
        )

    @staticmethod
    def create_event_cancelled_notification(
        user: User, event: Event
    ) -> Notification:
        title = f'The event has been cancelled: {event.title}'
        message = f"Unfortunately, '{event.title}' has been cancelled."

        return NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.EVENT_CANCELLED,
            related_event=event,
        )

    @staticmethod
    def create_event_updated_notification(
        user: User, event: Event, changes: dict[str, Any] | None = None
    ) -> Notification:
        title = f'The event has been updated: {event.title}'
        message = f"Information about '{event.title}' has been updated."
        if changes:
            message += '\n\nChanges:'  # noqa: WPS336
            for field, new_value in changes.items():  # noqa: WPS519
                message += f'\n- {field}: {new_value}'  # noqa: WPS336

        return NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type=NotificationType.EVENT_UPDATED,
            related_event=event,
        )

    @staticmethod
    def notify_all_participants(
        event: Event,
        notification_type: NotificationType,
        title: str,
        message: str,
    ) -> list[Notification]:
        bookings = Booking.objects.filter(event=event).select_related('user')
        notifications = []
        for booking in bookings:
            notification = NotificationService.create_notification(
                user=booking.user,
                title=title,
                message=message,
                notification_type=notification_type,
                related_event=event,
            )
            notifications.append(notification)
        return notifications


def send_fake_notification(notification: Notification) -> bool:
    logger.debug(
        'NOTIFICATION TO %s: %s',
        notification.user,
        notification.title,
    )
    logger.debug('MESSAGE: %s', notification.message)
    try:
        NotificationService.mark_as_sent(notification.id)
    except Exception as error:
        logger.debug('Error sending notification: %s', error)
        NotificationService.mark_as_failed(notification.id, str(error))
        return False
    else:
        return True


def send_grpc_notification(notification: Notification) -> bool:
    try:
        is_send = grpc_client.send_notification(
            notification_id=notification.pk,
            user_id=notification.user.pk,
            notification_type=notification.type,
            title=notification.title,
            message=notification.message,
        )
    except Exception as error:
        NotificationService.mark_as_failed(notification.id, str(error))
        return False
    else:
        if is_send:
            NotificationService.mark_as_sent(notification.id)
            return True
        NotificationService.mark_as_failed(notification.id)
        return False
