#!/usr/bin/env bash

echo "Migrate database"
sleep 5
until python3 manage.py migrate
do
  echo "No connection"
  sleep 3
done

echo "Setup database"
python3 create_ranks.py

python3 manage.py collectstatic --no-input

echo "Starting Frisbeer backend on top of gunicorn"
gunicorn server.wsgi:application  --bind 0.0.0.0:8000
