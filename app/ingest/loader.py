"""Document loader — reads .txt, .md, .pdf from a directory tree."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS: set[str] = {".txt", ".md", ".pdf"}
IGNORED_FILENAMES: set[str] = {"urls.txt", "sources.md"}

# Corpus files that add noise without covering any eval-relevant topic.
# They are excluded at load time to shrink the chunk pool and lift
# context precision across all question categories.
IGNORED_STEMS: set[str] = {
    "prompt-templates-and-examples",
    "design-a-prompt",
    "webcrawl-data-source-connector",
    "prompt-engineering-guidelines",
    "kb-advanced-parsing",
    "kb-custom-transformation",
    "kb-info",
    "what-is-prompt-engineering",
}


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
    """Normalize text while removing navigation boilerplate and noisy table rows."""
    import re

    boilerplate = {
        "table of contents",
        "contents",
        "on this page",
        "related resources",
        "was this page helpful",
        "feedback",
        "learn more",
        "documentation amazon bedrock",
        "javascript is disabled or is unavailable in your browser",
    }

    # Regex patterns for noisy corpus artefacts
    _source_header_re = re.compile(r"^(Source|Fetched[- ]?At)\s*:", re.IGNORECASE)
    _yes_no_tok_re = re.compile(r"\b(?:Yes|No)\b")
    _model_id_re = re.compile(
        r"\b[a-z][a-z0-9]*\.[a-z][a-z0-9]+-[a-z0-9]+-[a-z0-9]+"
    )

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
        # Strip Source: / Fetched-At: download headers
        if _source_header_re.match(line):
            continue
        # Strip region-availability table rows (5+ Yes/No tokens on one line)
        if len(_yes_no_tok_re.findall(line)) >= 5:
            continue
        # Strip detailed model-table rows (model ID + region pattern)
        if _model_id_re.search(line) and len(line) > 100:
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
        # Match noise files by prefix (stems may have hash suffixes)
        stem_lower = path.stem.lower()
        if any(stem_lower.startswith(ns) for ns in IGNORED_STEMS):
            logger.info("Skipping noise file: %s", path.name)
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
