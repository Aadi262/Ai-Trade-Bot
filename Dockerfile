FROM python:3.12-slim

WORKDIR /app

# Install system deps (for python-magic, asyncpg, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000
