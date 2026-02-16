"""Shared retrieval-time query intent detection utilities."""

from __future__ import annotations

import re

_MULTI_HOP_SIGNAL_RE = re.compile(
    r"\b(and|both|together|vs|versus|compared|compare|complement|"
    r"complementary|influence|affect|relationship)\b",
    re.IGNORECASE,
)


def is_multihop(question: str, min_words: int = 7) -> bool:
    """Return True when a question appears compositional/multi-hop."""
    normalized = re.sub(r"\s+", " ", question.strip())
    if len(normalized.split()) < min_words:
        return False
    return bool(_MULTI_HOP_SIGNAL_RE.search(normalized))
