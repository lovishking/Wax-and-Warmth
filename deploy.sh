#!/bin/bash

# Vercel deployment script
echo "Starting Vercel deployment preparation..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r backend/requirements.txt

# Run Django management commands
echo "Running Django migrations..."
cd backend
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Deployment preparation complete!"