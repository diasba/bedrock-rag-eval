"""FastAPI application — MVP endpoints: /health, /ingest, /query."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, MIN_DOC_LENGTH, NO_ANSWER_MIN_SCORE, TOP_K
from app.db.chroma import RetrievedChunk, heartbeat, query_chunks, upsert_chunks
from app.generation.llm import generate_answer
from app.ingest.chunker import Chunk, chunk_text
from app.ingest.embedder import embed_texts
from app.ingest.loader import load_folder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Bedrock RAG Service", version="0.1.0")


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
    answer: str
    citations: list[CitationResponse]
    retrieved: list[RetrievedChunkResponse] | None = None


# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    chroma_ok = heartbeat()
    return HealthResponse(
        status="ok",
        chroma="ok" if chroma_ok else "unreachable",
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
    retrieved = query_chunks(query_embedding, top_k=body.top_k)

    # 3. No-answer gate ─────────────────────────────────────────────────
    if not retrieved or (retrieved and retrieved[0].score < NO_ANSWER_MIN_SCORE):
        logger.info("No answer: insufficient context (score: %.3f)", retrieved[0].score if retrieved else 0.0)
        return QueryResponse(
            answer="I don't know based on the provided documents.",
            citations=[],
            retrieved=_format_retrieved(retrieved) if body.include_context else None,
        )

    # 4. Generate answer with LLM ──────────────────────────────────────
    result = generate_answer(body.question, retrieved)

    # 5. Citation fallback: if LLM produced an answer but omitted markers,
    #    cite all retrieved chunks (they passed the relevance gate).
    citations = result.citations
    if not citations and result.answer:
        no_answer_text = "I don't know based on the provided documents."
        if no_answer_text not in result.answer:
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
