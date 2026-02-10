# Use Python 3.11 with CUDA support for GPU acceleration
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    portaudio19-dev \
    libasound2-dev \
    libx11-dev \
    libxext-dev \
    libxtst-dev \
    libxss-dev \
    python3-tk \
    ffmpeg \
    build-essential \
    pkg-config \
    libjack-jackd2-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Create app directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 sttuser && \
    chown -R sttuser:sttuser /app
USER sttuser

# Copy requirements first (for better caching)
COPY --chown=sttuser:sttuser requirements.txt .
COPY --chown=sttuser:sttuser pyproject.toml .

# Create virtual environment and install dependencies
RUN /root/.cargo/bin/uv venv && \
    . .venv/bin/activate && \
    /root/.cargo/bin/uv pip install -r requirements.txt

# Copy application code
COPY --chown=sttuser:sttuser . .

# Install the application
RUN . .venv/bin/activate && \
    /root/.cargo/bin/uv pip install -e .

# Create directories for logs and data
RUN mkdir -p /app/logs /app/data /app/models

# Set proper permissions
RUN chmod +x /app/cli.py

# Expose port for potential web interface
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD . .venv/bin/activate && python -c "import stt_service; print('OK')" || exit 1

# Default command
CMD ["/bin/bash", "-c", "source .venv/bin/activate && python cli.py run"]