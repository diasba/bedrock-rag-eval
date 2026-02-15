# bedrock-rag-eval
Containerized local RAG service with ingestion, hybrid retrieval, citations, evaluation tooling, and an agentic research endpoint.

## Quick Start

```bash
# 1. Copy env template (optional — defaults work out of the box)
cp .env.example .env

# 2. Build and start
docker compose up --build

# 3. In another terminal — verify the service is running
```

## API Usage

### Health check
```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```
Expected response:
```json
{
    "status": "ok",
    "chroma": "ok"
}
```

### Ingest documents
```bash
curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "data/corpus_raw"}' | python3 -m json.tool
```
Expected response:
```json
{
    "docs_total": 3,
    "docs_ok": 3,
    "docs_failed": 0,
    "chunks_total": 5,
    "chunks_indexed": 5,
    "duration_sec": 1.23,
    "errors": []
}
```

### Smoke test (all-in-one)
```bash
./scripts/smoke_ingest.sh
```
