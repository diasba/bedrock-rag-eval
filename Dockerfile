FROM python:3.11-slim

WORKDIR /app

# Install API/runtime dependencies only (eval deps stay local)
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

# Pre-download the embedding model so first /ingest is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application code
COPY app/ ./app/

# Copy data directory (corpus)
COPY data/ ./data/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
