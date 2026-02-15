"""FastAPI application — MVP endpoints: /health, /ingest, /query."""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, MIN_DOC_LENGTH, TOP_K
from app.db.chroma import RetrievedChunk, get_collection, heartbeat, query_chunks, upsert_chunks
from app.generation.llm import check_llm_ready, generate_answer, is_llm_available
from app.ingest.chunker import Chunk, chunk_text
from app.ingest.embedder import embed_texts
from app.ingest.loader import load_folder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bedrock RAG Service", version="0.1.0")

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


class QueryResponse(BaseModel):
    answer: str | None
    citations: list[CitationResponse]
    retrieved: list[RetrievedChunkResponse] | None = None
    retrieved_count: int | None = None
    max_score: float | None = None
    gate_reason: str | None = None


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
    all_chunks: list[Chunk] = []
    for doc in docs:
        chunks = chunk_text(
            text=doc.text,
            doc_id=doc.doc_id,
            source_path=doc.source_path,
            content_type=doc.content_type,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
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

    # 1. Embed the question ─────────────────────────────────────────────
    query_embedding = embed_texts([body.question])[0]

    # 2. Retrieve relevant chunks ──────────────────────────────────────
    retrieved = query_chunks(query_embedding, top_k=body.top_k, question=body.question)
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

    return QueryResponse(
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


def _format_retrieved(chunks: list[RetrievedChunk]) -> list[RetrievedChunkResponse]:
    """Convert retrieved chunks to response format."""
    return [
        RetrievedChunkResponse(
            doc_id=c.doc_id,
            chunk_id=c.chunk_id,
            score=round(c.score, 4),
            text=c.text,
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
