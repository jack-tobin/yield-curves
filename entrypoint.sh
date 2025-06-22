#!/bin/bash
HOST="0.0.0.0"
PORT="8000"

# Allow overriding through environment variables
HOST="${DJANGO_HOST:-$HOST}"
PORT="${DJANGO_PORT:-$PORT}"

# Run migrations and collect static files
python -m src.manage migrate
python -m src.manage collectstatic --noinput

gunicorn src.config.wsgi --bind "$HOST:$PORT"
