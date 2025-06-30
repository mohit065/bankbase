# Start from official Python image
FROM python:3.11-slim

# Set workdir
WORKDIR /code

# Install system dependencies (optional, helpful for SQLite)
RUN apt-get update && apt-get install -y gcc libsqlite3-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY ./app ./app
COPY ./tests ./tests

# Copy .env manually if needed (GitHub Actions will mount it later)
# COPY .env .env

# Set env vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run uvicorn (used in container runs, not CI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
