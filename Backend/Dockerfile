# Use Python 3.11 slim image as base (matches your venv Python version)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for your venv packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        build-essential \
        libxml2-dev \
        libxslt-dev \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements from your working venv (exact copy minus Windows packages)
COPY crew_requirements_exact.txt .

# Install Python dependencies (exact versions from your working venv)
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r crew_requirements_exact.txt \
    && pip install --no-cache-dir rapidfuzz==3.14.3 \
    && pip cache purge \
    && find /usr/local/lib/python3.11/site-packages -name "*.pyc" -delete \
    && find /usr/local/lib/python3.11/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy application code
COPY app/ ./app/

# Create a non-root user and clean up build dependencies
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app \
    && apt-get purge -y gcc g++ build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm crew_requirements_exact.txt

USER app

# Expose port
EXPOSE 8000

# Health check using requests (since it's in your venv)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)" || exit 1

# Run the application (same as your venv setup)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]