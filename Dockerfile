FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY data/ ./data/

# Environment
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
