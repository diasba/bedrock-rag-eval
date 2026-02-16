# bedrock-rag-eval

Containerized local RAG service with ingestion, hybrid retrieval (vector + BM25), cross-encoder reranking, SSE streaming, query caching, a web UI, and a full evaluation pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Docker Container                             │
│                                                                     │
│  ┌──────────┐   ┌───────────┐   ┌────────────┐   ┌──────────────┐ │
│  │  FastAPI  │──▶│  Hybrid   │──▶│  Reranker  │──▶│ Mistral LLM  │ │
│  │  /query   │   │  Retrieval│   │ (optional) │   │  (streaming) │ │
│  │  /stream  │   │ Vec+BM25  │   │ CrossEnc / │   │ mistral-large│ │
│  │  /ingest  │   │           │   │ Cohere     │   │  latest      │ │
│  │  /ui      │   └─────┬─────┘   └────────────┘   └──────────────┘ │
│  └──────────┘         │                                             │
│       │          ┌────▼─────┐                                       │
│       │          │ ChromaDB │  ◄── cosine similarity, persistent    │
│       │          │ (volume) │                                       │
│       │          └──────────┘                                       │
│       │                                                             │
│  ┌────▼─────┐   ┌──────────┐   ┌──────────┐                       │
│  │  Query   │   │ BM25     │   │ Sentence  │                       │
│  │  Cache   │   │ Index    │   │Transformers│                       │
│  │(in-mem)  │   │(in-mem)  │   │all-MiniLM │                       │
│  └──────────┘   └──────────┘   └──────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
         │
    ┌────▼─────────────────────────────────────┐
    │  Eval Runner (host-side)                 │
    │  scripts/run_eval.py                     │
    │  ─ RAGAS + DeepEval (judge mode)         │
    │  ─ Token-overlap heuristics (fallback)   │
    │  ─ Outputs: JSON, CSV, Markdown report   │
    └──────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Copy env template and add your Mistral API key (optional — works without it)
cp .env.example .env
# Edit .env and set MISTRAL_API_KEY=your_key_here

# 2. Build and start
docker compose up --build -d

# 3. Ingest documents
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "data/corpus_raw"}'

# 4. Open the web UI
open http://localhost:8000/ui

# 5. Or query via CLI
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What metrics does Bedrock provide?"}' | python3 -m json.tool
```

### Build Corpus from `urls.txt` (recommended)

If `data/corpus_raw/txt/*.txt` is small/empty, build a larger corpus from the URL list:

```bash
python3 scripts/fetch_urls_to_md.py \
  --urls-file data/corpus_raw/html/urls.txt \
  --output-dir data/corpus_raw/md

curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path":"data/corpus_raw"}' | python3 -m json.tool

python3 scripts/chroma_stats.py --api-url http://localhost:8000
```

---

## Project Structure

```
bedrock-rag-eval/
├── app/
│   ├── main.py               # FastAPI: /query, /query/stream, /ingest, /health, /stats, /ui, /cache/clear
│   ├── config.py              # All env-var configuration (hybrid, rerank, cache, chunking, LLM)
│   ├── db/
│   │   └── chroma.py          # ChromaDB persistence: upsert, query, diversity filtering
│   ├── generation/
│   │   └── llm.py             # Mistral LLM: generate_answer, generate_answer_stream, refusal detection
│   ├── ingest/
│   │   ├── loader.py          # Document loader (Markdown, PDF, TXT)
│   │   ├── chunker.py         # Fixed-size character chunking with overlap
│   │   └── embedder.py        # Sentence-transformers embedding (all-MiniLM-L6-v2)
│   ├── retrieval/
│   │   ├── hybrid.py          # BM25 Okapi index + weighted score fusion with vector results
│   │   ├── reranker.py        # Cross-encoder reranking (local) or Cohere API (optional)
│   │   └── cache.py           # Thread-safe in-memory TTL query cache
│   └── static/
│       └── index.html         # Web UI (vanilla HTML/CSS/JS)
├── scripts/
│   ├── run_eval.py            # Evaluation runner (heuristic + judge mode)
│   ├── fetch_urls_to_md.py    # Scrape AWS docs into Markdown corpus
│   ├── check_llm.py           # Mistral API readiness checker
│   ├── chroma_stats.py        # ChromaDB statistics viewer
│   ├── smoke_ingest.sh        # Ingestion smoke test
│   └── smoke_query.sh         # Query smoke test
├── tests/
│   └── test_query.py          # 36 unit tests (query, retrieval, cache, streaming, hybrid, UI)
├── data/
│   ├── corpus_raw/            # Source documents (md, pdf, txt)
│   └── eval/
│       └── eval_dataset.jsonl # 22 evaluation question-answer-context triplets
├── reports/                   # Generated eval outputs (gitignored)
├── Dockerfile                 # Python 3.11-slim with pre-downloaded embedding model
├── docker-compose.yml         # Single-service stack with named ChromaDB volume
├── requirements-api.txt       # Runtime dependencies (Docker image)
├── requirements.txt           # Full dependencies (including eval tools)
├── .env.example               # Documented env-var template
└── .gitignore
```

---

## API Reference

### `GET /health`

Returns service status, ChromaDB connectivity, and LLM readiness.

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

```json
{
    "status": "ok",
    "chroma": "ok",
    "llm_ready": true,
    "llm_reason": "Mistral API operational (model: mistral-large-latest)"
}
```

### `GET /stats`

Returns ChromaDB collection statistics.

```bash
curl -s http://localhost:8000/stats | python3 -m json.tool
```

```json
{
    "total_chunks": 645,
    "by_content_type": {"md": 625, "pdf": 16, "txt": 4},
    "top_docs": [{"doc_id": "md/what-is-bedrock.html-abc.md", "chunks": 44}],
    "md_count": 625
}
```

### `POST /ingest`

Ingests documents from a folder. Accepts optional chunk parameter overrides.

```bash
curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "data/corpus_raw"}' | python3 -m json.tool
```

Request body:

| Field | Type | Default | Description |
|---|---|---|---|
| `path` | string | _(required)_ | Folder path to ingest |
| `chunk_size` | int | `800` | Characters per chunk (clamped to [100, 4000]) |
| `chunk_overlap` | int | `120` | Overlap between chunks (clamped to [0, chunk_size/2]) |

```json
{
    "docs_total": 35,
    "docs_ok": 35,
    "docs_failed": 0,
    "chunks_total": 645,
    "chunks_indexed": 645,
    "duration_sec": 12.34,
    "errors": []
}
```

After ingestion the BM25 index is automatically rebuilt if hybrid retrieval is enabled.

### `POST /query`

Answers a question using hybrid retrieval + LLM generation with citations.

```bash
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What metrics does Amazon Bedrock provide?"}' | python3 -m json.tool
```

Request body:

| Field | Type | Default | Description |
|---|---|---|---|
| `question` | string | _(required)_ | Natural language question |
| `top_k` | int | `6` | Number of chunks to retrieve |
| `include_context` | bool | `false` | Include retrieved chunks in response (debug mode) |

```json
{
    "answer": "Amazon Bedrock provides metrics including Invocations, InvocationLatency, InvocationClientErrors, InvocationServerErrors, InvocationThrottles, InputTokenCount, OutputTokenCount, LegacyModelInvocations, and OutputImageCount [Chunk 1].",
    "citations": [
        {"doc_id": "txt/bedrock_runtime_metrics.txt", "chunk_id": "txt/bedrock_runtime_metrics.txt#00000"}
    ],
    "retrieved": null,
    "cache_hit": null
}
```

When `include_context=true`, the response also contains:
- `retrieved` — array of chunks with `doc_id`, `chunk_id`, `score`, `text`, `vector_score`, `keyword_score`
- `retrieved_count`, `max_score`, `gate_reason` debug fields

**No-answer contract** — when the question is unanswerable:
```json
{"answer": null, "citations": [], "retrieved": null}
```

### `POST /query/stream`

Streams answer tokens via Server-Sent Events. Same request body as `/query`.

```bash
curl -N -X POST http://localhost:8000/query/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Amazon Bedrock?"}'
```

SSE events:

| Event | Payload | Description |
|---|---|---|
| `token` | `{"token": "..."}` | Partial answer text |
| `done` | `{"answer": "...", "citations": [...]}` | Final result |
| `cached` | Full response with `cache_hit: true` | Cache hit (no streaming) |

### `GET /ui`

Serves the built-in web interface at [http://localhost:8000/ui](http://localhost:8000/ui).

Features:
- Question input with Ctrl/⌘+Enter shortcut
- Toggle between streaming and regular mode
- Optional retrieved-context display with score breakdown (vector + keyword)
- Citation badges
- Cache-hit indicator

### `POST /cache/clear`

Clears the in-memory query cache. Returns `{"cleared": N}`.

```bash
curl -s -X POST http://localhost:8000/cache/clear | python3 -m json.tool
```

---

## Configuration

All settings are configured via environment variables (`.env` file). See `.env.example` for the full template.

### Core

| Variable | Default | Description |
|---|---|---|
| `MISTRAL_API_KEY` | _(empty)_ | Mistral API key. Get from [console.mistral.ai](https://console.mistral.ai/api-keys). If empty, LLM returns null answers. |
| `MISTRAL_MODEL` | `mistral-large-latest` | Primary Mistral model |
| `MISTRAL_TEMPERATURE` | `0.0` | LLM temperature |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `CHROMA_DIR` | `./chroma` | ChromaDB persistence directory |
| `CHROMA_COLLECTION` | `bedrock_docs` | ChromaDB collection name |

### Chunking

| Variable | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `120` | Overlap between consecutive chunks |
| `MIN_DOC_LENGTH` | `200` | Skip documents shorter than this |

These can also be overridden per-ingest via the `chunk_size` and `chunk_overlap` fields in the `POST /ingest` request body. Values are clamped: `chunk_size` ∈ [100, 4000], `chunk_overlap` ∈ [0, chunk_size/2].

### Retrieval

| Variable | Default | Description |
|---|---|---|
| `TOP_K` | `4` | Number of chunks to retrieve per query |
| `MAX_CHUNKS_PER_DOC` | `2` | Max chunks from the same document (diversity) |
| `NO_ANSWER_MIN_SCORE` | `0.3` | Minimum similarity threshold |

### Multi-Hop Retrieval

| Variable | Default | Description |
|---|---|---|
| `MULTIHOP_POOL_SIZE` | `32` | Candidate pool size before final multi-hop selection |
| `MULTIHOP_MAX_CHUNKS_PER_DOC` | `1` | Max chunks per document for multi-hop final contexts |
| `MULTIHOP_MIN_INTENT_MATCHES` | `1` | Minimum intent matches required to keep a chunk in multi-hop pool |

### Hybrid Retrieval

| Variable | Default | Description |
|---|---|---|
| `HYBRID_ENABLED` | `true` | Enable BM25 keyword search fused with vector similarity |
| `HYBRID_VECTOR_WEIGHT` | `0.7` | Weight for vector (cosine) scores in fusion |
| `HYBRID_KEYWORD_WEIGHT` | `0.3` | Weight for BM25 keyword scores in fusion |

When enabled, an in-memory BM25 Okapi index is built from all ChromaDB documents on startup and after each `/ingest`. The retrieval pipeline:

1. **Vector search** — ChromaDB cosine similarity (top_k × 3 candidates)
2. **BM25 keyword search** — term-frequency scoring over the same corpus
3. **Weighted fusion** — `fused = vector_weight × v + keyword_weight × k` (BM25 scores min-max normalised to [0, 1])
4. **Diversity filter** — max `MAX_CHUNKS_PER_DOC` chunks per document

Set `HYBRID_ENABLED=false` to disable and use pure vector retrieval.

### Reranking

| Variable | Default | Description |
|---|---|---|
| `RERANK_ENABLED` | `false` | Enable reranking after retrieval |
| `RERANK_PROVIDER` | `local` | `local` (cross-encoder) or `cohere` (API) |
| `RERANK_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Local cross-encoder model |
| `COHERE_API_KEY` | _(empty)_ | Cohere API key (only when `RERANK_PROVIDER=cohere`) |

Reranking reorders retrieved chunks by cross-encoder relevance without changing the original similarity scores (used by the confidence gate). Falls back gracefully to the original order on any error.

- **Local** — uses `sentence-transformers` CrossEncoder (already bundled). Model is downloaded on first use (~23 MB). No API key needed.
- **Cohere** — requires `pip install cohere` and a free API key from [dashboard.cohere.com](https://dashboard.cohere.com).

### Query Cache

| Variable | Default | Description |
|---|---|---|
| `QUERY_CACHE_ENABLED` | `true` | Enable in-memory query result caching |
| `QUERY_CACHE_TTL_SEC` | `300` | Cache entry time-to-live in seconds |

Cache key is derived from the normalised question text + `top_k` + `include_context`. Repeated identical queries return instantly with `cache_hit: true`. The cache is thread-safe, bounded at 2048 entries, and auto-evicts expired entries. Clear manually via `POST /cache/clear`.

---

## Pre-flight Checks

> **Important:** These scripts query the **running API container** by default,
> so they test the same ChromaDB and LLM configuration that `/query` uses.
> Add `--local` to check the host environment instead.

### Check Mistral LLM Readiness

```bash
python3 scripts/check_llm.py                            # via API (default)
python3 scripts/check_llm.py --api-url http://host:8000  # custom URL
python3 scripts/check_llm.py --local                     # host-side check
```

```
✅  Mistral LLM ready — Mistral API operational (model: mistral-large-latest)
```

### ChromaDB Collection Statistics

```bash
python3 scripts/chroma_stats.py                            # via API (default)
python3 scripts/chroma_stats.py --api-url http://host:8000
python3 scripts/chroma_stats.py --local                    # host-side check
```

```
ChromaDB Collection Statistics
========================================
Total chunks: 645
By content type:
     md: 625
    pdf:  16
    txt:   4
```

### Smoke Tests

```bash
./scripts/smoke_ingest.sh
./scripts/smoke_query.sh
```

---

## Evaluation

### Dataset

The evaluation dataset at `data/eval/eval_dataset.jsonl` contains **22 question–answer–context triplets**:

| Category | Count | Purpose |
|---|---|---|
| **Factual** | 8 | Clear, unambiguous questions with direct answers |
| **Multi-hop** | 4 | Require synthesizing info across multiple chunks |
| **Paraphrase** | 6 | Same question asked in different wording than the source |
| **No-answer** | 4 | Questions with no answer in the corpus (hallucination resistance) |

### Evaluation Modes

| Mode | Trigger | Metrics | Reliability |
|---|---|---|---|
| **Heuristic-only** (default) | No `MISTRAL_API_KEY` | Token-overlap heuristics for all 5 metrics | Always succeeds — no external calls |
| **Judge mode** | `MISTRAL_API_KEY` set + container LLM ready | RAGAS LLM-judge + DeepEval GEval via Mistral | Falls back to heuristics per-metric on failure |

> **Key guarantee:** Report artifacts are **always** generated regardless of mode or judge failures. The `metrics_source` field (`"judge"`, `"mixed"`, or `"heuristic"`) reflects what actually happened.

> **Split-brain prevention:** The eval runner queries the container's `/health` and `/stats` endpoints for all pre-flight checks — it never reads the host's local ChromaDB or Mistral config.

### Running Evaluation

```bash
# 1. Ensure the service is running with ingested data
docker compose up --build -d
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "data/corpus_raw"}'

# 2a. Heuristic-only (no keys required)
pip install httpx
python3 scripts/run_eval.py \
  --dataset data/eval/eval_dataset.jsonl \
  --api-url http://localhost:8000

# 2b. Judge mode (higher-quality metrics)
pip install ragas deepeval datasets langchain-openai
MISTRAL_API_KEY=... python3 scripts/run_eval.py \
  --dataset data/eval/eval_dataset.jsonl \
  --api-url http://localhost:8000

# 2c. Strict mode (fail if Mistral is not operational)
python3 scripts/run_eval.py \
  --dataset data/eval/eval_dataset.jsonl \
  --api-url http://localhost:8000 \
  --require-llm

# 3. View the report
cat reports/eval_report.md
```

### Output Artifacts

| File | Description |
|---|---|
| `reports/eval_results.json` | Machine-readable aggregate + per-question scores with metadata (`judge_mode`, `llm_enabled`, `metrics_source`, `chroma_stats`) |
| `reports/per_question_results.csv` | Spreadsheet-friendly per-question breakdown |
| `reports/eval_report.md` | Full Markdown report with mode banner, failure analysis, and improvement suggestions |

### Metrics

| Metric | Heuristic | Judge (Mistral) | What It Measures |
|---|---|---|---|
| Context Precision | Token-Jaccard overlap | RAGAS LLM-judge | Are the retrieved chunks actually relevant? |
| Context Recall | Token-recall coverage | RAGAS LLM-judge | Does retrieval find all needed chunks? |
| Faithfulness | Token-precision (answer vs context) | RAGAS LLM-judge | Is the answer grounded in context (no hallucination)? |
| Answer Relevancy | Token-overlap (question vs answer) | RAGAS LLM-judge | Does the answer address the question? |
| Answer Correctness | Token-overlap F1 | DeepEval GEval | Does the answer match the ground truth? |

---

## Technical Details

### Retrieval Pipeline

```
Query
  │
  ▼
Embed (all-MiniLM-L6-v2)
  │
  ├──▶ Vector Search (ChromaDB cosine, top_k × 3 candidates)
  │
  ├──▶ [if HYBRID_ENABLED] BM25 Keyword Search (in-memory index)
  │         │
  ▼         ▼
  Weighted Score Fusion ── fused = 0.7 × vector + 0.3 × keyword
  │
  ├──▶ [if RERANK_ENABLED] Cross-Encoder Rerank
  │
  ▼
  Diversity Filter (max N chunks per doc_id)
  │
  ▼
  Content-Type Balancing (cap PDF chunks when txt/md exist)
  │
  ▼
  top_k Final Chunks ──▶ LLM Generation (Mistral, with streaming support)
  │
  ▼
  Answer + [Chunk N] Citations
```

### Content-Type Balancing

To reduce PDF dominance in retrieval (PDF documents produce many more chunks):
- When txt/md chunks exist, PDF chunks are capped at **1** per query
- Exception: queries containing **IAM / policy / role** keywords bypass the cap

### No-Answer Contract

The system has a multi-layer refusal detection pipeline:

1. **LLM layer** (`llm.py`) — 12 regex patterns catch "I don't know", "insufficient context", etc. → returns `answer=None`
2. **API layer** (`main.py`) — 11 patterns + confidence gate (similarity score + token overlap) → null or extractive fallback
3. **Eval layer** (`run_eval.py`) — normalises leftover refusal strings to `None` before scoring

**Guarantee:** when a question is unanswerable, the response is always:
```json
{"answer": null, "citations": []}
```

No placeholder strings like "LLM unavailable" or "insufficient context" ever appear.

### Confidence Gate

When the LLM responds with a refusal ("I don't know") but retrieval confidence is high:
- **Low confidence** (score < 0.55 AND overlap < 0.30) → return `null`
- **High confidence** → extract a short answer from the top chunk instead of returning null

---

## Testing

```bash
python3 -m pytest tests/test_query.py -q
```

**36 tests** covering:

| Area | Tests |
|---|---|
| Answerable queries with citations | 2 |
| No-answer contract (empty retrieval, low confidence, refusal patterns) | 4 |
| Citation fallback (LLM omits markers) | 1 |
| Debug mode (`include_context`) | 1 |
| Health and stats endpoints | 4 |
| Content-type balancing (PDF cap, IAM bypass, runtime metrics) | 3 |
| Refusal pattern detection (8 parametrised variants) | 3 |
| Query cache (hit/miss/disabled) | 2 |
| Hybrid merge (BM25 boost) | 1 |
| SSE streaming endpoint | 1 |
| Ingest with custom chunk params | 2 |
| Web UI endpoint | 1 |
| LLM unavailable contract | 2 |
| Definition query deep fetch | 1 |

All tests are fully mocked (no models, no network) and run in ~1.5 s.

---

## Docker

```bash
# Build and start
docker compose up --build -d

# View logs
docker compose logs -f rag-api

# Rebuild after code changes
docker compose up --build -d

# Stop
docker compose down

# Stop and remove ChromaDB volume (full reset)
docker compose down -v
```

The container:
- Uses `python:3.11-slim` with pre-downloaded `all-MiniLM-L6-v2` embedding model
- Mounts `./data/` read-only for corpus access
- Persists ChromaDB in a named Docker volume `chroma-data`
- Reads `.env` for all configuration
- Runs on port **8000** via uvicorn
- Includes a healthcheck polling `GET /health` every 30 s
