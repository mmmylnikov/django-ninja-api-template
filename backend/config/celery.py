import os

from celery import Celery
from celery.schedules import crontab
from kombu import Exchange, Queue


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('api_events_celery')
app.config_from_object('django.conf:settings', force=True, namespace='CELERY')

DEFAULT = 'default'
URGENT = 'urgent'


app.conf.task_default_queue = DEFAULT
app.conf.task_queues = (
    Queue(DEFAULT, Exchange(DEFAULT), routing_key='task.#'),
    Queue(URGENT, Exchange(URGENT), routing_key=f'{URGENT}.#'),
)

app.conf.task_routes = {
    'notifications.tasks.*': {
        'queue': URGENT,
        'routing_key': f'{URGENT}.notification',
    },
    'events.tasks.notify_upcoming_events': {
        'queue': URGENT,
        'routing_key': f'{URGENT}.reminder',
    },
    'events.tasks.finish_expired_events': {
        'queue': DEFAULT,
        'routing_key': 'task.status_update',
    },
}

app.conf.beat_schedule = {
    'notify_upcoming_events': {
        'task': 'events.tasks.notify_upcoming_events',
        'schedule': crontab(minute=0, hour='*'),
    },
    'finish_expired_events': {
        'task': 'events.tasks.finish_expired_events',
        'schedule': crontab(minute=0, hour='*/3'),
    },
}

app.autodiscover_tasks()
