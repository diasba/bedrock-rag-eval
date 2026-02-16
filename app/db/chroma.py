"""ChromaDB persistence layer."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings

from app.config import (
    CHROMA_COLLECTION, CHROMA_DIR, CHROMA_HOST, CHROMA_PORT, CHROMA_SSL,
    MAX_CHUNKS_PER_DOC, TOP_K,
)
from app.ingest.chunker import Chunk
from app.retrieval.detection import is_list_style, is_multihop

logger = logging.getLogger(__name__)

_client: chromadb.ClientAPI | None = None

_BOILERPLATE_HINTS = (
    "table of contents",
    "was this page helpful",
    "feedback",
    "next steps",
    "related resources",
    "learn more",
)
_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")
_QUERY_STOPWORDS = frozenset(
    "a an the is are was were be been being have has had do does did will "
    "would shall should may might can could of in to for on with at by from "
    "as into through during before after above below between and but or nor "
    "not no so if then than too very just about also each how all both few "
    "more most other some such what which who whom this that these those am "
    "amazon aws bedrock".split()
)


@dataclass
class RetrievedChunk:
    """A retrieved chunk with similarity score."""

    chunk_id: str
    doc_id: str
    text: str
    score: float
    source_path: str
    content_type: str
    vector_score: float | None = None
    keyword_score: float | None = None


def get_client() -> chromadb.ClientAPI:
    """Return a persistent Chroma client (singleton)."""
    global _client  # noqa: PLW0603
    if _client is None:
        if CHROMA_HOST:
            logger.info("Initialising ChromaDB HTTP client at %s:%d", CHROMA_HOST, CHROMA_PORT)
            _client = chromadb.HttpClient(
                host=CHROMA_HOST,
                port=CHROMA_PORT,
                ssl=CHROMA_SSL,
                settings=Settings(anonymized_telemetry=False),
            )
        else:
            logger.info("Initialising ChromaDB persistent client at %s", CHROMA_DIR)
            _client = chromadb.PersistentClient(
                path=CHROMA_DIR,
                settings=Settings(anonymized_telemetry=False),
            )
    return _client


def get_collection() -> chromadb.Collection:
    """Get (or create) the default collection."""
    client = get_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(
    chunks: list[Chunk],
    embeddings: list[list[float]],
) -> int:
    """Upsert chunks + embeddings into ChromaDB.

    Also deletes stale chunk IDs for ingested docs so re-ingestion with a new
    chunking config stays idempotent (no orphaned old chunks).
    """
    collection = get_collection()
    if not chunks:
        return 0

    # Remove stale chunks per doc_id before upsert.
    doc_to_new_ids: dict[str, set[str]] = {}
    for c in chunks:
        doc_to_new_ids.setdefault(c.doc_id, set()).add(c.chunk_id)

    for doc_id, new_ids in doc_to_new_ids.items():
        try:
            existing = collection.get(where={"doc_id": doc_id}, include=[])
            existing_ids = set(existing.get("ids", []) or [])
            stale_ids = [cid for cid in existing_ids if cid not in new_ids]
            if stale_ids:
                collection.delete(ids=stale_ids)
        except Exception:  # noqa: BLE001
            # Continue with upsert even if stale cleanup fails for a doc.
            pass

    # ChromaDB allows batches up to ~5 000; we batch at 500 for safety.
    batch_size = 500
    total = 0

    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        batch_embeds = embeddings[i : i + batch_size]

        ids = [c.chunk_id for c in batch_chunks]
        documents = [c.text for c in batch_chunks]
        metadatas = [
            {
                "doc_id": c.doc_id,
                "chunk_id": c.chunk_id,
                "source_path": c.source_path,
                "content_type": c.content_type,
                "chunk_index": c.chunk_index,
            }
            for c in batch_chunks
        ]

        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=batch_embeds,
            metadatas=metadatas,
        )
        total += len(batch_chunks)

    return total


def heartbeat() -> bool:
    """Return True if Chroma is reachable."""
    try:
        get_client().heartbeat()
        return True
    except Exception:  # noqa: BLE001
        return False


def _query_terms(question: str) -> set[str]:
    return {
        t
        for t in _TOKEN_RE.findall(question.lower())
        if len(t) > 2 and t not in _QUERY_STOPWORDS
    }


def _text_terms(text: str) -> set[str]:
    return {
        t
        for t in _TOKEN_RE.findall(text.lower())
        if len(t) > 2
    }


def _lexical_overlap_score(question_terms: set[str], text: str) -> float:
    if not question_terms:
        return 0.0
    overlap = len(question_terms & _text_terms(text))
    return overlap / len(question_terms)

def _looks_structured_chunk(text: str) -> bool:
    if not text:
        return False
    if text.count("\n") >= 4:
        return True
    lower = text.lower()
    return lower.count("metric:") >= 2 or lower.count("description:") >= 2


def query_chunks(
    query_embedding: list[float],
    top_k: int = TOP_K,
    max_per_doc: int = MAX_CHUNKS_PER_DOC,
    question: str = "",
) -> list[RetrievedChunk]:
    """Query ChromaDB with diversity: max *max_per_doc* chunks per doc_id,
    plus content-type balancing to reduce PDF dominance.

    Returns up to *top_k* chunks, re-ranked to ensure diversity across docs.
    Scores are cosine distances (lower = more similar); we convert to similarity.
    """
    collection = get_collection()

    # Fetch more than top_k to allow for diversity and filtering.
    fetch_k = max(top_k * 4, 24)
    multi_hop_query = is_multihop(question)
    list_style_query = is_list_style(question)
    if multi_hop_query:
        fetch_k = max(fetch_k, top_k * 10, 60)
    if list_style_query:
        # List-style prompts often need multiple adjacent chunks from one doc.
        fetch_k = max(fetch_k, top_k * 8, 48)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=fetch_k,
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Build candidate list with similarity scores (1 - distance for cosine)
    candidates = [
        RetrievedChunk(
            chunk_id=ids[i],
            doc_id=metadatas[i]["doc_id"],
            text=documents[i],
            score=1.0 - distances[i],  # Convert distance to similarity
            source_path=metadatas[i]["source_path"],
            content_type=metadatas[i]["content_type"],
        )
        for i in range(len(ids))
    ]

    # Drop obvious navigation/boilerplate chunks when alternatives exist.
    cleaned_candidates = [
        c for c in candidates
        if not any(h in c.text.lower() for h in _BOILERPLATE_HINTS)
    ]
    if cleaned_candidates:
        candidates = cleaned_candidates

    # Generic lexical adjustment to reduce dense-only drift.
    q_terms = _query_terms(question)
    for chunk in candidates:
        overlap = _lexical_overlap_score(q_terms, chunk.text)
        chunk.score += 0.14 * overlap
        if list_style_query and _looks_structured_chunk(chunk.text):
            chunk.score += 0.05

    candidates.sort(key=lambda c: c.score, reverse=True)

    # Apply diversity: max *max_per_doc* chunks per doc_id.
    effective_max_per_doc = 1 if multi_hop_query else max_per_doc
    if list_style_query:
        effective_max_per_doc = max(effective_max_per_doc, min(top_k, 3))
    doc_counts: dict[str, int] = {}
    diverse_results: list[RetrievedChunk] = []

    for chunk in candidates:
        count = doc_counts.get(chunk.doc_id, 0)
        if count < effective_max_per_doc:
            diverse_results.append(chunk)
            doc_counts[chunk.doc_id] = count + 1
        if len(diverse_results) >= top_k * 3:
            break

    # ── Content-type balancing ────────────────────────────────────────
    has_text_md = any(c.content_type in ("txt", "md") for c in diverse_results)
    MAX_PDF = 1

    if has_text_md:
        balanced: list[RetrievedChunk] = []
        pdf_count = 0
        for chunk in diverse_results:
            if chunk.content_type == "pdf":
                if pdf_count >= MAX_PDF:
                    continue
                pdf_count += 1
            balanced.append(chunk)
            if len(balanced) >= top_k:
                break
        return balanced

    return diverse_results[:top_k]
