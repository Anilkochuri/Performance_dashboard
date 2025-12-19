#!/usr/bin/env bash
set -e
# Render will inject $PORT automatically. Bind Gunicorn to it.
exec gunicorn --workers 3 --threads 8 --timeout 120 --bind 0.0.0.0:${PORT} app:app
