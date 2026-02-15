"""Reranking module: local cross-encoder or optional Cohere API.

The reranker **reorders** retrieved chunks by relevance to the query
without changing the original similarity scores (which are still used
by the confidence gate downstream).

Feature-flagged via:
  RERANK_ENABLED=true/false
  RERANK_PROVIDER=local|cohere
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.config import COHERE_API_KEY, RERANK_MODEL, RERANK_PROVIDER
from app.db.chroma import RetrievedChunk

if TYPE_CHECKING:
    from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

# ── Local cross-encoder singleton ──────────────────────────────────────

_cross_encoder: CrossEncoder | None = None


def _get_cross_encoder() -> CrossEncoder:
    """Lazy-load the cross-encoder model (singleton)."""
    global _cross_encoder  # noqa: PLW0603
    if _cross_encoder is None:
        from sentence_transformers import CrossEncoder

        logger.info("Loading cross-encoder model: %s", RERANK_MODEL)
        _cross_encoder = CrossEncoder(RERANK_MODEL)
        logger.info("Cross-encoder model loaded.")
    return _cross_encoder


# ── Reranking implementations ──────────────────────────────────────────


def _rerank_local(
    question: str,
    chunks: list[RetrievedChunk],
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """Rerank using a local cross-encoder model.

    Reorders chunks by cross-encoder relevance score.  The original
    ``chunk.score`` (similarity) is preserved for downstream confidence
    gating; the cross-encoder score is **not** written back.
    """
    try:
        model = _get_cross_encoder()
        pairs = [(question, chunk.text) for chunk in chunks]
        scores = model.predict(pairs).tolist()

        # Sort by cross-encoder score (descending)
        scored = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
        result = [chunk for _, chunk in scored]
        return result[:top_k] if top_k else result
    except Exception as exc:
        logger.warning("Local reranking failed, returning original order: %s", exc)
        return chunks


def _rerank_cohere(
    question: str,
    chunks: list[RetrievedChunk],
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """Rerank using Cohere Rerank API (requires ``cohere`` package)."""
    if not COHERE_API_KEY:
        logger.warning("COHERE_API_KEY not set — skipping Cohere reranking")
        return chunks

    try:
        import cohere  # type: ignore

        client = cohere.Client(COHERE_API_KEY)
        docs = [chunk.text for chunk in chunks]
        response = client.rerank(
            query=question,
            documents=docs,
            top_n=top_k or len(chunks),
            model="rerank-english-v3.0",
        )

        reranked: list[RetrievedChunk] = []
        for result in response.results:
            reranked.append(chunks[result.index])
        return reranked
    except ImportError:
        logger.warning("cohere package not installed — skipping Cohere reranking")
        return chunks
    except Exception as exc:
        logger.warning("Cohere reranking failed, returning original order: %s", exc)
        return chunks


# ── Public API ─────────────────────────────────────────────────────────


def rerank_chunks(
    question: str,
    chunks: list[RetrievedChunk],
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """Rerank chunks using the configured provider.

    Falls back gracefully to the original ordering on any error.
    """
    if len(chunks) <= 1:
        return chunks

    if RERANK_PROVIDER == "cohere" and COHERE_API_KEY:
        return _rerank_cohere(question, chunks, top_k)
    return _rerank_local(question, chunks, top_k)
