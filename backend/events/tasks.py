from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from notifications.tasks import event_reminder

from events.models import Event, EventStatus


@shared_task(name='events.tasks.finish_expired_events')
def finish_expired_events() -> str:
    updated = Event.objects.filter(
        status=EventStatus.UPCOMING,
        start_time__lte=timezone.now() - timedelta(hours=2),
    ).update(status=EventStatus.COMPLETED)
    return f'Finished {updated} events'


@shared_task(name='events.tasks.notify_upcoming_events')
def notify_upcoming_events(accuracy_minute: int = 5) -> str:
    upcoming_start = timezone.now() + timedelta(hours=1)
    events_to_notify = Event.objects.filter(
        start_time__gte=upcoming_start,
        start_time__lt=upcoming_start + timedelta(minutes=accuracy_minute),
        status=EventStatus.UPCOMING,
    )
    for event in events_to_notify:
        event_reminder.delay(event.id)
    return f'Sent reminders for {events_to_notify.count()} events'
