"""ChromaDB persistence layer."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings

from app.config import CHROMA_COLLECTION, CHROMA_DIR, MAX_CHUNKS_PER_DOC, TOP_K
from app.ingest.chunker import Chunk

logger = logging.getLogger(__name__)

_client: chromadb.ClientAPI | None = None


@dataclass
class RetrievedChunk:
    """A retrieved chunk with similarity score."""

    chunk_id: str
    doc_id: str
    text: str
    score: float
    source_path: str
    content_type: str


def get_client() -> chromadb.ClientAPI:
    """Return a persistent Chroma client (singleton)."""
    global _client  # noqa: PLW0603
    if _client is None:
        logger.info("Initialising ChromaDB at %s", CHROMA_DIR)
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
    """Upsert chunks + embeddings into ChromaDB. Returns count upserted."""
    collection = get_collection()
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


def query_chunks(
    query_embedding: list[float],
    top_k: int = TOP_K,
    max_per_doc: int = MAX_CHUNKS_PER_DOC,
) -> list[RetrievedChunk]:
    """Query ChromaDB with diversity: max *max_per_doc* chunks per doc_id.

    Returns up to *top_k* chunks, re-ranked to ensure diversity across docs.
    Scores are cosine distances (lower = more similar); we convert to similarity.
    """
    collection = get_collection()

    # Fetch more than top_k to allow for diversity filtering
    fetch_k = top_k * 3

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

    # Apply diversity: max *max_per_doc* chunks per doc_id
    doc_counts: dict[str, int] = {}
    diverse_results: list[RetrievedChunk] = []

    for chunk in candidates:
        count = doc_counts.get(chunk.doc_id, 0)
        if count < max_per_doc:
            diverse_results.append(chunk)
            doc_counts[chunk.doc_id] = count + 1
        if len(diverse_results) >= top_k:
            break

    return diverse_results
