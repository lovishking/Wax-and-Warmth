#!/bin/bash

# Build script for Vercel deployment
echo "Building project..."

# Install Python dependencies
pip install -r backend/requirements.txt

# Collect static files
cd backend
python manage.py collectstatic --noinput --clear