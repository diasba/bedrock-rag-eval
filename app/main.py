"""FastAPI application — endpoints: /health, /ingest, /query, /query/stream, /ui."""

from __future__ import annotations

import json
import logging
import re
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import FileResponse, StreamingResponse

from app.config import (
    CHUNK_OVERLAP, CHUNK_SIZE, HYBRID_ENABLED, MAX_CHUNKS_PER_DOC,
    MIN_DOC_LENGTH, QUERY_CACHE_ENABLED, QUERY_CACHE_TTL_SEC,
    RERANK_ENABLED, TOP_K,
)
from app.db.chroma import RetrievedChunk, get_collection, heartbeat, query_chunks, upsert_chunks
from app.generation.llm import (
    check_llm_ready, generate_answer, generate_answer_stream, is_llm_available,
)
from app.ingest.chunker import Chunk, chunk_text
from app.ingest.embedder import embed_texts
from app.ingest.loader import load_folder
from app.retrieval.cache import QueryCache
from app.retrieval.hybrid import (
    expand_query_variants, fuse_bm25_runs, fuse_vector_runs, get_bm25_index,
    hybrid_merge, rebuild_bm25_index, select_multi_hop_contexts,
)
from app.retrieval.reranker import rerank_chunks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Cache singleton ────────────────────────────────────────────────────
query_cache: QueryCache | None = (
    QueryCache(ttl_sec=QUERY_CACHE_TTL_SEC) if QUERY_CACHE_ENABLED else None
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Build BM25 index on startup if hybrid retrieval is enabled."""
    if HYBRID_ENABLED:
        try:
            collection = get_collection()
            if collection.count() > 0:
                rebuild_bm25_index(collection)
        except Exception as exc:  # noqa: BLE001
            logger.warning("BM25 index build failed on startup: %s", exc)
    yield


app = FastAPI(title="Bedrock RAG Service", version="0.2.0", lifespan=lifespan)

_CONFIDENCE_STOPWORDS = {
    "the", "is", "a", "an", "of", "and", "to", "in", "for", "on", "with", "by",
    "what", "how", "do", "does", "are", "both", "before", "can", "you", "it",
    "this", "that", "be", "from", "or", "as", "at", "your", "through", "about",
    "used", "using", "use", "user", "guide", "api", "aws", "amazon", "bedrock",
    "model", "models", "service", "services", "default", "supports", "support",
    "foundation", "knowledge", "base", "runtime",
}

# Conservative thresholds: only treat an "I don't know" output as true no-answer
# when retrieval confidence is low by BOTH similarity and lexical overlap.
LOW_CONFIDENCE_SCORE_MAX = 0.55
LOW_CONFIDENCE_OVERLAP_MAX = 0.30


# ── Schemas ────────────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    path: str  # folder to ingest, e.g. "data/corpus_raw"
    chunk_size: int | None = None   # override CHUNK_SIZE for this run
    chunk_overlap: int | None = None  # override CHUNK_OVERLAP for this run


class IngestError(BaseModel):
    doc_id: str
    error: str


class IngestResponse(BaseModel):
    docs_total: int
    docs_ok: int
    docs_failed: int
    chunks_total: int
    chunks_indexed: int
    duration_sec: float
    errors: list[IngestError]


class HealthResponse(BaseModel):
    status: str
    chroma: str
    llm_ready: bool
    llm_reason: str


class StatsResponse(BaseModel):
    total_chunks: int
    by_content_type: dict[str, int]
    top_docs: list[dict]
    md_count: int


class QueryRequest(BaseModel):
    question: str
    top_k: int = TOP_K
    include_context: bool = False


class CitationResponse(BaseModel):
    doc_id: str
    chunk_id: str


class RetrievedChunkResponse(BaseModel):
    doc_id: str
    chunk_id: str
    score: float
    text: str
    vector_score: float | None = None
    keyword_score: float | None = None


class QueryResponse(BaseModel):
    answer: str | None
    citations: list[CitationResponse]
    retrieved: list[RetrievedChunkResponse] | None = None
    retrieved_count: int | None = None
    max_score: float | None = None
    gate_reason: str | None = None
    cache_hit: bool | None = None


# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    chroma_ok = heartbeat()
    llm_result = check_llm_ready()
    return HealthResponse(
        status="ok",
        chroma="ok" if chroma_ok else "unreachable",
        llm_ready=llm_result["ready"],
        llm_reason=llm_result["reason"],
    )


@app.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    """Return ChromaDB collection statistics from the running service."""
    from collections import Counter

    collection = get_collection()
    total = collection.count()

    if total == 0:
        return StatsResponse(
            total_chunks=0, by_content_type={}, top_docs=[], md_count=0,
        )

    all_data = collection.get(include=["metadatas"])
    metadatas = all_data["metadatas"] or []

    type_counter: Counter[str] = Counter()
    doc_counter: Counter[str] = Counter()
    for meta in metadatas:
        type_counter[meta.get("content_type", "unknown")] += 1
        doc_counter[meta.get("doc_id", "unknown")] += 1

    top_docs = [
        {"doc_id": doc_id, "chunks": count}
        for doc_id, count in doc_counter.most_common(5)
    ]

    return StatsResponse(
        total_chunks=total,
        by_content_type=dict(type_counter),
        top_docs=top_docs,
        md_count=type_counter.get("md", 0),
    )


@app.post("/ingest", response_model=IngestResponse)
def ingest(body: IngestRequest) -> IngestResponse:
    t0 = time.perf_counter()

    root = Path(body.path)
    if not root.is_absolute():
        root = Path.cwd() / root  # resolve relative to working dir

    logger.info("Starting ingestion from %s", root)

    # 1. Load documents ─────────────────────────────────────────────────
    load_result = load_folder(root, min_doc_length=MIN_DOC_LENGTH)
    docs = load_result.docs
    errors = load_result.errors

    logger.info("Loaded %d docs, %d errors", len(docs), len(errors))

    # 2. Chunk ──────────────────────────────────────────────────────────
    # Use request overrides or defaults; clamp to safe ranges
    cs = max(100, min(body.chunk_size or CHUNK_SIZE, 4000))
    co = max(0, min(body.chunk_overlap or CHUNK_OVERLAP, cs // 2))

    all_chunks: list[Chunk] = []
    for doc in docs:
        chunks = chunk_text(
            text=doc.text,
            doc_id=doc.doc_id,
            source_path=doc.source_path,
            content_type=doc.content_type,
            chunk_size=cs,
            chunk_overlap=co,
        )
        all_chunks.extend(chunks)

    logger.info("Created %d chunks from %d docs", len(all_chunks), len(docs))

    # 3. Embed ──────────────────────────────────────────────────────────
    texts = [c.text for c in all_chunks]
    embeddings = embed_texts(texts) if texts else []

    # 4. Upsert into ChromaDB ──────────────────────────────────────────
    indexed = upsert_chunks(all_chunks, embeddings) if all_chunks else 0

    duration = round(time.perf_counter() - t0, 2)
    logger.info("Ingestion complete: %d chunks indexed in %.2fs", indexed, duration)

    # 5. Rebuild BM25 index for hybrid retrieval ───────────────────────
    if HYBRID_ENABLED and indexed > 0:
        try:
            rebuild_bm25_index(get_collection())
        except Exception as exc:  # noqa: BLE001
            logger.warning("BM25 index rebuild failed after ingest: %s", exc)

    return IngestResponse(
        docs_total=len(docs) + len(errors),
        docs_ok=len(docs),
        docs_failed=len(errors),
        chunks_total=len(all_chunks),
        chunks_indexed=indexed,
        duration_sec=duration,
        errors=[IngestError(**e) for e in errors[:10]],
    )


@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest) -> QueryResponse:
    """Answer a question using RAG with grounded citations."""
    logger.info("Query: %s", body.question)

    # ── Cache check ───────────────────────────────────────────────────
    if query_cache is not None:
        cached = query_cache.get(
            body.question, body.top_k, include_context=body.include_context,
        )
        if cached is not None:
            logger.info("Cache HIT for: %s", body.question[:60])
            return QueryResponse(**{**cached, "cache_hit": True})

    # 1. Expand query variants (for multi-hop prompts) ─────────────────
    query_variants = expand_query_variants(body.question)
    if not query_variants:
        return QueryResponse(answer=None, citations=[])

    is_multi_variant = len(query_variants) > 1
    candidate_top_k = max(body.top_k * (3 if is_multi_variant else 1), body.top_k)
    per_doc_limit = 1 if is_multi_variant else MAX_CHUNKS_PER_DOC

    # 2. Dense retrieval for each variant, then fuse with RRF + lexical scoring
    dense_runs: list[list[RetrievedChunk]] = []
    dense_fetch_k = max(body.top_k * (3 if is_multi_variant else 1), body.top_k)
    for variant in query_variants:
        embedding = embed_texts([variant])[0]
        dense_runs.append(
            query_chunks(embedding, top_k=dense_fetch_k, question=variant),
        )

    retrieved = fuse_vector_runs(
        body.question,
        dense_runs,
        top_k=candidate_top_k,
        max_per_doc=per_doc_limit,
    )

    # 2b. Hybrid merge (BM25 + dense), fused over query variants ──────
    if HYBRID_ENABLED:
        bm25_idx = get_bm25_index()
        if bm25_idx.ready:
            bm25_runs = [
                bm25_idx.query(variant, top_k=dense_fetch_k * 2)
                for variant in query_variants
            ]
            bm25_hits = fuse_bm25_runs(bm25_runs, top_k=dense_fetch_k * 3)
            retrieved = hybrid_merge(
                retrieved,
                bm25_hits,
                bm25_idx,
                top_k=candidate_top_k,
                max_per_doc=per_doc_limit,
            )

    # 2c. Optional model-based rerank ──────────────────────────────────
    if RERANK_ENABLED and len(retrieved) > 1:
        retrieved = rerank_chunks(body.question, retrieved, top_k=body.top_k)

    if is_multi_variant:
        retrieved = select_multi_hop_contexts(body.question, retrieved, top_k=body.top_k)
    else:
        retrieved = retrieved[: body.top_k]
    retrieved_count = len(retrieved)
    max_score = max((chunk.score for chunk in retrieved), default=None)
    token_overlap = _question_context_overlap(body.question, retrieved)

    # 3. No-answer gate: only when retrieval is empty ──────────────────
    if not retrieved:
        logger.info("No answer: retrieval returned 0 chunks")
        return QueryResponse(
            answer=None,
            citations=[],
            retrieved=_format_retrieved(retrieved) if body.include_context else None,
            retrieved_count=retrieved_count if body.include_context else None,
            max_score=max_score if body.include_context else None,
            gate_reason="no_retrieval" if body.include_context else None,
        )

    # 4. Generate answer with LLM ──────────────────────────────────────
    result = generate_answer(body.question, retrieved)

    # 5. If LLM generation is unavailable/failed, preserve strict null contract.
    if result.answer is None:
        return QueryResponse(
            answer=None,
            citations=[],
            retrieved=_format_retrieved(retrieved) if body.include_context else None,
            retrieved_count=retrieved_count if body.include_context else None,
            max_score=max_score if body.include_context else None,
            gate_reason=(
                "llm_generation_failed" if (body.include_context and is_llm_available())
                else "llm_unavailable" if body.include_context else None
            ),
        )

    # 6. Normalize explicit "can't answer from provided docs" outputs.
    if _is_no_answer_output(result.answer):
        if _is_low_confidence(max_score, token_overlap):
            return QueryResponse(
                answer=None,
                citations=[],
                retrieved=_format_retrieved(retrieved) if body.include_context else None,
                retrieved_count=retrieved_count if body.include_context else None,
                max_score=max_score if body.include_context else None,
                gate_reason="generated_no_answer_low_confidence" if body.include_context else None,
            )
        # Retrieval looks confident; return a short extractive answer instead of null.
        extracted = _short_extractive_answer(retrieved[0].text)
        if extracted:
            return QueryResponse(
                answer=extracted,
                citations=[
                    CitationResponse(
                        doc_id=retrieved[0].doc_id,
                        chunk_id=retrieved[0].chunk_id,
                    ),
                ],
                retrieved=_format_retrieved(retrieved) if body.include_context else None,
                retrieved_count=retrieved_count if body.include_context else None,
                max_score=max_score if body.include_context else None,
                gate_reason="generated_no_answer_but_confident" if body.include_context else None,
            )
        return QueryResponse(
            answer="Based on the retrieved context, a concise answer is not explicit.",
            citations=[
                CitationResponse(
                    doc_id=retrieved[0].doc_id,
                    chunk_id=retrieved[0].chunk_id,
                ),
            ],
            retrieved=_format_retrieved(retrieved) if body.include_context else None,
            retrieved_count=retrieved_count if body.include_context else None,
            max_score=max_score if body.include_context else None,
            gate_reason="generated_no_answer_but_confident" if body.include_context else None,
        )

    # 6. Citation fallback: if LLM produced an answer but omitted markers,
    #    cite all retrieved chunks (they passed the relevance gate).
    citations = result.citations
    if not citations:
        logger.info("LLM omitted chunk markers — falling back to all retrieved chunks as citations")
        from app.generation.llm import Citation as _Cit
        citations = [_Cit(doc_id=c.doc_id, chunk_id=c.chunk_id) for c in retrieved]

    logger.info("Generated answer with %d citations", len(citations))

    response = QueryResponse(
        answer=result.answer,
        citations=[
            CitationResponse(doc_id=c.doc_id, chunk_id=c.chunk_id)
            for c in citations
        ],
        retrieved=_format_retrieved(retrieved) if body.include_context else None,
        retrieved_count=retrieved_count if body.include_context else None,
        max_score=max_score if body.include_context else None,
        gate_reason="generated_answer" if body.include_context else None,
    )

    # ── Cache store (success path) ────────────────────────────────────
    if query_cache is not None:
        query_cache.set(
            body.question, body.top_k, response.model_dump(),
            include_context=body.include_context,
        )

    return response


def _format_retrieved(chunks: list[RetrievedChunk]) -> list[RetrievedChunkResponse]:
    """Convert retrieved chunks to response format."""
    return [
        RetrievedChunkResponse(
            doc_id=c.doc_id,
            chunk_id=c.chunk_id,
            score=round(c.score, 4),
            text=c.text,
            vector_score=round(c.vector_score, 4) if c.vector_score is not None else None,
            keyword_score=round(c.keyword_score, 4) if c.keyword_score is not None else None,
        )
        for c in chunks
    ]


_NO_ANSWER_PATTERNS = (
    re.compile(r"\bi don't know based on (the )?provided documents?\b", re.IGNORECASE),
    re.compile(r"\bnot in (the )?provided documents?\b", re.IGNORECASE),
    re.compile(r"\bcontext does not mention\b", re.IGNORECASE),
    re.compile(r"\bprovided context does not mention\b", re.IGNORECASE),
    re.compile(r"\bcannot be determined from (the )?provided (documents?|context)\b", re.IGNORECASE),
    re.compile(r"^insufficient (context|information)\.?$", re.IGNORECASE),
    re.compile(r"\binsufficient (context|information) to\b", re.IGNORECASE),
    re.compile(r"\b(cannot|can't|unable to) (answer|determine|provide)\b", re.IGNORECASE),
    re.compile(r"\bno relevant (information|context|data)\b", re.IGNORECASE),
    re.compile(r"\bcontext (is )?insufficient\b", re.IGNORECASE),
    re.compile(r"\bnot (enough|sufficient) (context|information)\b", re.IGNORECASE),
)


def _is_no_answer_output(answer: str) -> bool:
    text = answer.strip()
    return any(pattern.search(text) for pattern in _NO_ANSWER_PATTERNS)


def _tokenize_for_confidence(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    out: list[str] = []
    for token in tokens:
        if len(token) <= 3 or token in _CONFIDENCE_STOPWORDS:
            continue
        if token.endswith("ing") and len(token) > 5:
            token = token[:-3]
        elif token.endswith("ion") and len(token) > 5:
            token = token[:-3]
        elif token.endswith("s") and len(token) > 4:
            token = token[:-1]
        out.append(token)
    return out


def _question_context_overlap(question: str, chunks: list[RetrievedChunk]) -> float:
    question_tokens = set(_tokenize_for_confidence(question))
    if not question_tokens:
        return 0.0
    context_tokens = set(_tokenize_for_confidence(" ".join(c.text for c in chunks)))
    if not context_tokens:
        return 0.0
    return len(question_tokens & context_tokens) / len(question_tokens)


def _is_low_confidence(max_score: float | None, token_overlap: float) -> bool:
    if max_score is None:
        return True
    return max_score < LOW_CONFIDENCE_SCORE_MAX and token_overlap < LOW_CONFIDENCE_OVERLAP_MAX


def _short_extractive_answer(text: str) -> str | None:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return None
    parts = re.split(r"(?<=[.!?])\s+", cleaned)
    first = (parts[0] if parts else cleaned).strip()
    if len(first) < 40 and len(parts) > 1:
        first = f"{first} {parts[1].strip()}".strip()
    return first[:280]


# ── SSE streaming endpoint ─────────────────────────────────────────────

def _sse_event(event: str, data: dict) -> str:
    """Format a single SSE frame."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/query/stream")
def query_stream(body: QueryRequest):
    """Stream answer tokens via Server-Sent Events.

    Events emitted:
      ``token``  — ``{"token": "..."}`` (partial answer text)
      ``cached`` — full cached response (if cache hit)
      ``done``   — ``{"answer": "...", "citations": [...]}``
    """

    def event_generator():
        # ── Cache check ──────────────────────────────────────────
        if query_cache is not None:
            cached = query_cache.get(
                body.question, body.top_k, include_context=body.include_context,
            )
            if cached is not None:
                logger.info("Stream cache HIT for: %s", body.question[:60])
                yield _sse_event("cached", {**cached, "cache_hit": True})
                return

        # 1. Retrieve ─────────────────────────────────────────────
        query_variants = expand_query_variants(body.question)
        if not query_variants:
            yield _sse_event("done", {"answer": None, "citations": []})
            return
        is_multi_variant = len(query_variants) > 1
        candidate_top_k = max(body.top_k * (3 if is_multi_variant else 1), body.top_k)
        per_doc_limit = 1 if is_multi_variant else MAX_CHUNKS_PER_DOC
        dense_fetch_k = max(body.top_k * (3 if is_multi_variant else 1), body.top_k)

        dense_runs: list[list[RetrievedChunk]] = []
        for variant in query_variants:
            embedding = embed_texts([variant])[0]
            dense_runs.append(
                query_chunks(embedding, top_k=dense_fetch_k, question=variant),
            )
        retrieved = fuse_vector_runs(
            body.question,
            dense_runs,
            top_k=candidate_top_k,
            max_per_doc=per_doc_limit,
        )

        # 2. Hybrid merge ─────────────────────────────────────────
        if HYBRID_ENABLED:
            bm25_idx = get_bm25_index()
            if bm25_idx.ready:
                bm25_runs = [
                    bm25_idx.query(variant, top_k=dense_fetch_k * 2)
                    for variant in query_variants
                ]
                bm25_hits = fuse_bm25_runs(bm25_runs, top_k=dense_fetch_k * 3)
                retrieved = hybrid_merge(
                    retrieved,
                    bm25_hits,
                    bm25_idx,
                    top_k=candidate_top_k,
                    max_per_doc=per_doc_limit,
                )

        # 3. Rerank ───────────────────────────────────────────────
        if RERANK_ENABLED and len(retrieved) > 1:
            retrieved = rerank_chunks(body.question, retrieved, top_k=body.top_k)
        if is_multi_variant:
            retrieved = select_multi_hop_contexts(body.question, retrieved, top_k=body.top_k)
        else:
            retrieved = retrieved[: body.top_k]

        # 4. No-answer gate (empty retrieval) ─────────────────────
        if not retrieved:
            result = {"answer": None, "citations": []}
            yield _sse_event("done", result)
            return

        # 5. Stream LLM tokens ────────────────────────────────────
        final_event = None
        for event in generate_answer_stream(body.question, retrieved):
            if event["type"] == "token":
                yield _sse_event("token", {"token": event["token"]})
            elif event["type"] == "done":
                final_event = event

        answer = final_event["answer"] if final_event else None
        citations = final_event.get("citations", []) if final_event else []

        result = {"answer": answer, "citations": citations}
        yield _sse_event("done", result)

        # Cache store
        if query_cache is not None:
            query_cache.set(
                body.question, body.top_k, result,
                include_context=body.include_context,
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Web UI ─────────────────────────────────────────────────────────────

@app.get("/ui", include_in_schema=False)
def ui():
    """Serve the single-page web UI."""
    return FileResponse(
        Path(__file__).parent / "static" / "index.html",
        media_type="text/html",
    )


# ── Cache management ───────────────────────────────────────────────────

@app.post("/cache/clear", include_in_schema=False)
def cache_clear():
    """Clear the query cache. Returns number of evicted entries."""
    if query_cache is not None:
        n = query_cache.clear()
        return {"cleared": n}
    return {"cleared": 0, "reason": "cache disabled"}
