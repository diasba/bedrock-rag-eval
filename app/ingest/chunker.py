"""Fixed-size character chunker with overlap."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import CHUNK_OVERLAP, CHUNK_SIZE


@dataclass
class Chunk:
    """A single text chunk with provenance metadata."""

    chunk_id: str  # e.g. "txt/foo.txt#00002"
    doc_id: str
    text: str
    chunk_index: int
    source_path: str
    content_type: str


def chunk_text(
    text: str,
    doc_id: str,
    source_path: str,
    content_type: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Split *text* into fixed-size character chunks with overlap.

    Returns an ordered list of :class:`Chunk` objects with deterministic IDs.
    """
    if not text:
        return []

    chunks: list[Chunk] = []
    start = 0
    idx = 0

    while start < len(text):
        end = start + chunk_size
        segment = text[start:end]

        chunk_id = f"{doc_id}#{idx:05d}"
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                text=segment,
                chunk_index=idx,
                source_path=source_path,
                content_type=content_type,
            )
        )
        idx += 1
        start += chunk_size - chunk_overlap

    return chunks
