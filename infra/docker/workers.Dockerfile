FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for NLP processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY apps/workers/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy models for medical NLP
RUN python -m spacy download en_core_web_sm
RUN pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz

# Copy application code
COPY apps/workers ./workers
COPY packages/py-utils ./packages/py-utils

# Install shared utilities
RUN pip install -e ./packages/py-utils

# Create non-root user
RUN useradd --create-home --shell /bin/bash worker && \
    chown -R worker:worker /app
USER worker

# Health check for worker processes
HEALTHCHECK --interval=60s --timeout=30s --start-period=30s --retries=3 \
    CMD python -c "import redis; r=redis.Redis(host='redis'); r.ping()" || exit 1

CMD ["python", "-m", "rq.worker", "--with-scheduler"]