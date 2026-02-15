"""FastAPI application — MVP endpoints: /health, /ingest."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, MIN_DOC_LENGTH
from app.db.chroma import heartbeat, upsert_chunks
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
