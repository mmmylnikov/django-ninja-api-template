from django.contrib.auth.models import User
from django.db import models
from events import models as events_models


class NotificationType(models.TextChoices):
    EVENT_REMINDER = 'event_reminder', 'Event Reminder'
    BOOKING_CONFIRMATION = 'booking_confirmation', 'Booking confirmation'
    EVENT_CANCELLED = 'event_cancelled', 'The event has been cancelled'
    EVENT_UPDATED = 'event_updated', 'The event has been updated'


class NotificationStatus(models.TextChoices):
    PENDING = 'pending', 'Awaiting dispatch'
    SENT = 'sent', 'Shipped'
    READ = 'read', 'Readed'
    FAILED = 'failed', 'Sending error'


class Notification(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    type = models.CharField(
        max_length=32,
        choices=NotificationType.choices,
        default=NotificationType.EVENT_REMINDER,
    )
    status = models.CharField(
        max_length=10,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_event = models.ForeignKey(
        events_models.Event,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='notifications',
    )

    def __str__(self) -> str:
        return 'Notification to {user}: {title}'.format(
            user=self.user.username, title=self.title
        )
