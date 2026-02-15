# bedrock-rag-eval
Containerized local RAG service with ingestion, hybrid retrieval, citations, evaluation tooling, and an agentic research endpoint.

## Quick Start

```bash
# 1. Copy env template and add your Groq API key (optional — works without it)
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here

# 2. Build and start
docker compose up --build

# 3. In another terminal — ingest documents first
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "data/corpus_raw"}'

# 4. Query the service
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What metrics does Bedrock provide?"}'
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

### Query with citations
```bash
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What metrics does Amazon Bedrock provide for monitoring?"}' | python3 -m json.tool
```
Expected response:
```json
{
    "answer": "Amazon Bedrock provides several metrics including Invocations, InvocationLatency, InvocationClientErrors, InvocationServerErrors, InvocationThrottles, InputTokenCount, OutputTokenCount, LegacyModelInvocations, and OutputImageCount. [Chunk 1]",
    "citations": [
        {
            "doc_id": "txt/bedrock_runtime_metrics.txt",
            "chunk_id": "txt/bedrock_runtime_metrics.txt#00000"
        }
    ],
    "retrieved": null
}
```

### Query with retrieved context (debugging)
```bash
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Does Bedrock support streaming?", "include_context": true}' | python3 -m json.tool
```

### Query with no answer
```bash
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the price of AWS Lambda?"}' | python3 -m json.tool
```
Expected response (when question is not in corpus):
```json
{
    "answer": "I don't know based on the provided documents.",
    "citations": [],
    "retrieved": null
}
```

### Smoke tests
```bash
./scripts/smoke_ingest.sh
./scripts/smoke_query.sh
```

## Configuration

Key environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | _(empty)_ | Groq API key for LLM generation. Get from [console.groq.com](https://console.groq.com/keys). If empty, returns retrieval-only fallback. |
| `TOP_K` | `4` | Number of chunks to retrieve per query |
| `MAX_CHUNKS_PER_DOC` | `2` | Max chunks from same document (diversity) |
| `NO_ANSWER_MIN_SCORE` | `0.3` | Minimum similarity threshold for answering |
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `120` | Overlap between chunks |
