"""Centralised configuration — reads from environment / .env file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root (if present)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_PATH)

# ── Paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
CHROMA_DIR: str = os.getenv("CHROMA_DIR", str(PROJECT_ROOT / "chroma"))

# ── Chunking ───────────────────────────────────────────────────────────
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))
MIN_DOC_LENGTH: int = int(os.getenv("MIN_DOC_LENGTH", "200"))

# ── Embeddings ─────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# ── ChromaDB ───────────────────────────────────────────────────────────
CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "bedrock_docs")

# ── LLM (reserved for later) ──────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
