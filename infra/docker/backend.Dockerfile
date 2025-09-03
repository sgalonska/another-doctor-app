FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base AS development

# Copy requirements first for better layer caching
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    black \
    ruff \
    mypy

# Copy application code
COPY apps/backend ./apps/backend
COPY packages/py-utils ./packages/py-utils

# Install shared utilities in development mode
RUN pip install -e ./packages/py-utils

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Install additional production dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install production-specific packages
RUN pip install --no-cache-dir \
    gunicorn \
    uvicorn[standard] \
    google-cloud-sql-python-connector \
    google-cloud-storage \
    google-cloud-secret-manager \
    psycopg2-binary

# Copy application code
COPY apps/backend ./apps/backend
COPY packages/py-utils ./packages/py-utils

# Install shared utilities
RUN pip install ./packages/py-utils

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Production startup script
COPY infra/docker/scripts/backend-start.sh /app/start.sh
USER root
RUN chmod +x /app/start.sh
USER appuser

CMD ["/app/start.sh"]