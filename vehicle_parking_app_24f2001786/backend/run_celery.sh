#!/bin/bash

# Vehicle Parking App - Celery Services Startup Script
# This script helps you run Celery worker and beat scheduler

echo "==================================="
echo "Vehicle Parking App - Celery Setup"
echo "==================================="
echo ""

# Check if Redis is running
echo "Checking if Redis is running..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "✗ Redis is not running!"
    echo "Please start Redis first:"
    echo "  - Ubuntu/Debian: sudo service redis-server start"
    echo "  - macOS: brew services start redis"
    echo "  - Windows: Start redis-server.exe"
    exit 1
fi

echo ""
echo "Choose an option:"
echo "1. Run Celery Worker only"
echo "2. Run Celery Beat (Scheduler) only"
echo "3. Run Both Worker and Beat (recommended)"
echo "4. Run Worker with Beat in same process"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting Celery Worker..."
        celery -A celery_worker.celery worker --loglevel=info
        ;;
    2)
        echo ""
        echo "Starting Celery Beat Scheduler..."
        celery -A celery_worker.celery beat --loglevel=info
        ;;
    3)
        echo ""
        echo "Starting Celery Worker and Beat in separate terminals..."
        echo "Opening Worker in current terminal..."
        echo "Please open a new terminal and run: celery -A celery_worker.celery beat --loglevel=info"
        echo ""
        sleep 2
        celery -A celery_worker.celery worker --loglevel=info
        ;;
    4)
        echo ""
        echo "Starting Celery Worker with Beat scheduler..."
        celery -A celery_worker.celery worker --beat --loglevel=info
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac