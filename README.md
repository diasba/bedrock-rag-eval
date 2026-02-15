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

### Build Corpus from `urls.txt` (recommended)

If `data/corpus_raw/txt/*.txt` is small/empty, build a larger corpus from URL docs:

```bash
python3 scripts/fetch_urls_to_md.py \
  --urls-file data/corpus_raw/html/urls.txt \
  --output-dir data/corpus_raw/md

curl -s -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path":"data/corpus_raw"}' | python3 -m json.tool

python3 scripts/chroma_stats.py --api-url http://localhost:8000
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
    "chroma": "ok",
    "llm_ready": true,
    "llm_reason": "Groq API operational (model: llama-3.3-70b-versatile)"
}
```

### Collection statistics
```bash
curl -s http://localhost:8000/stats | python3 -m json.tool
```
Expected response:
```json
{
    "total_chunks": 128,
    "by_content_type": {"txt": 27, "pdf": 89, "md": 12},
    "top_docs": [{"doc_id": "pdf/bedrock_user_guide.pdf", "chunks": 45}],
    "md_count": 12
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
    "answer": null,
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

## Pre-flight Checks

> **Important:** These scripts query the **running API container** by default,
> so they test the same ChromaDB and LLM configuration that `/query` uses.
> Add `--local` to check the host environment instead.

### Check Groq LLM Readiness

Verify that the **container** has a valid Groq API key and the model responds:

```bash
python scripts/check_groq.py                          # via API (default)
python scripts/check_groq.py --api-url http://host:8000
python scripts/check_groq.py --local                  # host-side only
```

Output (success):
```
✅  Groq LLM ready — Groq API operational (model: llama-3.3-70b-versatile)
```

Output (failure):
```
❌  Groq LLM NOT ready — GROQ_API_KEY not set
```

### ChromaDB Collection Statistics

Inspect the **container's** vector store (not the host's local `./chroma/`):

```bash
python scripts/chroma_stats.py                          # via API (default)
python scripts/chroma_stats.py --api-url http://host:8000
python scripts/chroma_stats.py --local                  # host-side only
```

Output:
```
ChromaDB Collection Statistics
========================================
Total chunks: 128
By content type:
     md:   12
    pdf:   89
    txt:   27
Top documents by chunk count:
  pdf/bedrock_user_guide.pdf: 45 chunks
  ...
```

## Evaluation

### Dataset

The evaluation dataset is at `data/eval/eval_dataset.jsonl` — 22 question–answer–context triplets covering:
- **Factual** (8): clear, unambiguous questions
- **Multi-hop** (4): require synthesizing info across chunks
- **Paraphrase** (6): same question asked differently than source text
- **No-answer** (4): questions with no answer in the corpus

### Evaluation Modes

The evaluation runner works in **two modes** so it never aborts due to missing API keys:

| Mode | Trigger | Metrics | Reliability |
|---|---|---|---|
| **Heuristic-only** (default) | No `GROQ_API_KEY` set | Token-overlap heuristics for all 5 metrics | Always succeeds — no external calls |
| **Judge mode** | `GROQ_API_KEY` set on host AND container LLM ready | RAGAS LLM-judge + DeepEval GEval via Groq | Falls back to heuristics per-metric on any failure |

> **Key guarantee:** Report artifacts (`eval_results.json`, `per_question_results.csv`, `eval_report.md`) are **always** generated regardless of mode or judge failures.

> **Split-brain prevention:** The eval runner queries the container's `GET /health` and `GET /stats` endpoints for all pre-flight checks — it never reads the host's local ChromaDB or local Groq config. The JSON output includes a `metrics_source` field (`"judge"`, `"mixed"`, or `"heuristic"`) that reflects what **actually** happened, not what was attempted.

### Running Evaluation

Prerequisites: the RAG service must be running with ingested data.

```bash
# 1. Start the service and ingest
docker compose up --build -d
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"path": "data/corpus_raw"}'
```

**Heuristic-only run** (no paid keys required):
```bash
pip install httpx
python scripts/run_eval.py \
  --dataset data/eval/eval_dataset.jsonl \
  --api-url http://localhost:8000
```

**Groq-enabled judge run** (higher-quality metrics):
```bash
pip install ragas deepeval datasets langchain-groq
GROQ_API_KEY=gsk_... python scripts/run_eval.py \
  --dataset data/eval/eval_dataset.jsonl \
  --api-url http://localhost:8000
```

**Strict LLM-required run** (fail if Groq is not operational):
```bash
GROQ_API_KEY=gsk_... python scripts/run_eval.py \
  --dataset data/eval/eval_dataset.jsonl \
  --api-url http://localhost:8000 \
  --require-llm
```

```bash
# View the report
cat reports/eval_report.md
```

### Output Artifacts

| File | Description |
|---|---|
| `reports/eval_results.json` | Machine-readable aggregate + per-question scores (includes `judge_mode`, `llm_enabled`, `llm_status`, `metrics_source`, `chroma_stats` fields) |
| `reports/per_question_results.csv` | Spreadsheet-friendly per-question breakdown |
| `reports/eval_report.md` | Full evaluation report with mode banner, LLM/chroma status, metric interpretation notes, failure analysis, and improvement suggestions |

### Metrics

| Metric | Heuristic | Judge (Groq) | What It Measures |
|---|---|---|---|
| Context Precision | Token-Jaccard overlap | RAGAS LLM-judge | Are the retrieved chunks actually relevant? |
| Context Recall | Token-recall coverage | RAGAS LLM-judge | Does retrieval find all needed chunks? |
| Faithfulness | Token-precision (answer vs context) | RAGAS LLM-judge | Is the answer grounded in context (no hallucination)? |
| Answer Relevancy | Token-overlap (question vs answer) | RAGAS LLM-judge | Does the answer address the question? |
| Answer Correctness | Token-overlap F1 | DeepEval GEval | Does the answer match the ground truth? |

> **Note:** The report includes a banner indicating which mode was used. In judge mode, if any individual metric computation fails, that metric falls back to its heuristic value — the run never aborts.

### Retrieval Content-Type Balancing

To reduce PDF dominance in retrieval results (PDF documents tend to produce many more chunks), the system applies content-type balancing:

- When **txt/md** chunks are available, PDF chunks are capped at **1** per query
- Exception: queries containing **IAM / policy / role** keywords bypass the PDF cap (these topics are typically PDF-only)

### Null-Answer Contract

When the LLM is unavailable or a question falls below the similarity threshold:

- `answer` is **always `null`** (never a placeholder string)
- `citations` is **always `[]`**
- No "LLM unavailable" or "Retrieved context" text ever appears in responses
