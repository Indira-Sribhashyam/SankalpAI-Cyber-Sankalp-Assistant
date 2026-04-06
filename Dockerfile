FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Ensure static directory exists
RUN mkdir -p static

EXPOSE 8000

# Cloud platform typically provides PORT env var
CMD ["sh", "-c", "uvicorn assistant_api:app --host 0.0.0.0 --port ${PORT:-8000}"]
