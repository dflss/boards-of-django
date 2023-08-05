#!/bin/sh

python manage.py collectstatic --no-input
gunicorn boards_of_django.wsgi:application --workers 2 --bind 0.0.0.0:8000 --reload

exec "$@"
