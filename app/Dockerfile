FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY domain/ ./domain/
COPY tools/ ./tools/

# Set Python path to include both directories
ENV PYTHONPATH=/app

WORKDIR /app/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
