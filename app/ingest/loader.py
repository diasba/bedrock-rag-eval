"""Document loader — reads .txt, .md, .pdf from a directory tree."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: set[str] = {".txt", ".md", ".pdf"}
IGNORED_FILENAMES: set[str] = {"urls.txt", "sources.md"}


@dataclass
class LoadedDoc:
    """A single loaded document."""

    doc_id: str  # relative path from ingest root
    text: str
    source_path: str  # absolute path on disk
    content_type: str  # "txt" | "md" | "pdf"


@dataclass
class LoadResult:
    """Aggregate result of loading a folder."""

    docs: list[LoadedDoc] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


# ── Helpers ────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Normalize text while removing obvious navigation boilerplate."""
    import re

    boilerplate = {
        "table of contents",
        "contents",
        "on this page",
        "related resources",
        "was this page helpful",
        "feedback",
        "learn more",
    }

    cleaned_lines: list[str] = []
    prev = ""
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue
        low = line.lower()
        if low in boilerplate:
            continue
        if len(low) < 3 and not any(ch.isdigit() for ch in low):
            continue
        if line == prev:
            continue
        cleaned_lines.append(line)
        prev = line

    normalized = "\n".join(cleaned_lines)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _read_text(path: Path) -> str:
    return _normalize(path.read_text(encoding="utf-8", errors="replace"))


def _read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return _normalize("\n".join(pages))


# ── Public API ─────────────────────────────────────────────────────────

def load_folder(root: Path, min_doc_length: int = 200) -> LoadResult:
    """Recursively load all supported files under *root*.

    Returns a :class:`LoadResult` with successfully loaded docs and any
    errors encountered (capped at detail level).
    """
    result = LoadResult()
    root = root.resolve()

    if not root.is_dir():
        result.errors.append({"doc_id": str(root), "error": "Path is not a directory"})
        return result

    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if path.name in IGNORED_FILENAMES:
            continue

        doc_id = str(path.relative_to(root))
        content_type = path.suffix.lstrip(".").lower()

        try:
            if content_type in ("txt", "md"):
                text = _read_text(path)
            elif content_type == "pdf":
                text = _read_pdf(path)
            else:
                continue

            if len(text) < min_doc_length:
                logger.info("Skipping %s — too short (%d chars)", doc_id, len(text))
                continue

            result.docs.append(
                LoadedDoc(
                    doc_id=doc_id,
                    text=text,
                    source_path=str(path),
                    content_type=content_type,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load %s: %s", doc_id, exc)
            result.errors.append({"doc_id": doc_id, "error": str(exc)})

    return result
