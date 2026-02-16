"""Multi-hop intent extraction and intent-aware retrieval.

For compositional questions like "How are X and Y complementary?":
1. Extract structured intents (one per topic)
2. Run dense + BM25 retrieval per intent
3. Fuse into a deduped candidate pool (default 32)
4. Rerank with cross-encoder (if enabled)
5. Select top-k with ≥1 chunk per intent guarantee
"""

from __future__ import annotations

import copy
import logging
import math
import re
from dataclasses import dataclass

from app.db.chroma import RetrievedChunk
from app.retrieval.detection import is_multihop as detect_multihop

logger = logging.getLogger(__name__)


# ── Intent extraction helpers ──────────────────────────────────────────

_CONJUNCTION_RE = re.compile(
    r"\b(?:and|vs|versus|compared to|as well as|together with)\b",
    re.IGNORECASE,
)

_QUESTION_PREFIX_RE = re.compile(
    r"^(?:how|why|what|where|when|which|do|does|can|is|are)"
    r"(?:\s+(?:do|does|are|is|can|will|would|should))?\s+",
    re.IGNORECASE,
)

_RELATIONAL_TAIL_RE = re.compile(
    r"\s+\b(?:together|both|important|complementary|complement|influence|"
    r"affect|impact)\b.*$",
    re.IGNORECASE,
)

_NOISE = frozenset(
    "a an the is are was were be been being have has had do does did will "
    "would shall should may might can could of in to for on with at by from "
    "as into through during before after above below between amazon aws "
    "service services application applications".split()
)


@dataclass
class Intent:
    """A single retrieval intent from a multi-hop question."""

    query: str                  # Sub-query string for dense / BM25 retrieval
    key_terms: frozenset[str]   # Key noun-phrase terms for coverage matching


def _terms(text: str) -> frozenset[str]:
    """Extract meaningful terms (lowercase, noise-filtered)."""
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return frozenset(t for t in tokens if len(t) > 2 and t not in _NOISE)


# ── Public API: intent extraction ──────────────────────────────────────

def is_multihop(question: str) -> bool:
    """Quick heuristic: is this a compositional multi-hop question?"""
    return detect_multihop(question)


def extract_intents(question: str) -> list[Intent]:
    """Split a compositional question into 2-3 structured intents.

    Returns an empty list when the question is *not* multi-hop.
    Each intent carries a focused sub-query and key terms for matching.
    """
    norm = re.sub(r"\s+", " ", question.strip())
    if not is_multihop(norm):
        return []

    parts = [p.strip(" ,.;:!?") for p in _CONJUNCTION_RE.split(norm)]
    parts = [p for p in parts if len(p.split()) >= 2]
    if len(parts) < 2:
        return []

    intents: list[Intent] = []
    for part in parts:
        # Strip question prefix: "How do model access" → "model access"
        cleaned = _QUESTION_PREFIX_RE.sub("", part).strip()
        # Strip relational tail: "regions together affect …" → "regions"
        cleaned = _RELATIONAL_TAIL_RE.sub("", cleaned).strip(" ,.;:!?")
        if len(cleaned) < 3:
            continue
        key = _terms(cleaned)
        if not key:
            continue
        # Build focused sub-query with domain anchor
        q = cleaned
        if "bedrock" not in q.lower() and "bedrock" in norm.lower():
            q += " Bedrock"
        intents.append(Intent(query=q, key_terms=key))

    return intents if len(intents) >= 2 else []


# ── Coverage helpers ───────────────────────────────────────────────────

def chunk_covers_intent(chunk: RetrievedChunk, intent: Intent) -> bool:
    """True when the chunk text contains enough of the intent's key terms.

    Uses 5-char prefix matching to handle morphological variants
    (e.g. retrieval/retrieved, configuration/configure, endpoints/endpoint).
    """
    return _intent_match_count(chunk, intent) >= _intent_threshold(intent)


def _intent_threshold(intent: Intent) -> int:
    size = len(intent.key_terms)
    if size <= 1:
        return 1
    if size == 2:
        return 2
    # For longer intents, require stronger lexical support.
    return max(2, math.ceil(size * 0.6))


def _intent_match_count(chunk: RetrievedChunk, intent: Intent) -> int:
    """Count matched intent terms inside a chunk (with prefix fallback)."""
    chunk_terms = _terms(chunk.text)
    hits = 0
    for key_term in intent.key_terms:
        if key_term in chunk_terms:
            hits += 1
            continue
        # Prefix match for morphological variants
        prefix_len = min(len(key_term), 5)
        if prefix_len >= 4:
            prefix = key_term[:prefix_len]
            if any(ct.startswith(prefix) for ct in chunk_terms):
                hits += 1
    return hits


# ── Public API: intent-aware retrieval pipeline ────────────────────────

def retrieve_multihop(
    question: str,
    intents: list[Intent],
    pool_size: int = 32,
    top_k: int = 4,
) -> tuple[list[RetrievedChunk], list[bool]]:
    """Per-intent dense + BM25 → fuse → rerank → coverage-select.

    Returns ``(selected_chunks, intent_covered)`` where
    ``intent_covered[i]`` is True when at least one selected chunk
    matches intent *i*.
    """
    from app.config import (
        HYBRID_ENABLED, MULTIHOP_KEYWORD_BOOST,
        MULTIHOP_MAX_CHUNKS_PER_DOC,
        MULTIHOP_MIN_INTENT_MATCHES, RERANK_ENABLED,
    )
    from app.ingest.embedder import embed_texts
    from app.db.chroma import query_chunks
    from app.retrieval.hybrid import get_bm25_index
    from app.retrieval.reranker import rerank_chunks

    per_k = max(pool_size // len(intents), 8)
    best: dict[str, RetrievedChunk] = {}

    # Run retrieval for original question + each intent sub-query
    queries = [question] + [intent.query for intent in intents]

    for q_text in queries:
        emb = embed_texts([q_text])[0]
        dense = query_chunks(emb, top_k=per_k, question=q_text)
        for c in dense:
            prev = best.get(c.chunk_id)
            if prev is None or c.score > prev.score:
                best[c.chunk_id] = copy.copy(c)

        if HYBRID_ENABLED:
            bm25_idx = get_bm25_index()
            if bm25_idx.ready:
                bm25_hits = bm25_idx.query(q_text, top_k=per_k)
                if bm25_hits:
                    mx = max(s for _, s in bm25_hits) or 1.0
                    for cid, raw in bm25_hits:
                        if cid in best:
                            continue
                        data = bm25_idx.get_chunk_data(cid)
                        if not data:
                            continue
                        best[cid] = RetrievedChunk(
                            chunk_id=data["chunk_id"],
                            doc_id=data["doc_id"],
                            text=data["text"],
                            score=MULTIHOP_KEYWORD_BOOST * (raw / mx),
                            source_path=data["source_path"],
                            content_type=data["content_type"],
                        )

    pool = sorted(best.values(), key=lambda c: c.score, reverse=True)[:pool_size]
    if not pool:
        return [], [False] * len(intents)

    # Cross-encoder rerank over the full pool
    if RERANK_ENABLED and len(pool) > 1:
        pool = rerank_chunks(question, pool, top_k=pool_size)

    # Drop chunks that do not support any intent. This usually lifts context
    # precision for compositional questions by filtering generic filler text.
    intent_hit_count: dict[str, int] = {
        chunk.chunk_id: _intent_hit_count(chunk, intents)
        for chunk in pool
    }
    filtered_pool = [
        chunk
        for chunk in pool
        if intent_hit_count.get(chunk.chunk_id, 0) >= MULTIHOP_MIN_INTENT_MATCHES
    ]
    if filtered_pool:
        pool = filtered_pool

    # Prefer chunks that cover multiple intents, then keep original order.
    order_index = {chunk.chunk_id: idx for idx, chunk in enumerate(pool)}
    pool = sorted(
        pool,
        key=lambda chunk: (
            -intent_hit_count.get(chunk.chunk_id, 0),
            order_index.get(chunk.chunk_id, 0),
        ),
    )

    return _select_with_coverage(
        pool,
        intents,
        top_k=top_k,
        max_per_doc=MULTIHOP_MAX_CHUNKS_PER_DOC,
    )


def _intent_hit_count(chunk: RetrievedChunk, intents: list[Intent]) -> int:
    """Count how many intents a chunk covers."""
    return sum(1 for intent in intents if chunk_covers_intent(chunk, intent))


def _select_with_coverage(
    pool: list[RetrievedChunk],
    intents: list[Intent],
    top_k: int,
    max_per_doc: int = 1,
) -> tuple[list[RetrievedChunk], list[bool]]:
    """Pick *top_k* chunks, guaranteeing ≥1 per intent when possible."""
    selected: list[RetrievedChunk] = []
    used: set[str] = set()
    doc_counts: dict[str, int] = {}
    satisfied = [False] * len(intents)

    # Pass 1: seed one chunk per unsatisfied intent
    for i, intent in enumerate(intents):
        if satisfied[i]:
            continue
        best_chunk: RetrievedChunk | None = None
        best_rank = (-1, -1.0, -1.0)  # (match_count, match_ratio, similarity_score)
        for chunk in pool:
            if chunk.chunk_id in used:
                continue
            count = doc_counts.get(chunk.doc_id, 0)
            if count >= max_per_doc:
                continue
            match_count = _intent_match_count(chunk, intent)
            if match_count < _intent_threshold(intent):
                continue
            match_ratio = match_count / max(len(intent.key_terms), 1)
            rank = (match_count, match_ratio, chunk.score)
            if rank > best_rank:
                best_rank = rank
                best_chunk = chunk
        if best_chunk is not None:
            selected.append(best_chunk)
            used.add(best_chunk.chunk_id)
            doc_counts[best_chunk.doc_id] = doc_counts.get(best_chunk.doc_id, 0) + 1
            satisfied[i] = True
            # Mark any other intents this chunk also covers
            for j, other_intent in enumerate(intents):
                if not satisfied[j] and chunk_covers_intent(best_chunk, other_intent):
                    satisfied[j] = True

    # Pass 2: fill remaining slots by score
    for chunk in pool:
        if len(selected) >= top_k:
            break
        if chunk.chunk_id in used:
            continue
        count = doc_counts.get(chunk.doc_id, 0)
        if count >= max_per_doc:
            continue
        selected.append(chunk)
        used.add(chunk.chunk_id)
        doc_counts[chunk.doc_id] = count + 1

    return selected[:top_k], satisfied
