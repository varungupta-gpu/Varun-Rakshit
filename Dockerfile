# ── Stage 1: Builder ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Final Image ─────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Pre-create runtime output directories
RUN mkdir -p /app/data_processed /app/data

# Copy application code
COPY app/ ./app/
COPY main.py .

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Cloud Run Job entry point
ENTRYPOINT ["python", "main.py"]
