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

# ── LLM (Mistral) ─────────────────────────────────────────────────────
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL: str = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
MISTRAL_TEMPERATURE: float = float(os.getenv("MISTRAL_TEMPERATURE", "0.0"))
MISTRAL_FALLBACK_MODELS: list[str] = [
    model.strip()
    for model in os.getenv("MISTRAL_FALLBACK_MODELS", "mistral-small-latest").split(",")
    if model.strip()
]

# ── Multi-Hop Retrieval ────────────────────────────────────────────────
MULTIHOP_POOL_SIZE: int = int(os.getenv("MULTIHOP_POOL_SIZE", "32"))
MULTIHOP_MAX_CHUNKS_PER_DOC: int = int(os.getenv("MULTIHOP_MAX_CHUNKS_PER_DOC", "1"))
MULTIHOP_MIN_INTENT_MATCHES: int = int(os.getenv("MULTIHOP_MIN_INTENT_MATCHES", "1"))
MULTIHOP_TOP_K: int = int(os.getenv("MULTIHOP_TOP_K", "6"))
MULTIHOP_KEYWORD_BOOST: float = float(os.getenv("MULTIHOP_KEYWORD_BOOST", "0.45"))

# ── Hybrid Retrieval ───────────────────────────────────────────────────
HYBRID_ENABLED: bool = os.getenv("HYBRID_ENABLED", "true").lower() in ("true", "1", "yes")
HYBRID_VECTOR_WEIGHT: float = float(os.getenv("HYBRID_VECTOR_WEIGHT", "0.7"))
HYBRID_KEYWORD_WEIGHT: float = float(os.getenv("HYBRID_KEYWORD_WEIGHT", "0.3"))

# ── Reranking ──────────────────────────────────────────────────────────
RERANK_ENABLED: bool = os.getenv("RERANK_ENABLED", "false").lower() in ("true", "1", "yes")
RERANK_PROVIDER: str = os.getenv("RERANK_PROVIDER", "local")  # "local" | "cohere"
COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
RERANK_MODEL: str = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANK_POOL_SIZE: int = int(os.getenv("RERANK_POOL_SIZE", "20"))

# ── Query Cache ────────────────────────────────────────────────────────
QUERY_CACHE_ENABLED: bool = os.getenv("QUERY_CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
QUERY_CACHE_TTL_SEC: int = int(os.getenv("QUERY_CACHE_TTL_SEC", "300"))
