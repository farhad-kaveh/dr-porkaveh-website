#!/usr/bin/env bash
set -e
export DJANGO_SETTINGS_MODULE=clinic.settings_production
python manage.py migrate
python manage.py collectstatic --noinput
exec gunicorn clinic.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3} --timeout 60
