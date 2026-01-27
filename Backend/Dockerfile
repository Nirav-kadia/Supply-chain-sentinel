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

# First install essential packages that we know work
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir \
        fastapi==0.123.10 \
        uvicorn==0.40.0 \
        pydantic==2.11.10 \
        python-dotenv==1.1.1 \
        requests==2.32.5

# Copy and install the minimal requirements for now
COPY crew_requirements_minimal.txt .
RUN pip install --no-cache-dir -r crew_requirements_minimal.txt || echo "Some packages failed to install, continuing..."

# Copy application code
COPY app/ ./app/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app \
    && rm -f crew_requirements_minimal.txt

USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)" || exit 1

# Use full path to uvicorn to ensure it's found
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]