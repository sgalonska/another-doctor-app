#!/bin/bash

set -e

echo "🚀 Starting Another Doctor Backend..."

# Wait for database connection
echo "⏳ Waiting for database connection..."
timeout=30
count=0
until pg_isready -h "${DATABASE_HOST:-localhost}" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-postgres}"; do
    if [ $count -ge $timeout ]; then
        echo "❌ Timed out waiting for database"
        exit 1
    fi
    echo "Database not ready, waiting..."
    sleep 1
    count=$((count + 1))
done

echo "✅ Database connection established"

# Run database migrations
echo "🔄 Running database migrations..."
cd /app/apps/backend
alembic upgrade head

echo "✅ Database migrations completed"

# Start the server
echo "🎯 Starting FastAPI server..."

if [ "${ENVIRONMENT}" = "development" ]; then
    echo "Starting in development mode..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting in production mode..."
    exec gunicorn app.main:app \
        -w 4 \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --timeout 30 \
        --keep-alive 5 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --preload \
        --access-logfile - \
        --error-logfile -
fi