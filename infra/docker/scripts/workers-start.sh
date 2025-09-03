#!/bin/bash

set -e

echo "👷 Starting Another Doctor Workers..."

# Wait for Redis connection
echo "⏳ Waiting for Redis connection..."
timeout=30
count=0

# Extract Redis host and port from REDIS_URL
REDIS_HOST=${REDIS_URL#*://}
REDIS_HOST=${REDIS_HOST%:*}
REDIS_PORT=${REDIS_URL##*:}

until redis-cli -h "${REDIS_HOST:-localhost}" -p "${REDIS_PORT:-6379}" ping > /dev/null 2>&1; do
    if [ $count -ge $timeout ]; then
        echo "❌ Timed out waiting for Redis"
        exit 1
    fi
    echo "Redis not ready, waiting..."
    sleep 1
    count=$((count + 1))
done

echo "✅ Redis connection established"

# Wait for database connection (workers need DB access for job processing)
echo "⏳ Waiting for database connection..."
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

# Change to app directory
cd /app/apps/backend

# Start workers
echo "🎯 Starting RQ workers..."

if [ "${ENVIRONMENT}" = "development" ]; then
    echo "Starting workers in development mode..."
    exec python -m rq worker --with-scheduler --url "${REDIS_URL:-redis://localhost:6379}" high default low
else
    echo "Starting workers in production mode..."
    # Start multiple worker processes for better performance
    exec python -m rq worker \
        --with-scheduler \
        --url "${REDIS_URL}" \
        --name "worker-$(hostname)-$$" \
        --worker-class rq.SimpleWorker \
        --job-timeout 300 \
        --result-ttl 3600 \
        --worker-ttl 1800 \
        high default low
fi