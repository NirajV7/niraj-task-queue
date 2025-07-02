#!/bin/sh

set -e


until pg_isready -h db -p 5432 -U "user"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

echo "Running database migrations..."
python -m alembic upgrade head

exec "$@"