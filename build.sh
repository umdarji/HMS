#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies from the nested requirements file
pip install -r myenv/myproject/requirements.txt

# Run collectstatic from the nested project directory
python myenv/myproject/manage.py collectstatic --no-input

# Run migrations from the nested project directory
python myenv/myproject/manage.py migrate
