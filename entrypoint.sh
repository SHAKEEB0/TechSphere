#!/bin/sh
set -e

echo "========================================="
echo "Starting TechSphere deployment..."
echo "========================================="

echo "Checking Django..."
python -c "import django; print('Django version:', django.get_version())"

echo "========================================="
echo "Showing blog migrations..."
echo "========================================="
python manage.py showmigrations blog

echo "========================================="
echo "Running migrations..."
echo "========================================="
python manage.py migrate --noinput

echo "========================================="
echo "Collecting static files..."
echo "========================================="
python manage.py collectstatic --noinput

echo "========================================="
echo "Starting Gunicorn..."
echo "========================================="

exec "$@"