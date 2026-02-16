"""Hybrid retrieval: vector + BM25 keyword search with score fusion.

Implements BM25 Okapi from scratch (no external dependency) and provides
a merge function that combines vector similarity scores with keyword
relevance using a configurable weighted sum.
"""

from __future__ import annotations

import copy
import logging
import math
import re
import threading
from collections import Counter

from app.db.chroma import RetrievedChunk
from app.retrieval.detection import is_multihop

logger = logging.getLogger(__name__)


# ── Tokeniser ──────────────────────────────────────────────────────────

_STOPWORDS = frozenset(
    "a an the is are was were be been being have has had do does did will "
    "would shall should may might can could of in to for on with at by from "
    "as into through during before after above below between and but or nor "
    "not no so if then than too very just about also each how all both few "
    "more most other some such what which who whom this that these those am".split()
)


def _tokenize(text: str) -> list[str]:
    """Lowercase alphanumeric tokeniser with stop-word removal."""
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


_SUBQUERY_SPLIT_RE = re.compile(
    r"\b(?:and|vs|versus|compared to|as well as|together with)\b",
    re.IGNORECASE,
)

_RELATION_CUT_RE = re.compile(
    r"\b(together|both|affect|influence|impact|important|complementary|"
    r"complement|behavior|quality|planning|deployment)\b",
    re.IGNORECASE,
)

_BOILERPLATE_PATTERNS = (
    "table of contents",
    "was this page helpful",
    "feedback",
    "next steps",
    "related resources",
    "learn more",
)

_QUERY_NOISE_TERMS = {
    "amazon", "aws", "bedrock", "service", "services",
    "runtime", "foundation", "application", "applications",
}


def is_multi_hop_question(question: str) -> bool:
    """Heuristic multi-hop detection used to trigger query expansion."""
    return is_multihop(question)


def expand_query_variants(question: str) -> list[str]:
    """Return deduplicated query variants for retrieval.

    The first item is always the original question. For multi-hop prompts,
    we also add sub-queries split around conjunctions.
    """
    base = re.sub(r"\s+", " ", question.strip())
    if not base:
        return []

    variants = [base]
    if not is_multi_hop_question(base):
        return variants

    parts = [p.strip(" ,.;:!?") for p in _SUBQUERY_SPLIT_RE.split(base)]
    for part in parts:
        part = re.sub(
            r"^(how|why|what|where|when|which|do|does|can|is|are)\s+",
            "",
            part,
            flags=re.IGNORECASE,
        ).strip()
        part = re.sub(r"^(do|does|are|is|can)\s+", "", part, flags=re.IGNORECASE).strip()
        relation_hit = _RELATION_CUT_RE.search(part)
        if relation_hit and relation_hit.start() > 0:
            part = part[: relation_hit.start()].strip(" ,.;:!?")
        tokens = [t for t in _tokenize(part) if t not in _QUERY_NOISE_TERMS]
        if not tokens:
            continue
        if len(tokens) == 1 and len(tokens[0]) < 5:
            continue
        part = " ".join(tokens[:4])
        if "bedrock" in base.lower() and "bedrock" not in part.lower():
            part = f"{part} bedrock"
        variants.append(part)

    # Preserve order while deduplicating case-insensitively
    seen: set[str] = set()
    deduped: list[str] = []
    for item in variants:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _boilerplate_penalty(text: str) -> float:
    t = text.lower()
    return 0.12 if any(p in t for p in _BOILERPLATE_PATTERNS) else 0.0


# ── BM25 Okapi index ──────────────────────────────────────────────────


class BM25Index:
    """In-memory BM25 (Okapi) index over chunk texts.

    Thread-safe: all reads/writes are protected by a reentrant lock.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._lock = threading.RLock()

        # Index data
        self._corpus_tfs: list[Counter[str]] = []
        self._doc_lens: list[int] = []
        self._avg_dl: float = 0.0
        self._doc_freqs: Counter[str] = Counter()
        self._chunk_ids: list[str] = []
        self._chunk_map: dict[str, dict] = {}
        self._n_docs: int = 0
        self._ready = False

    # ── properties ─────────────────────────────────────────────────

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def size(self) -> int:
        return self._n_docs

    # ── build ──────────────────────────────────────────────────────

    def build_from_collection(self, collection) -> int:
        """(Re-)build BM25 index from all documents in a ChromaDB collection."""
        all_data = collection.get(include=["documents", "metadatas"])
        ids = all_data.get("ids", [])
        documents = all_data.get("documents", [])
        metadatas = all_data.get("metadatas", [])

        if not ids:
            return 0

        with self._lock:
            self._corpus_tfs = []
            self._doc_lens = []
            self._doc_freqs = Counter()
            self._chunk_ids = []
            self._chunk_map = {}

            for cid, doc, meta in zip(ids, documents, metadatas):
                tokens = _tokenize(doc)
                tf = Counter(tokens)
                self._corpus_tfs.append(tf)
                self._doc_lens.append(len(tokens))
                self._chunk_ids.append(cid)
                self._chunk_map[cid] = {
                    "chunk_id": cid,
                    "doc_id": meta.get("doc_id", ""),
                    "text": doc,
                    "source_path": meta.get("source_path", ""),
                    "content_type": meta.get("content_type", ""),
                }
                # Update document frequency (each unique term counted once)
                for term in tf:
                    self._doc_freqs[term] += 1

            self._n_docs = len(self._corpus_tfs)
            self._avg_dl = sum(self._doc_lens) / max(self._n_docs, 1)
            self._ready = True

        logger.info(
            "BM25 index built: %d documents, %d unique terms",
            self._n_docs,
            len(self._doc_freqs),
        )
        return self._n_docs

    # ── query ──────────────────────────────────────────────────────

    def query(self, question: str, top_k: int = 20) -> list[tuple[str, float]]:
        """Return top_k ``(chunk_id, bm25_score)`` pairs."""
        if not self._ready:
            return []

        query_tokens = _tokenize(question)
        if not query_tokens:
            return []

        with self._lock:
            scores: list[float] = [0.0] * self._n_docs
            for token in query_tokens:
                df = self._doc_freqs.get(token, 0)
                if df == 0:
                    continue
                idf = math.log((self._n_docs - df + 0.5) / (df + 0.5) + 1.0)
                for i, tf_map in enumerate(self._corpus_tfs):
                    tf = tf_map.get(token, 0)
                    if tf == 0:
                        continue
                    dl = self._doc_lens[i]
                    numerator = tf * (self._k1 + 1)
                    denominator = tf + self._k1 * (1 - self._b + self._b * dl / self._avg_dl)
                    scores[i] += idf * numerator / denominator

            scored = [
                (self._chunk_ids[i], scores[i])
                for i in range(self._n_docs)
                if scores[i] > 0
            ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def get_chunk_data(self, chunk_id: str) -> dict | None:
        """Return stored metadata for a chunk, or None."""
        return self._chunk_map.get(chunk_id)


# ── Module-level singleton ─────────────────────────────────────────────

_bm25_index = BM25Index()


def get_bm25_index() -> BM25Index:
    """Return the global BM25 index singleton."""
    return _bm25_index


def rebuild_bm25_index(collection) -> int:
    """Rebuild the global BM25 index from the given ChromaDB collection."""
    return _bm25_index.build_from_collection(collection)


# ── Hybrid merge (weighted fusion) ─────────────────────────────────────


def fuse_vector_runs(
    question: str,
    runs: list[list[RetrievedChunk]],
    top_k: int,
    max_per_doc: int = 2,
) -> list[RetrievedChunk]:
    """Fuse multiple vector retrieval runs (query expansion) via RRF + lexical match.

    This improves multi-hop retrieval by rewarding chunks that surface across
    multiple sub-queries and by preferring chunks that overlap with query terms.
    """
    if not runs:
        return []
    if len(runs) == 1:
        return runs[0][:top_k]

    query_terms = {t for t in _tokenize(question) if t not in _QUERY_NOISE_TERMS}
    sub_queries = expand_query_variants(question)[1:]
    sub_term_sets = [
        {t for t in _tokenize(q) if t not in _QUERY_NOISE_TERMS}
        for q in sub_queries
    ]
    sub_term_sets = [s for s in sub_term_sets if s]

    fused: dict[str, dict] = {}
    rrf_k = 60.0
    run_count = len(runs)

    for run in runs:
        for rank, chunk in enumerate(run, 1):
            rec = fused.get(chunk.chunk_id)
            if rec is None:
                rec = {
                    "chunk": copy.copy(chunk),
                    "rrf": 0.0,
                    "best_score": chunk.score,
                    "hits": 0,
                }
                fused[chunk.chunk_id] = rec
            rec["rrf"] += 1.0 / (rrf_k + rank)
            rec["best_score"] = max(rec["best_score"], chunk.score)
            rec["hits"] += 1

    if not fused:
        return []

    max_rrf = max(v["rrf"] for v in fused.values()) or 1.0
    items: list[dict] = []

    for rec in fused.values():
        chunk: RetrievedChunk = rec["chunk"]
        chunk_terms = set(_tokenize(chunk.text))
        overlap = (
            len(query_terms & chunk_terms) / len(query_terms)
            if query_terms else 0.0
        )
        sub_overlaps: list[float] = []
        sub_matches: list[bool] = []
        for terms in sub_term_sets:
            hit_count = len(terms & chunk_terms)
            min_hits = 1 if len(terms) <= 2 else 2
            sub_matches.append(hit_count >= min_hits)
            sub_overlaps.append(hit_count / len(terms))
        matched = sum(1 for ok in sub_matches if ok)
        coverage = (matched / len(sub_term_sets)) if sub_term_sets else 0.0

        # Multi-hop favors lexical coverage more than raw vector similarity.
        if sub_term_sets:
            score = (
                0.35 * rec["best_score"]
                + 0.24 * (rec["rrf"] / max_rrf)
                + 0.23 * overlap
                + 0.15 * coverage
                + 0.03 * (rec["hits"] / run_count)
                - _boilerplate_penalty(chunk.text)
            )
        else:
            score = (
                0.52 * rec["best_score"]
                + 0.23 * (rec["rrf"] / max_rrf)
                + 0.17 * overlap
                + 0.08 * (rec["hits"] / run_count)
                - _boilerplate_penalty(chunk.text)
            )
        chunk.vector_score = rec["best_score"]
        chunk.score = score
        items.append({
            "score": score,
            "chunk": chunk,
            "sub_overlaps": sub_overlaps,
            "sub_matches": sub_matches,
        })

    items.sort(key=lambda x: x["score"], reverse=True)

    results: list[RetrievedChunk] = []
    doc_counts: dict[str, int] = {}

    # For multi-hop, seed one strong chunk per sub-query intent when possible.
    if sub_term_sets:
        used: set[str] = set()
        for i in range(len(sub_term_sets)):
            for row in items:
                chunk: RetrievedChunk = row["chunk"]
                if chunk.chunk_id in used:
                    continue
                if i >= len(row["sub_matches"]) or not row["sub_matches"][i]:
                    continue
                count = doc_counts.get(chunk.doc_id, 0)
                if count >= max_per_doc:
                    continue
                results.append(chunk)
                used.add(chunk.chunk_id)
                doc_counts[chunk.doc_id] = count + 1
                break
        for prefer_matched in (True, False):
            for row in items:
                if len(results) >= top_k:
                    break
                chunk = row["chunk"]
                if chunk.chunk_id in used:
                    continue
                has_match = any(row["sub_matches"])
                if prefer_matched and not has_match:
                    continue
                if not prefer_matched and has_match:
                    continue
                count = doc_counts.get(chunk.doc_id, 0)
                if count >= max_per_doc:
                    continue
                results.append(chunk)
                used.add(chunk.chunk_id)
                doc_counts[chunk.doc_id] = count + 1
    else:
        for row in items:
            chunk = row["chunk"]
            count = doc_counts.get(chunk.doc_id, 0)
            if count >= max_per_doc:
                continue
            results.append(chunk)
            doc_counts[chunk.doc_id] = count + 1
            if len(results) >= top_k:
                break

    return results


def fuse_bm25_runs(
    runs: list[list[tuple[str, float]]],
    top_k: int,
) -> list[tuple[str, float]]:
    """Fuse BM25 ranked lists from query variants using RRF + max-score mix."""
    if not runs:
        return []
    if len(runs) == 1:
        return runs[0][:top_k]

    acc: dict[str, dict[str, float]] = {}
    rrf_k = 60.0

    for run in runs:
        for rank, (cid, raw_score) in enumerate(run, 1):
            rec = acc.setdefault(cid, {"rrf": 0.0, "best": 0.0})
            rec["rrf"] += 1.0 / (rrf_k + rank)
            rec["best"] = max(rec["best"], raw_score)

    if not acc:
        return []

    max_rrf = max(v["rrf"] for v in acc.values()) or 1.0
    max_best = max(v["best"] for v in acc.values()) or 1.0

    scored = []
    for cid, rec in acc.items():
        fused_score = 0.55 * (rec["best"] / max_best) + 0.45 * (rec["rrf"] / max_rrf)
        scored.append((cid, fused_score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


def select_multi_hop_contexts(
    question: str,
    chunks: list[RetrievedChunk],
    top_k: int,
) -> list[RetrievedChunk]:
    """Select final contexts with per-subquery coverage guarantees."""
    if top_k <= 0 or not chunks:
        return []

    sub_queries = expand_query_variants(question)[1:]
    term_sets = [
        {t for t in _tokenize(q) if t not in _QUERY_NOISE_TERMS}
        for q in sub_queries
    ]
    term_sets = [s for s in term_sets if s]
    if not term_sets:
        return chunks[:top_k]

    ranked = sorted(chunks, key=lambda c: c.score, reverse=True)
    selected: list[RetrievedChunk] = []
    used: set[str] = set()

    # First pass: cover each subquery intent with at least one chunk.
    for terms in term_sets:
        min_hits = 1 if len(terms) <= 2 else 2
        for chunk in ranked:
            if chunk.chunk_id in used:
                continue
            hit_count = len(terms & set(_tokenize(chunk.text)))
            if hit_count < min_hits:
                continue
            selected.append(chunk)
            used.add(chunk.chunk_id)
            break

    # Fill remaining slots by score.
    for chunk in ranked:
        if len(selected) >= top_k:
            break
        if chunk.chunk_id in used:
            continue
        selected.append(chunk)
        used.add(chunk.chunk_id)

    return selected[:top_k]


def hybrid_merge(
    vector_results: list[RetrievedChunk],
    bm25_results: list[tuple[str, float]],
    bm25_index: BM25Index,
    top_k: int,
    max_per_doc: int = 2,
    vector_weight: float | None = None,
    keyword_weight: float | None = None,
) -> list[RetrievedChunk]:
    """Merge vector and BM25 results using weighted score fusion.

    • Vector scores are assumed to be in [0, 1] (cosine similarity).
    • BM25 scores are min-max normalised to [0, 1] within the result set.
    • The fused score is ``vector_weight * v + keyword_weight * k``.
    • A simple max-per-doc diversity filter is applied after merging.
    """
    from app.config import HYBRID_KEYWORD_WEIGHT, HYBRID_VECTOR_WEIGHT

    vw = vector_weight if vector_weight is not None else HYBRID_VECTOR_WEIGHT
    kw = keyword_weight if keyword_weight is not None else HYBRID_KEYWORD_WEIGHT

    if not bm25_results:
        return vector_results

    # ── normalise BM25 scores to [0, 1] ───────────────────────────
    max_bm25 = max(s for _, s in bm25_results)
    min_bm25 = min(s for _, s in bm25_results)
    rng = max_bm25 - min_bm25 if max_bm25 > min_bm25 else 1.0
    bm25_norm: dict[str, float] = {
        cid: (s - min_bm25) / rng for cid, s in bm25_results
    }

    # ── fuse scores ───────────────────────────────────────────────
    fused: dict[str, tuple[float, float, float, RetrievedChunk]] = {}
    #  key → (fused_score, vec_score, kw_score, chunk)

    for chunk in vector_results:
        vs = chunk.score
        ks = bm25_norm.get(chunk.chunk_id, 0.0)
        fs = vw * vs + kw * ks
        fused[chunk.chunk_id] = (fs, vs, ks, chunk)

    # BM25-only results (not found by vector search)
    for cid, _ in bm25_results:
        if cid in fused:
            continue
        data = bm25_index.get_chunk_data(cid)
        if not data:
            continue
        ks = bm25_norm.get(cid, 0.0)
        fs = kw * ks  # vector score is 0
        chunk = RetrievedChunk(
            chunk_id=data["chunk_id"],
            doc_id=data["doc_id"],
            text=data["text"],
            score=fs,
            source_path=data["source_path"],
            content_type=data["content_type"],
        )
        fused[cid] = (fs, 0.0, ks, chunk)

    # ── sort + diversity filter ───────────────────────────────────
    sorted_items = sorted(fused.values(), key=lambda x: x[0], reverse=True)

    doc_counts: dict[str, int] = {}
    results: list[RetrievedChunk] = []
    for fs, vs, ks, chunk in sorted_items:
        count = doc_counts.get(chunk.doc_id, 0)
        if count >= max_per_doc:
            continue
        chunk.score = fs
        chunk.vector_score = vs
        chunk.keyword_score = ks
        results.append(chunk)
        doc_counts[chunk.doc_id] = count + 1
        if len(results) >= top_k:
            break

    return results
