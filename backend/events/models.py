from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Coalesce


class EventManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(
                _seats_booked=Coalesce(
                    models.Sum('bookings__seats'), models.Value(0)
                ),
                _seats_available=models.F('seats_total')
                - Coalesce(models.Sum('bookings__seats'), models.Value(0)),
            )
        )


class EventStatus(models.TextChoices):
    UPCOMING = 'upcoming', 'Ожидается'
    CANCELLED = 'cancelled', 'Отменено'
    COMPLETED = 'completed', 'Завершено'


class Event(models.Model):
    objects = EventManager()  # noqa: WPS110
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    city = models.CharField(max_length=100)
    seats_total = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.UPCOMING,
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        limit_choices_to={'is_staff': True},
    )

    @property
    def seats_available(self) -> int:
        return getattr(self, '_seats_available', 0)

    @property
    def seats_booked(self) -> int:
        return getattr(self, '_seats_booked', 0)

    def __str__(self) -> str:
        return '{title} {start_time}'.format(
            title=self.title,
            start_time=self.start_time.strftime('%d.%m.%y %H:%M'),
        )

    class Meta:
        indexes = (
            models.Index(fields=['start_time']),
            models.Index(fields=['city']),
            models.Index(fields=['status']),
        )


class Booking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='bookings'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='bookings'
    )
    seats = models.PositiveSmallIntegerField(default=1)
    attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self) -> str:
        return '{user} ({seats}) - {event}'.format(
            user=self.user.username,
            event=self.event.title,
            seats=self.seats,
        )
