#!/usr/bin/env bash

set -e

LOG_LEVEL='INFO'

if [ "$1" == 'runserver' ]; then
    cd /opt/app
    exec gosu unprivileged python -m gunicorn \
         -t 180 \
         --worker-tmp-dir /dev/shm \
         --access-logfile - \
         --error-logfile - \
         --log-level info \
         --workers 4 \
         --bind 0.0.0.0:8000 \
    config.wsgi:application 
elif [ "$1" == 'celery-worker' ]; then
    cd /opt/app
    exec gosu unprivileged python -m celery -A config worker
elif [ "$1" == 'celery-beat' ]; then
    cd /opt/app
    exec gosu unprivileged python -m celery -A config beat
elif [ "$1" == 'celery-flower' ]; then
    cd /opt/app
    exec gosu unprivileged python -m celery -A config flower
else
    echo "Unknown command: $1"
    exit 1
fi

exec "$@"
