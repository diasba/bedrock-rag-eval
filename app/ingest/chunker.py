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


def _snap_chunk_end(text: str, start: int, target_end: int) -> int:
    """Snap chunk end near a natural boundary while preserving fixed-size behavior."""
    n = len(text)
    target_end = min(max(target_end, start + 1), n)
    if target_end >= n:
        return n

    window_back = 120
    window_forward = 80
    lower = max(start + 1, target_end - window_back)
    upper = min(n, target_end + window_forward)

    # Prefer paragraph/sentence boundaries.
    for marker in ("\n\n", "\n", ". ", "? ", "! ", "; "):
        pos = text.rfind(marker, lower, upper)
        if pos != -1 and pos > start + 80:
            return min(pos + len(marker), n)
    return target_end


def _split_markdown_sections(text: str) -> list[str]:
    """Split Markdown into header-bounded sections before fixed chunking."""
    sections: list[str] = []
    current: list[str] = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.lstrip().startswith("#"):
            if current:
                section = "\n".join(current).strip()
                if section:
                    sections.append(section)
                current = []
        current.append(line)

    if current:
        section = "\n".join(current).strip()
        if section:
            sections.append(section)

    return sections if sections else [text]


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
    idx = 0
    stride = max(1, chunk_size - chunk_overlap)
    sections = _split_markdown_sections(text) if content_type == "md" else [text]

    for section in sections:
        n = len(section)
        if n == 0:
            continue

        start = 0
        while start < n:
            target_end = min(start + chunk_size, n)
            end = _snap_chunk_end(section, start, target_end)
            if end <= start:
                end = min(start + chunk_size, n)

            segment = section[start:end].strip()
            if not segment:
                start += stride
                continue

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

            if end >= n:
                break
            next_start = max(end - chunk_overlap, start + 1)
            if next_start <= start:
                next_start = start + stride
            start = next_start

    return chunks
