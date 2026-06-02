#!/bin/sh
set -e

# Wait for DB to become available, then run migrations and collectstatic.
# Retry a few times to handle transient DB start timing on managed Postgres.
TRIES=0
MAX_TRIES=10
SLEEP_SECONDS=3

until python -c "import sys, django; print('ok')" 2>/dev/null || [ "$TRIES" -ge "$MAX_TRIES" ]; do
	TRIES=$((TRIES+1))
	echo "Waiting for Django environment... (attempt $TRIES/$MAX_TRIES)"
	sleep $SLEEP_SECONDS
done

# Run migrations and collect static files
echo "Running migrations..."
python manage.py migrate --noinput || echo "migrate failed (will retry on next start)"
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "collectstatic failed"

# Exec the container CMD
exec "$@"
