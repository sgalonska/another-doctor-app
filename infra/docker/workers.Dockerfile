FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for NLP processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base AS development

# Copy requirements from backend (workers share same dependencies)
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional worker dependencies
RUN pip install --no-cache-dir \
    rq \
    celery \
    spacy \
    scispacy

# Install spaCy models for medical NLP
RUN python -m spacy download en_core_web_sm
RUN pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz

# Copy application code
COPY apps/backend ./apps/backend  
COPY packages/py-utils ./packages/py-utils

# Install shared utilities in development mode
RUN pip install -e ./packages/py-utils

# Create non-root user
RUN useradd --create-home --shell /bin/bash worker && \
    chown -R worker:worker /app
USER worker

# Health check for worker processes
HEALTHCHECK --interval=60s --timeout=30s --start-period=30s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis'); r.ping()" || exit 1

# Default command for development
CMD ["python", "-m", "rq", "worker", "--with-scheduler", "--url", "redis://redis:6379"]

# Production stage
FROM base AS production

# Install additional production dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install worker dependencies and GCP packages
RUN pip install --no-cache-dir \
    rq \
    celery \
    spacy \
    scispacy \
    google-cloud-sql-python-connector \
    google-cloud-storage \
    google-cloud-secret-manager \
    psycopg2-binary

# Install spaCy models
RUN python -m spacy download en_core_web_sm
RUN pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz

# Copy application code
COPY apps/backend ./apps/backend
COPY packages/py-utils ./packages/py-utils

# Install shared utilities
RUN pip install ./packages/py-utils

# Create non-root user
RUN useradd --create-home --shell /bin/bash worker && \
    chown -R worker:worker /app
USER worker

# Health check - check both Redis and job processing
HEALTHCHECK --interval=60s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import redis; r=redis.from_url('${REDIS_URL:-redis://localhost:6379}'); r.ping()" || exit 1

# Production startup script
COPY infra/docker/scripts/workers-start.sh /app/start.sh
USER root
RUN chmod +x /app/start.sh
USER worker

CMD ["/app/start.sh"]