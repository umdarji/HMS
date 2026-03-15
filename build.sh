#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run collectstatic
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate
