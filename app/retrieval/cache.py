"""In-memory TTL cache for query responses.

Thread-safe, bounded by entry count, with automatic eviction of
expired entries on ``set()``.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time

logger = logging.getLogger(__name__)

MAX_ENTRIES = 2048  # hard cap to avoid unbounded memory growth


class QueryCache:
    """Thread-safe in-memory cache with TTL expiration."""

    def __init__(self, ttl_sec: int = 300) -> None:
        self._cache: dict[str, tuple[float, dict]] = {}
        self._ttl = ttl_sec
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    # ── stats ──────────────────────────────────────────────────────

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def size(self) -> int:
        return len(self._cache)

    # ── key generation ─────────────────────────────────────────────

    @staticmethod
    def _make_key(question: str, top_k: int, include_context: bool = False) -> str:
        normalised = question.strip().lower()
        raw = (
            f"{normalised}|top_k={top_k}"
            f"|include_context={1 if include_context else 0}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    # ── get / set / clear ──────────────────────────────────────────

    def get(
        self, question: str, top_k: int, include_context: bool = False,
    ) -> dict | None:
        """Return cached response dict, or ``None`` on miss / expiry."""
        key = self._make_key(question, top_k, include_context)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            ts, data = entry
            if time.time() - ts > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None
            self._hits += 1
            logger.debug("Cache HIT (key=%s…)", key[:12])
            return data

    def set(
        self, question: str, top_k: int, data: dict, include_context: bool = False,
    ) -> None:
        """Store a response in the cache."""
        key = self._make_key(question, top_k, include_context)
        with self._lock:
            # Lazy eviction of expired entries when cache grows large
            if len(self._cache) >= MAX_ENTRIES:
                self._evict_expired_locked()
            self._cache[key] = (time.time(), data)

    def clear(self) -> int:
        """Remove all entries. Returns the number removed."""
        with self._lock:
            n = len(self._cache)
            self._cache.clear()
            return n

    def stats(self) -> dict:
        """Return cache statistics."""
        return {
            "size": self.size,
            "hits": self._hits,
            "misses": self._misses,
            "ttl_sec": self._ttl,
        }

    # ── internal ───────────────────────────────────────────────────

    def _evict_expired_locked(self) -> int:
        """Remove expired entries (caller must hold self._lock)."""
        now = time.time()
        expired = [k for k, (ts, _) in self._cache.items() if now - ts > self._ttl]
        for k in expired:
            del self._cache[k]
        return len(expired)
