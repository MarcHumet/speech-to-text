# Production Dockerfile for Speech-to-Text Service
# Uses Python 3.11-slim for optimal compatibility with ML dependencies

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libasound2-dev \
    portaudio19-dev \
    libpulse-dev \
    pulseaudio \
    pkg-config \
    curl \
    libxext-dev \
    libx11-dev \
    libxtst-dev \
    libxkbcommon-dev \
    xdotool \
    xclip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies globally
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY stt_service ./stt_service
COPY cli.py config.yaml pyproject.toml ./

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data /app/models

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import stt_service.core.engine; print('OK')" || exit 1

# Default command
CMD ["python", "cli.py", "run"]