#!/bin/bash

# Start the web server and bot (main.py already does this)
# But we also need a Celery worker if we want to use background tasks.
# For now, let's just run main.py as it handles most things in memory.

# If we want a worker:
# celery -A core.celery_app worker --loglevel=info &

python bot/main.py
