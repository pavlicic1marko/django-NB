#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "=== Pulling latest code ==="
git pull

echo "=== Activating virtual environment ==="
source .venv/bin/activate

echo "=== Installing requirements ==="
pip install -r requirements.txt

echo "=== Django production check ==="
python manage.py check --deploy

echo "=== Running migrations ==="
python manage.py migrate

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Checking Nginx configuration ==="
sudo nginx -t

echo "=== Restarting Django ==="
sudo systemctl restart django

echo "=== Reloading Nginx ==="
sudo systemctl reload nginx

echo "=== Deployment completed successfully ==="~