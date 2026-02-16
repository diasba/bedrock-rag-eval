# bedrock-rag-eval

Containerized local RAG service for AWS Bedrock docs with ingestion, hybrid retrieval, grounded answers with citations, and evaluation using RAGAS + DeepEval.

## Requirement Coverage

| Requirement | Status | Evidence |
|---|---|---|
| Containerized service (`docker compose up`) | Done | `docker-compose.yml`, `Dockerfile` |
| Ingest Markdown / PDF / TXT | Done | `POST /ingest`, `app/ingest/loader.py` |
| Fixed-size chunking + local embeddings + ChromaDB | Done | `app/ingest/chunker.py`, `app/ingest/embedder.py`, `app/db/chroma.py` |
| REST API: `/health`, `/ingest`, `/query` | Done | `app/main.py` |
| Grounded answers with `doc_id` + `chunk_id` citations | Done | `app/generation/llm.py`, `app/main.py` |
| No-answer contract (`answer=null`, empty citations) | Done | `/query` response handling in `app/main.py` |
| Evaluation dataset (>=20 rows) | Done | `data/eval/eval_dataset.jsonl` (20 rows) |
| Metrics (Context Precision/Recall, Faithfulness, Relevancy, Correctness) via RAGAS + DeepEval | Done | `scripts/run_eval.py` |
| Evaluation report with aggregate + per-question + failure analysis + improvements | Done | `reports/eval_report.md` |
| README with architecture, setup, tradeoffs, limitations, improvements | Done | this file |

Note: the **agentic research endpoint** is not included (extra credit scope).

---

## Architecture

```text
                   +-----------------------------+
                   |      Host (evaluation)      |
                   | scripts/run_eval.py         |
                   | RAGAS + DeepEval            |
                   +--------------+--------------+
                                  |
                                  v
+-------------------------- Docker Container --------------------------+
| FastAPI app (app/main.py)                                          |
|                                                                     |
|  /ingest  -> loader -> fixed-size chunker -> MiniLM embeddings      |
|                  -> ChromaDB persistent collection                  |
|                                                                     |
|  /query   -> query expansion -> vector search (Chroma)              |
|            -> BM25 hybrid fusion -> rerank (optional)               |
|            -> no-answer gate -> Mistral generation -> citations     |
|                                                                     |
|  /health, /stats, /query/stream, /ui                               |
+---------------------------------------------------------------------+
```

---

## Tech Stack

- Python 3.11
- FastAPI + Uvicorn
- ChromaDB (persistent local vector store)
- sentence-transformers `all-MiniLM-L6-v2` (local embeddings)
- Mistral API (optional for generation and judge mode)
- RAGAS + DeepEval (evaluation)

---

## Project Structure

```text
app/
  main.py                 API endpoints and query pipeline
  config.py               env/config management
  ingest/
    loader.py             load .md/.pdf/.txt and clean text
    chunker.py            fixed-size chunking with overlap
    embedder.py           local embeddings
  db/chroma.py            Chroma persistence + retrieval helpers
  retrieval/              hybrid retrieval, rerank, multihop, cache
  generation/llm.py       Mistral prompting + citation extraction
scripts/
  run_eval.py             end-to-end evaluation runner
  smoke_ingest.sh         ingestion smoke script
  smoke_query.sh          query smoke script
data/
  corpus_raw/             source docs
  eval/eval_dataset.jsonl evaluation dataset (20 rows)
reports/                  generated eval outputs
```

---

## Setup (Fresh Machine)

### 1) Configure environment

```bash
cp .env.example .env
```

Set at least:

```env
MISTRAL_API_KEY=...   # optional for LLM generation/judge mode
```

Secrets are loaded from `.env`; do not commit `.env`.

### 2) Start service

```bash
docker compose up --build -d
```

### 3) Ingest corpus

```bash
curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path":"data/corpus_raw"}' | python3 -m json.tool
```

### 4) Health check

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

---

## API

### `GET /health`

Returns service and Chroma/LLM readiness.

### `POST /ingest`

Request:

```json
{"path":"data/corpus_raw"}
```

Response fields:
- `docs_total`, `docs_ok`, `docs_failed`
- `chunks_total`, `chunks_indexed`
- `duration_sec`
- `errors` (max 10)

### `POST /query`

Request:

```json
{"question":"What is Amazon Bedrock?","top_k":4,"include_context":true}
```

Response:

```json
{
  "answer":"...",
  "citations":[{"doc_id":"...","chunk_id":"..."}],
  "retrieved":[{"doc_id":"...","chunk_id":"...","score":0.0,"text":"..."}]
}
```

**No-answer contract**

If the question is not answerable from corpus:

```json
{"answer":null,"citations":[]}
```

### Additional endpoints

- `POST /query/stream` (SSE streaming)
- `GET /stats` (collection stats)
- `POST /cache/clear`
- `GET /ui` (simple local web UI)

---

## Ingestion + Indexing Design

### Deterministic IDs

- `doc_id`: relative path from ingest root
- `chunk_id`: `<doc_id>#<chunk_index:05d>`

### Stored metadata per chunk

- `doc_id`
- `chunk_id`
- `source_path`
- `content_type`
- `chunk_index`

### Idempotency

Upserts use deterministic `chunk_id` and clean stale IDs per `doc_id`, so re-ingest does not create duplicates.

---

## Retrieval + Generation Design Decisions (Tradeoffs)

1. **Fixed-size chunking (char-based)**
   - Chosen for predictable behavior and fast MVP.
   - Tradeoff: semantic boundaries are imperfect.

2. **Hybrid retrieval (vector + BM25)**
   - Improves precision on keyword-heavy technical questions.
   - Tradeoff: more tuning complexity (weights, diversity caps).

3. **Optional reranking**
   - Improves ordering quality for hard queries.
   - Tradeoff: extra latency and model load.

4. **Strict no-answer contract**
   - Prioritizes hallucination resistance.
   - Tradeoff: can return null on borderline answerable rows.

5. **Citation fallback**
   - If model omits chunk markers, API still returns grounded citations from retrieved chunks.

---

## Evaluation (Part 2)

### Dataset

- File: `data/eval/eval_dataset.jsonl`
- Total rows: 20
- Categories:
  - factual: 7
  - multi_hop: 4
  - paraphrase: 5
  - no_answer: 4

### Run evaluation

```bash
python3 scripts/run_eval.py \
  --dataset data/eval/eval_dataset.jsonl \
  --api-url http://localhost:8000 \
  --require-llm
```

### Generated artifacts

- `reports/eval_results.json`
- `reports/per_question_results.csv`
- `reports/eval_report.md`

### Latest aggregate (judge mode)

From `reports/eval_report.md`:

- Context Precision: **0.6556**
- Context Recall: **0.7750**
- Faithfulness: **0.8083**
- Answer Relevancy: **0.5941**
- Answer Correctness: **0.7300**

---

## AI-Assisted Workflow (what was done)

- Iterative branch-based implementation (ingest -> query -> eval -> retrieval tuning).
- Prompt-driven decomposition into small verifiable deliverables.
- Frequent re-evaluation after targeted retrieval/generation changes.
- Test-backed refinements (query behavior and contracts validated with pytest).

---

## Known Limitations

1. Chroma runs in-process in the API container (single-service compose); not a separate DB service.
2. Judge metrics can vary run-to-run because they depend on LLM scoring.
3. Fixed-size chunking can still split semantic units.
4. Some evaluation rows remain sensitive to retrieval ranking noise.
5. Agentic research endpoint (extra credit) is not implemented.

---

## What I Would Improve With More Time

1. Add semantic/section-aware chunking to improve context precision.
2. Add stronger query decomposition + rerank fusion for hard multi-hop queries.
3. Add a minimal `/research` agent endpoint (sub-question planning + synthesis).
4. Add deterministic CI pipeline for regression checks (ingest smoke + eval smoke).

---

## Hardware / Runtime Expectations

Runs on:
- 16 GB RAM
- 4+ CPU cores
- ~20 GB disk
- No GPU required

---

## Useful Commands

```bash
# Start
docker compose up --build -d

# Ingest
./scripts/smoke_ingest.sh

# Query smoke test
./scripts/smoke_query.sh

# Unit tests
python3 -m pytest -q tests/test_query.py

# Eval
python3 scripts/run_eval.py --dataset data/eval/eval_dataset.jsonl --api-url http://localhost:8000 --require-llm
```

