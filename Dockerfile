# Dockerfile for Fracture Detection AI

# Use official Python runtime as a parent image
# WHY SLIM: Smaller image size, faster deployment, smaller attack surface
FROM python:3.10-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

# Set work directory
WORKDIR $APP_HOME

# Install system dependencies
# WHY THESE:
# - build-essential: for compiling some python packages
# - libgl1-mesa-glx: required for opencv
# - curl: for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user for security
# WHY NON-ROOT: Best practice to prevent privilege escalation attacks
RUN useradd -m appuser && chown -R appuser:appuser $APP_HOME
USER appuser

# Expose port (FastAPI default)
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
