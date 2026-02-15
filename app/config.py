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

# ── Query / Retrieval ─────────────────────────────────────────────────
TOP_K: int = int(os.getenv("TOP_K", "4"))
MAX_CHUNKS_PER_DOC: int = int(os.getenv("MAX_CHUNKS_PER_DOC", "2"))
NO_ANSWER_MIN_SCORE: float = float(os.getenv("NO_ANSWER_MIN_SCORE", "0.3"))

# ── LLM (Groq) ────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.0"))
GROQ_FALLBACK_MODELS: list[str] = [
    model.strip()
    for model in os.getenv("GROQ_FALLBACK_MODELS", "llama-3.1-8b-instant").split(",")
    if model.strip()
]
