"""ChromaDB persistence layer."""

from __future__ import annotations

import logging

import chromadb
from chromadb.config import Settings

from app.config import CHROMA_COLLECTION, CHROMA_DIR
from app.ingest.chunker import Chunk

logger = logging.getLogger(__name__)

_client: chromadb.ClientAPI | None = None


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
