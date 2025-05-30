#!/bin/bash
    #
HOST="127.0.0.1"
PORT="8000"

# Check for Docker environment
# In Docker, we need to bind to 0.0.0.0 to make the server accessible outside the container
if [ -f "/.dockerenv" ] || [ -n "$DOCKER_CONTAINER" ]; then
    HOST="0.0.0.0"
    echo "Running in Docker environment, binding to $HOST:$PORT"
else
    echo "Running in local environment, binding to $HOST:$PORT"
fi

# Allow overriding through environment variables
HOST="${DJANGO_HOST:-$HOST}"
PORT="${DJANGO_PORT:-$PORT}"

python -m src.manage runserver "$HOST:$PORT"
