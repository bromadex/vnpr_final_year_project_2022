#!/bin/bash
# VNPR Project Setup Script

set -e

echo "============================================"
echo "  VNPR - Vehicle Number Plate Recognition"
echo "  Setup Script"
echo "============================================"

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your actual credentials before starting!"
fi

# Create necessary directories
mkdir -p media staticfiles logs violation_backups

# Build and start services
echo "Building and starting services..."
docker-compose build
docker-compose up -d db redis

# Wait for database
echo "Waiting for database to be ready..."
sleep 5

# Run migrations
echo "Running database migrations..."
docker-compose run --rm backend python manage.py migrate

# Create superuser
echo ""
echo "============================================"
echo "  Create Admin Account"
echo "============================================"
docker-compose run --rm backend python manage.py createsuperuser

# Collect static files
echo "Collecting static files..."
docker-compose run --rm backend python manage.py collectstatic --noinput

# Start all services
echo "Starting all services..."
docker-compose up -d

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Services are now running:"
echo "  Frontend Dashboard: http://localhost"
echo "  Backend API:        http://localhost:8000/api/"
echo "  Admin Panel:        http://localhost:8000/admin/"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop:      docker-compose down"
echo ""
